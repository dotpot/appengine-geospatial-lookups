""" Copyright (c) 2011 FriendzyShop, LLC. All rights reserved """

__author__ = 'Brian Sargent'

import os
import ast
import time
import logging

from GlobalPositionLib.GpMath import metersToMiles
from GlobalPositionLib.GpModel import IsGpCellXBoundedByGpCellY

from RandomGenerator import RandomQueryFileClass
from Util import CheckDataClass
from Util import CsvFileIO
from Util.QueryStatisticsClass import QueryStatistics
from Util import DataConversion
from Util.TestRunResultsClass import TestRunResults


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
TEST_VECTOR_DATA_DIRECTORY =  'TestVectorData'
QUERY_DATA_DIRECTORY = os.path.join(TEST_VECTOR_DATA_DIRECTORY,"QueryData")
QUERY_FILENAME = TEST_REGION +'_' + 'ProximityQueries.csv'

# Define directory and file for query stats
QUERY_STATS_DIRECTORY =  'QueryStatsData'
QUERY_STATS_FILENAME = TEST_REGION + '_' + 'QueryStats' + TEST_DESCRIPTION + '.csv'
QUERY_STATS_RAW_FILENAME = TEST_REGION + '_' + 'RawQueryStats' + TEST_DESCRIPTION + '.csv'
QUERY_RESULTS_FILENAME = TEST_REGION + '_' + 'QueryResults' + TEST_DESCRIPTION + '.csv'

# Define directory paths for reference model data
ModelDataDirectory = os.path.join(TEST_VECTOR_DATA_DIRECTORY,"ModelData")
LocationModelDataDirectory = TEST_REGION + '_' + 'Location'
VendorModelDataDirectory = TEST_REGION + '_' + 'Vendor'

# Get a logger
logger = logging.getLogger(name = 'Main')
logger.setLevel(logging.INFO)
# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# add ch to logger
logger.addHandler(ch)
logger.removeHandler(ch)


####################################################
# Get Copy of Previously Uploaded Random Data Models
####################################################
directoryPath =os.path.join( ModelDataDirectory, LocationModelDataDirectory)
LocationAllEntityAttributeDic = CsvFileIO.ReadCsvFilesToDic(directoryPath,"KeyName",logger)
locationCount = len(LocationAllEntityAttributeDic)

logger.info("Location Count = %d",locationCount)

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
# Instantiate class for aggregating test run results
testRunResults = TestRunResults()

# Run previously saved random queries
errorCount = 0
for queryNumber in range(0,queryCount):
    logger.info('---------------------------------------------------------------------------------')
    logger.info('---------------------------------------------------------------------------------')
    logger.info('Query Number: %d', queryNumber)
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
    LocalStartTime = time.time()
    locationEntityAttributeDic = randomQuery.RunSavedQuery(queryParametersDic)
    RoundTripQueryTime = time.time() - LocalStartTime
    queryStats = randomQuery.queryStats

    queryStatistics.AccumulateResults(locationEntityAttributeDic)
    testRunResults.AccumulateStats(queryNumber,queryParametersDic,RoundTripQueryTime,queryStats)

    # Temp
    # print "queryStats =",queryStats
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
    queryStatistics.AccumulateStats(maxDistanceMiles,RoundTripQueryTime,queryStats)

    logger.info('CenterPt: (%f,%f) , MaxDistance(miles): %f', centerPt[0],centerPt[1], maxDistanceMiles)
    SearchGpGridCells = queryParametersDic['SearchGridCells']
    cellCount = len(SearchGpGridCells)
    logger.info('Search GpGridCell Count = %d',cellCount)


    if not numberExpected:
        logger.error(" No locations found within %f miles", maxDistanceMiles)
    if numberExpected != numberReturnedFromQuery:
        logger.error(" Error: numExpected = %d, numFound = %d",numberExpected,numberReturnedFromQuery)
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

            logger.error('keyName = %s, At Distance(miles) %f, LatLon (%f,%f), GpGridCell not Found %s, BoundedBy %s',
                         keyName,distanceMiles,latLon[0],latLon[1],gpGridCell,boundedBy)

        else:
            logger.info('Found: keyName = %s, At Distance(miles) = %f ,LatLon = %s',keyName,distanceMiles,latLon)
                        
            foundCount += 1
    logger.info("Total Found Count = %d",foundCount)
    logger.info("Round Trip Query Time: %s",RoundTripQueryTime)
    logger.info('%s',queryStats)

logger.info('-------------------------------------------------------------')
logger.info('Total Error Count = %d',errorCount)
logger.info('-------------------------------------------------------------')
logger.info("Statistics for all queries:")

queryStatistics.LogAllStatsData()
queryStatistics.WriteAllStatsToCsvFile(QUERY_STATS_DIRECTORY, QUERY_STATS_FILENAME)
queryStatistics.WriteAllRawStatsToCsvFile(QUERY_STATS_DIRECTORY, QUERY_STATS_RAW_FILENAME)
#queryStatistics.WriteAllResultsToCsvFile(QUERY_STATS_DIRECTORY, QUERY_RESULTS_FILENAME)

#Print JSON dictionary of results for output to CouchDB
testRunResults.PrintRunResultsJSON()