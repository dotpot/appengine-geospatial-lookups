""" Copyright (c) 2011 FriendzyShop, LLC. All rights reserved """

__author__ = 'Brian Sargent'

import os
import ast
import time

from GlobalPositionLib.GpMath import metersToMiles
from GlobalPositionLib.GpModel import IsGpCellXBoundedByGpCellY

from RandomGenerator import RandomQueryFileClass
from Util import CheckDataClass
from Util import CsvFileIO
from Util.QueryStatisticsClass import QueryStatistics


RUN_ON_APPENGINE = True
TEST_DESCRIPTION = 'NoCache'

if RUN_ON_APPENGINE:
    HOST_AND_PORT = "friendzyshop-dev.appspot.com:80"
else:
    HOST_AND_PORT = 'localhost:8080'

HTTP_PAGE = 'Admin'

TEST_REGION = 'WA'
#TEST_REGION = 'MT'
#TEST_REGION = 'MN'
#TEST_REGION = 'CO'
#TEST_REGION = 'MO'

ASYNCHRONOUS_QUERY = True
USE_MEM_CACHE = True

# Define path for query data directory and file
TEST_VECTOR_DATA_DIRECTORY =  "../TestVectorData"
QUERY_DATA_DIRECTORY = os.path.join(TEST_VECTOR_DATA_DIRECTORY,"QueryData")
QUERY_FILENAME = TEST_REGION +'_' + 'ProximityQueries.csv'

# Define directory and file for query stats
QUERY_STATS_DIRECTORY =  '../QueryData'
QUERY_STATS_FILENAME = TEST_REGION + '_' + 'QueryStats' + TEST_DESCRIPTION + '.csv'
QUERY_STATS_RAW_FILENAME = TEST_REGION + '_' + 'RawQueryStats' + TEST_DESCRIPTION + '.csv'
QUERY_RESULTS_FILENAME = TEST_REGION + '_' + 'QueryResults' + TEST_DESCRIPTION + '.csv'

# Define directory paths for reference model data
ModelDataDirectory = os.path.join(TEST_VECTOR_DATA_DIRECTORY,"ModelData")
LocationModelDataDirectory = TEST_REGION + '_' + 'Location'
VendorModelDataDirectory = TEST_REGION + '_' + 'Vendor'

####################################################
# Get Copy of Previously Uploaded Random Data Models
####################################################
directoryPath =os.path.join( ModelDataDirectory, LocationModelDataDirectory)
LocationAllEntityAttributeDic = CsvFileIO.ReadCsvFilesToDic(directoryPath,"KeyName")
locationCount = len(LocationAllEntityAttributeDic)
print "Location Count =",locationCount

# Instantiate class with methods for checking data. Can make this static later.
checkData = CheckDataClass.CheckData()

# Instantiate class for generating random queries
randomQuery = RandomQueryFileClass.RandomQueryFile()
randomQuery.HostAndPort = HOST_AND_PORT
randomQuery.QueryDataDirectory = QUERY_DATA_DIRECTORY
randomQuery.QueryFilename = QUERY_FILENAME
AllQueriesParametersDic = randomQuery.GetSavedQueryParametersDic()
queryCount = len(AllQueriesParametersDic)

# Instantiate class for aggregating performance statistics
queryStatistics = QueryStatistics()

