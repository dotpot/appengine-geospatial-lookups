import logging
import math
import Util.DataConversion as DataConversion
import HttpInterface.HttpInterface as HttpInterface
from GlobalPositionLib.GpPointClass import GpPoint
from GlobalPositionLib.GpGridPointClass import GpGridPoint

__author__ = 'Brian'

class CheckData:

    RADIUS_OF_EARTH_METERS = 6378135
    MILES_PER_METER =  0.000621371192
    EntityDistanceMetersSorted = []
    EntityCount = 0
    EntitiesWithinDistance = 0

    def CompareAttributes(self,ReferenceAttributeDic, AttributeDic):
        """ Compare two dictionaries of attributeName:attributeValue

        Return True if all attributes in ReferenceAttributeDic are
        present in AttributeDic and match in value"""
        for attribute in ReferenceAttributeDic:
            if not attribute in ReferenceAttributeDic:
                logging.error("Attribute %s not found in reference attributes", attribute)
                return False
            else:
                if ReferenceAttributeDic[attribute] != AttributeDic[attribute] :
                    logging.error("Values of attribute %s are not equal: reference = %s, checked = %s",
                                  attribute,ReferenceAttributeDic[attribute],AttributeDic[attribute])
                    return False
            return True


    def CheckDataStoreKind(self,HostAndPort,Page, modelKind ,modelGroup, kindAllEntityAttributeDic):
        """ Download and Check All Entities of modelKind in a modelGroup.

        KindAllEntityAttributeDic provides reference data to check against"""
        # Create a query
        ACTION = 'Query'
        parameterDic = {}
        parameterDic['SearchType'] = 'ModelKindAll'
        parameterDic['ModelKind'] = modelKind
        parameterDic['ModelGroup'] = modelGroup
        QueryJSON = DataConversion.dict_to_json(parameterDic)
        print "JSON Query for %s:" % modelKind
        print QueryJSON

        # Send Query and Get Results
        res = HttpInterface.get_data(HostAndPort,Page,ACTION,QueryJSON)
        if res is None:
            print "Query for %s Model returned no results" % modelKind
            return 1

        # First check number of results from query
        ResultsDic = {}
        errorCount = 0
        returnedChangeSetDic = DataConversion.json_to_dict(res)
        print 'CheckDataStoreKind()- returnedChangeSetDic from Query for Model %s:' % modelKind
        print returnedChangeSetDic
        returnedClassEntityDic = returnedChangeSetDic['c']
        returnedEntityAttributeDic = returnedClassEntityDic[modelKind]

        numberEntitiesFound = len(returnedEntityAttributeDic)
        numberEntitiesExpected = len(kindAllEntityAttributeDic)
        ResultsDic['numberEntitiesFound'] = numberEntitiesFound
        ResultsDic['numberEntitiesExpected'] = numberEntitiesExpected
        if numberEntitiesFound < numberEntitiesExpected:
            print "Failed to retrieve all entities, number sent = %d, number received = %d" % \
                  (numberEntitiesExpected, numberEntitiesFound)

        # Compare each uploaded entity against entities downloaded

        for modelKeyName in kindAllEntityAttributeDic:
            if not modelKeyName in returnedEntityAttributeDic:
                print "modelKeyName %s not found in data downloaded" % modelKeyName
                errorCount += 1
            else:
                if not self.CompareAttributes(kindAllEntityAttributeDic[modelKeyName],
                              returnedEntityAttributeDic[modelKeyName]):
                    errorCount += 1

        return errorCount

    def distanceMeters(self,p1, p2):
      """Calculates the great circle distance between two points (law of cosines).

      Args:
        p1: A tuple of (lattitude,longitude) indicating the first point.
        p2: A tuple of (lattitude,longitude) indicating the second point.

      Returns:
        The 2D great-circle distance between the two given points, in meters.
      """
      p1lat, p1lon = math.radians(p1[0]), math.radians(p1[1])
      p2lat, p2lon = math.radians(p2[0]), math.radians(p2[1])
      return self.RADIUS_OF_EARTH_METERS * math.acos(math.sin(p1lat) * math.sin(p2lat) +
          math.cos(p1lat) * math.cos(p2lat) * math.cos(p2lon - p1lon))

    def GetLocationsOrderedByProximity(self,maxSearchResults, maxDistanceMeters,
               LocationAllEntityAttributeDic, centerPt):
        """ Make a list of (EntityKeyName,DistanceMeters,GeoCell) sorted by DistanceMeters

            Limit the number of list entries to maxSearchResult and limit entries by
            MaxDistanceMeters. EntityKeyName and location (lattitude,longitude) are
            extracted from the supplied LocationAllEntityAttributeDic.
        """
        entityDistanceMeters = []
        for entityKeyName in LocationAllEntityAttributeDic:
            attributeDic = LocationAllEntityAttributeDic[entityKeyName]
            longitudeStr =  attributeDic['longitude']
            lattitudeStr = attributeDic['lattitude']
            locationPt = float(lattitudeStr) ,float(longitudeStr)
            locationGpPoint =GpPoint(locationPt[0],locationPt[1])
            locationGpGridPoint = GpGridPoint()
            locationGpGridPoint.InitFromGpPoint(locationGpPoint,16)
            locationGpCell = locationGpGridPoint.ToLongString()
            distanceInMeters = self.distanceMeters(locationPt, centerPt)
            if distanceInMeters <= maxDistanceMeters:
                tup = entityKeyName,distanceInMeters,locationGpCell
                entityDistanceMeters.append(tup)
        self.EntityDistanceMetersSorted = sorted(entityDistanceMeters,key=self.GetDistance)

        if len(self.EntityDistanceMetersSorted) > maxSearchResults:
            self.EntityDistanceMetersSorted = self.EntityDistanceMetersSorted[0: maxSearchResults]
        


    def GetDistance(self,entityDistance):
        """ Get distance from an entity-distance tuple.

        Used to provide a key for sorting"""
        return entityDistance[1]