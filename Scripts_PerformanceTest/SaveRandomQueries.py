""" Copyright (c) 2011 FriendzyShop, LLC. All rights reserved """

from RandomGenerator.RandomQueryFileClass  import RandomQueryFile
from TestVectorData.LocationTestDataClass import LocationTestData
import os

__author__ = 'Brian Sargent'

#Define parameters for random query creation and save
MIN_DISTANCE_MILES = 0.5
MAX_DISTANCE_MILES = 10.0
NUMBER_RANDOM_QUERIES = 20

QUERY_DATA_DIRECTORY = os.path.join("TestVectorData","QueryData")

#TEST_REGION = 'WA'
#TEST_REGION = 'MT'
#TEST_REGION = 'MN'
TEST_REGION = 'CO'
#TEST_REGION = 'MO'

QUERY_DATA_FILENAME = TEST_REGION + "_ProximityQueries.csv"

locationTestData = LocationTestData()
locationTestData.SetRegion(TEST_REGION)

randomQueryFile = RandomQueryFile()
randomQueryFile.minDistanceMiles = MIN_DISTANCE_MILES
randomQueryFile.maxDistanceMiles = MAX_DISTANCE_MILES
randomQueryFile.SetRegionBoundary(locationTestData.GetRegionGpBox())
randomQueryFile.QueryDataDirectory = QUERY_DATA_DIRECTORY
randomQueryFile.QueryFilename = QUERY_DATA_FILENAME

######################################
# Create and Save Random Queries
######################################
randomQueryFile.SaveRandomProximityQueries(NUMBER_RANDOM_QUERIES)