# Run previously saved random queries
errorCount = 0
for queryNumber in range(0,queryCount):
    print '----' * 50
    print '----' * 50
    print 'Query Number:', queryNumber
    queryParametersDic = AllQueriesParametersDic[queryNumber]
    cellSearchListString = queryParametersDic['SearchGridCells']
    queryParametersDic['SearchGridCells']=ast.literal_eval(cellSearchListString)
    centerPtString =  queryParametersDic['CenterPt']
    queryParametersDic['CenterPt'] = ast.literal_eval(centerPtString)
    queryParametersDic['MaxDistanceMeters'] = float( queryParametersDic['MaxDistanceMeters'])
    queryParametersDic['MaxResults'] = int(queryParametersDic['MaxResults'])
    queryParametersDic['AsynchronousQuery'] = ASYNCHRONOUS_QUERY
    queryParametersDic['UseCache'] = USE_MEM_CACHE

    # Execute the query
    LocalStartTime = time.clock()
    locationEntityAttributeDic = randomQuery.RunSavedQuery(queryParametersDic)
    LocalQueryTime = time.clock() - LocalStartTime
    queryStats = randomQuery.queryStats

    queryStatistics.AccumulateResults(locationEntityAttributeDic)

    # Temp
    print "queryStats =",queryStats
    # Build a reference list of locations ordered by proximity and limited by the Maximum
    # distance in meters and the maximum search results
    maxDistanceMeters =  queryParametersDic['MaxDistanceMeters']
    centerPt  = queryParametersDic['CenterPt']

    checkData.GetLocationsOrderedByProximity(\
                queryParametersDic['MaxResults'],
                queryParametersDic['MaxDistanceMeters'],
                LocationAllEntityAttributeDic,\
                centerPt)
            
    maxDistanceMiles =  metersToMiles(maxDistanceMeters)
    numberExpected = len(checkData.EntityDistanceMetersSorted)
    numberReturnedFromQuery = len(locationEntityAttributeDic)
    queryStatistics.AccumulateStats(maxDistanceMiles,LocalQueryTime,queryStats)

    print 'CenterPt:', centerPt,\
                  'MaxDistance(miles):', maxDistanceMiles
    SearchGpGridCells = queryParametersDic['SearchGridCells']
    cellCount = len(SearchGpGridCells)
    print 'Search GpGridCell Count =',cellCount


    if not numberExpected:
        print "  No locations found within %f miles" % maxDistanceMiles
    if numberExpected != numberReturnedFromQuery:
        print '    Error: numExpected =',numberExpected, 'numFound =',numberReturnedFromQuery
        if numberReturnedFromQuery > numberExpected:
            errorCount +=  numberReturnedFromQuery - numberExpected
    foundCount = 0
    for keyDistance in checkData.EntityDistanceMetersSorted:
        keyName = keyDistance[0]
        distanceMiles = metersToMiles(keyDistance[1])
        entityAttributeDic = LocationAllEntityAttributeDic[keyName]
        latLon = entityAttributeDic['lattitude'],entityAttributeDic['longitude']
        if not keyName in locationEntityAttributeDic:
            errorCount += 1
            gpGridCell = keyDistance[2]
            boundedBy = 'None'
            for SearchGpGridCell in SearchGpGridCells:
                # Argument SearchGpGridCell[1] selects GpGridCellLongStr from tuple (priority, GpGridCellLongStr)
                if IsGpCellXBoundedByGpCellY(gpGridCell,SearchGpGridCell[1]):
                    boundedBy = SearchGpGridCell[1]
                    break

            print '   Error: keyName =',keyName,'At Distance(miles) =',distanceMiles,\
                ',LatLon =',latLon, 'Not found','GpGridCell =',gpGridCell,'BoundedBy',boundedBy
        else:
            print '   Found: keyName =',keyName, 'At Distance(miles) =',distanceMiles,',LatLon =',latLon
            foundCount += 1
    print "Total Found Count =",foundCount
    print 'Round Trip Query Time:',LocalQueryTime
    print queryStats

print '---' * 50
print 'Total Error Count =',errorCount
print '---' * 50
print "Statistics for all queries:"

queryStatistics.PrintAllStatsData()
queryStatistics.WriteAllStatsToCsvFile(QUERY_STATS_DIRECTORY, QUERY_STATS_FILENAME)
queryStatistics.WriteAllRawStatsToCsvFile(QUERY_STATS_DIRECTORY, QUERY_STATS_RAW_FILENAME)
#queryStatistics.WriteAllResultsToCsvFile(QUERY_STATS_DIRECTORY, QUERY_RESULTS_FILENAME)