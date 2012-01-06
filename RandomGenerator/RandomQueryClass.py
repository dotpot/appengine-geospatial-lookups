from GlobalPositionLib.GpPointClass import GpPoint
import HttpInterface.HttpInterface as HttpInterface
import RandomGeneratorClass
import GeoLib.GeoSearch as GeoSearch
import Util.GeoConversion as GeoConversion
import Util.DataConversion as DataConversion
from GlobalPositionLib.GpSearchClass import GpSearch

__author__ = 'Brian'


class RandomQuery:

    minDistanceMiles = 0.5
    maxDistanceMiles = 5.0
    maxSearchResults = 200
    MaxSearchCellCount = 10
    HostAndPort = 'localhost:8080'
    HttpPage = 'Admin'
    HttpAction = 'Query'
    # The following are set to random values
    CenterPoint = 0.0,0.0
    SearchDistanceMiles = 0.0
    SearchDistanceMeters = 0.0
    SearchResolution = 16
    SearchGpGridCells = []
    FinalSearchResolution = 0

    randomGenerator = RandomGeneratorClass.RandomDataGenerator()
    geoSearch = GeoSearch.GeoSearchClass(0.0,0.0,10.0)

    def RunLocationByProximityQuery(self):
        """Runs a query for locations within random miles from random center location

         Returns a location Entity-Attribute dictionary
         """
        self.CenterPoint = self.randomGenerator.CreateRandomLattitudeLongitude()
        self.SearchDistanceMiles = self.randomGenerator.CreateRandomNumber(self.minDistanceMiles,self.maxDistanceMiles)
        self.SearchDistanceMeters =  GeoConversion.ConvertMilesToMeters(self.SearchDistanceMiles)
        QueryParameterDic = {}
        QueryParameterDic['SearchType'] ='LocationByProximity'
        QueryParameterDic['MaxResults'] = self.maxSearchResults
        QueryParameterDic['MaxDistanceMeters'] = GeoConversion.ConvertMilesToMeters(self.SearchDistanceMiles)
        QueryParameterDic['CenterPt'] = self.CenterPoint
        QueryParameterDic['HasShopsOnly'] = 'True'
        QueryParameterDic['FilterByTrueDistance'] = 'True'
        # Get a list of GpGridCells to search
        gpSearch = GpSearch()
        gpSearch.MaxSearchCellCount = self.MaxSearchCellCount
        centerGpPoint = GpPoint(self.CenterPoint[0],self.CenterPoint[1])
        gpSearch.ComputeSearchListForMetersProximity(centerGpPoint,self.SearchDistanceMeters)
        self.FinalSearchResolution = gpSearch.FinalSearchResolution
        self.SearchGpGridCells = gpSearch.SearchCellList
       
        QueryParameterDic['SearchGridCells'] = self.SearchGpGridCells

        # Convert Query to JSON
        QueryJSON = DataConversion.dict_to_json(QueryParameterDic)
        print 'QueryJSON ='
        print QueryJSON
        resultsJSON = HttpInterface.get_data(self.HostAndPort,self.HttpPage,self.HttpAction,QueryJSON)
        if resultsJSON == "":
            # No entities found in search
            locationEntityAttributeDic = {}
        elif resultsJSON.startswith('Not found error'):
            locationEntityAttributeDic = {}
        else:
            results = DataConversion.json_to_dict(resultsJSON)
            locationClassEntityDic = results['c']
            locationEntityAttributeDic = locationClassEntityDic['Location']
        return locationEntityAttributeDic

