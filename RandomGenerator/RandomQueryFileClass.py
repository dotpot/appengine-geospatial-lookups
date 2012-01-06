""" Copyright (c) 2011 FriendzyShop, LLC. All rights reserved """
__author__ = 'Brian Sargent'

import csv
import sys
import os
import random
import logging

from GlobalPositionLib.GpBoxClass import GpBox
from GlobalPositionLib.GpPointClass import GpPoint
from GlobalPositionLib import GpMath
from GlobalPositionLib.GpSearchClass import GpSearch

from HttpInterface import HttpInterface

from Util.CsvFileIO import ReadCsvFileToItemDic
from Util import CsvFileIO
from Util import DataConversion


class RandomQueryFile:

    HostAndPort = 'localhost:8080'
    HttpPage = 'Admin'
    HttpAction = 'Query'

    minDistanceMiles = 0.5
    maxDistanceMiles = 5.0
    maxSearchResults = 200
    MaxSearchCellCount = 10

    #Bounding box for the test region
    RegionGpBox = GpBox(0.0,0.0,0.0,0.0)

    # The following are set to random values
    CenterPoint = 0.0,0.0
    SearchDistanceMiles = 0.0
    SearchDistanceMeters = 0.0
    SearchResolution = 16
    SearchGpGridCells = []
    FinalSearchResolution = 0

    # Default directory and filename for query data files
    QueryDataDirectory = os.path.join("TestVectorCsvData","QueryData")
    QueryFilename = 'ProximityQueries.csv'

    logger = logging.getLogger(name = 'RandomQueryFile')
    logger.setLevel(logging.INFO)
    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    # add ch to logger
    logger.addHandler(ch)
  

    def SaveRandomProximityQueries(self,nRandomQueries):

        filePath = os.path.join(self.QueryDataDirectory,self.QueryFilename)
        try:
            csvFile = open(filePath,'w')
        except csv.Error as e:
            sys.exit('Failed to open file {} : {}'.format(filePath,e))

        parameterNames = []
        # Generate the first query
        queryDic = self.CreateLocationByProximityQuery()
        # Build a dictionary of query parameters
        columnDic = {}
        for parameter in queryDic:
            parameterNames.append(parameter)
            columnDic[parameter] = parameter
        # Open a Dictionary to csv file writer
        writer = csv.DictWriter(csvFile,parameterNames)
        # Write a row of headings consisting of the parameter names
        writer.writerow(columnDic)
        # Generate and save the remainder of the queries
        for query in range(0,nRandomQueries):
            writer.writerow(queryDic)
            queryDic = self.CreateLocationByProximityQuery()
            print query,queryDic

        csvFile.close()
        print "Saved",nRandomQueries,"Random Queries to File:",filePath

    def CreateLocationByProximityQuery(self):
        """Creates a query for locations within random miles from random center location.

         Returns a dictionary of search query parameters.
         """
        self.CenterPoint = self.CreateRandomLattitudeLongitude()
        self.SearchDistanceMiles = random.uniform(self.minDistanceMiles,self.maxDistanceMiles)
        self.SearchDistanceMeters = GpMath.milesToMeters(self.SearchDistanceMiles)
        QueryParameterDic = {}
        QueryParameterDic['SearchType'] ='LocationByProximity'
        QueryParameterDic['MaxResults'] = self.maxSearchResults
        QueryParameterDic['MaxDistanceMeters'] = self.SearchDistanceMeters
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

        return QueryParameterDic

    def GetSavedQueryParametersDic(self):
        filePath = os.path.join(self.QueryDataDirectory,self.QueryFilename)
        QueryParametersDic = ReadCsvFileToItemDic(filePath)
        return QueryParametersDic

    def RunSavedQuery(self,QueryParameterDic):
        """Runs a query for locations within random miles from random center location

         Returns a location Entity-Attribute dictionary
         """

        # Convert Query to JSON
        QueryJSON = DataConversion.dict_to_json(QueryParameterDic)
        self.logger.info('QueryJSON =')
        self.logger.info('%s',QueryJSON)
        
        resultsJSON = HttpInterface.get_data(self.HostAndPort,self.HttpPage,self.HttpAction,QueryJSON)
        if resultsJSON == "":
            # No entities found in search
            locationEntityAttributeDic = {}
        elif resultsJSON.startswith('Not found error'):
            locationEntityAttributeDic = {}
        else:
            results = DataConversion.json_to_dict(resultsJSON)
            locationClassEntityDic = results['c']
            self.queryStats = results['stats']
            locationEntityAttributeDic = locationClassEntityDic['Location']
        return locationEntityAttributeDic


    def SetRegionBoundary(self,regionGpBox):
        """ Set boundaries for random lat-lon generation"""
        self.RegionGpBox = regionGpBox
        self.minimumLattitude = regionGpBox.SouthLattitude
        self.maximumLattitude = regionGpBox.NorthLattitude
        self.minimumLongitude = regionGpBox.WestLongitude
        self.maximumLongitude = regionGpBox.EastLongitude
       

    def ReadSavedQueriesFromCsvFile(self):
        """ Read the previously saved Query CSV File from Directory and Create Query Dictionary."""
        filePath = self.QueryDataDirectory +self.QueryFilename + ".csv"
        QueryDic = CsvFileIO.ReadCsvFileToItemDic(filePath)

        return QueryDic

    def CreateRandomLattitudeLongitude(self):
        """ Create a random lattitude, longitude tuple """
        lattitude = random.uniform(self.minimumLattitude, self.maximumLattitude)
        longitude = random.uniform(self.minimumLongitude, self.maximumLongitude)
        return lattitude,longitude

    def CreateRandomNumber(self,min,max):
        distance = random.uniform(min,max)
        return distance