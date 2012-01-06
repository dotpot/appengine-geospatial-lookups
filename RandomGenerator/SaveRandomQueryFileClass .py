import csv
import sys
import os
from GlobalPositionLib.GpPointClass import GpPoint
import RandomGeneratorClass
from Util.CsvFileIO import ReadCsvFileToItemDic
import Util.GeoConversion as GeoConversion
from Util import CsvFileIO
from Util import DataConversion
from GlobalPositionLib.GpSearchClass import GpSearch

__author__ = 'Brian'


class SaveRandomQueryFile:

    minDistanceMiles = 0.5
    maxDistanceMiles = 5.0
    maxSearchResults = 200
    MaxSearchCellCount = 10

    #Set default lattitude-longitude boundaries to Washington state boundaries
    minimumLattitude = 45.6
    maximumLattitude = 49.0
    minimumLongitude = -124.0
    maximumLongitude = -117.0

    # The following are set to random values
    CenterPoint = 0.0,0.0
    SearchDistanceMiles = 0.0
    SearchDistanceMeters = 0.0

    SearchResolution = 16
    SearchGpGridCells = []
    FinalSearchResolution = 0

    randomGenerator = RandomGeneratorClass.RandomDataGenerator()


    QueryDataDirectory = "TestVectorCsvData\\QueryData"
    QueryFilename = 'ProximityQueries'

    def SaveRandomProximityQueries(self,nRandomQueries):
        self.SetGeoBoundaries(self.minimumLattitude,self.maximumLattitude,self.minimumLongitude, self.maximumLongitude)

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

        csvFile.close()
        print "Saved",nRandomQueries,"Random Queries to File:",filePath

    def CreateLocationByProximityQuery(self):
        """Creates a query for locations within random miles from random center location

         Returns a dictionary of search query parameters
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
        return QueryParameterDic


    def SetGeoBoundaries(self,minLattitude,maxLattitude,minLongitude,maxLongitude):
        """ Set boundaries for random lat-lon generation"""
        self.randomGenerator.minimumLattitude = minLattitude
        self.randomGenerator.maximumLattitude = maxLattitude
        self.randomGenerator.minimumLongitude = minLongitude
        self.randomGenerator.maximumLongitude = maxLongitude

  