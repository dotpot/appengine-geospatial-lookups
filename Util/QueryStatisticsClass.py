import os
import sys
import math
import csv
import logging

__author__ = 'Brian'



class QueryStatistics:

    AllStatsData = []
    StatsData = {}
    AllStatsDataRaw = []
    StatsDataRaw = {}
    AllResultsData = []
    ResultsData = {}
    queryNumber = 0

    # Get a logger
    logger = logging.getLogger(name = 'Main')
    logger.setLevel(logging.INFO)
    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    # add ch to logger
    logger.addHandler(ch)

    def AccumulateStats(self,searchMiles,localTime,queryStats):
        self.StatsData = {}
        self.StatsData["QueryNumber"] = self.queryNumber
        self.queryNumber += 1
        self.StatsData['SearchMiles'] = searchMiles
        self.StatsData['RoundTripQueryTime'] = localTime
        AllGpCellStats = queryStats['GpCellStats']
        self.StatsData['GpCellCount'] = len(AllGpCellStats)

        cacheHit = 0
        found = 0
        inBounds = 0
        hasShops = 0
        cellResolution = []
        nonCacheSearchTime = []
        allSearchTime = []
        for GpGridCell in AllGpCellStats:
            GpCellStats = AllGpCellStats[GpGridCell]
            # Record raw stats data
            self.StatsDataRaw = {}
            self.StatsDataRaw['QueryNumber'] =  self.queryNumber
            self.StatsDataRaw['GpGridCell'] = GpGridCell
            self.StatsDataRaw['StartTime'] = GpCellStats['StartTime']
            self.StatsDataRaw['EndTime'] = GpCellStats['EndTime']
            self.StatsDataRaw['CacheHit'] = GpCellStats['CacheHit']
            self.StatsDataRaw['Found'] = GpCellStats['Found']
            self.StatsDataRaw['InBounds'] = GpCellStats['InBounds']
            self.StatsDataRaw['HasShops'] = GpCellStats['HasShops']
            self.AllStatsDataRaw.append(self.StatsDataRaw)

            # Record per search query stats data
            cacheHit += GpCellStats['CacheHit']
            found += GpCellStats['Found']
            inBounds += GpCellStats['InBounds']
            hasShops +=  GpCellStats['HasShops']
            searchTime =  GpCellStats['EndTime'] -  GpCellStats['StartTime']
            if  not GpCellStats['CacheHit']:
                nonCacheSearchTime.append(searchTime)
            allSearchTime.append(searchTime)

            gridCellSubString = GpGridCell.rsplit('_')
            gridCellResolution = int(gridCellSubString[0],16)
            cellResolution.append(gridCellResolution)

        self.StatsData['CacheHit'] = cacheHit
        self.StatsData['Found'] = found
        self.StatsData['InBounds'] = inBounds
        self.StatsData['HasShops'] = hasShops
        self.StatsData['MeanCellResolution'] = self.Mean(cellResolution)
        meanNonCacheSearchTime = 0.0
        stdNonCacheSearchTime = 0.0
        if len(nonCacheSearchTime) > 0:
            meanNonCacheSearchTime = self.Mean(nonCacheSearchTime)
            stdNonCacheSearchTime = self.Std(nonCacheSearchTime)
        self.StatsData['MeanNonCacheSearchTime'] = meanNonCacheSearchTime
        self.StatsData['StdNonCacheSearchTime'] = stdNonCacheSearchTime
        meanAllSearchTime = 0.0
        stdAllSearchTime = 0.0
        if len(allSearchTime) > 0:
            meanAllSearchTime = self.Mean(allSearchTime)
            stdAllSearchTime = self.Std(allSearchTime)
        self.StatsData['MeanAllSearchTime'] = meanAllSearchTime
        self.StatsData['StdAllSearchTime'] = stdAllSearchTime
        self.StatsData['CpuUsage'] = queryStats['CpuUsage']
        self.AllStatsData.append(self.StatsData)

    def AccumulateResults(self,EntityAttributeDic):
        self.ResultsData[self.queryNumber] = EntityAttributeDic

    def LogAllStatsData(self):
        for statsData in self.AllStatsData:
            self.logger.info( "------------------------------------")
            self.logger.info( "QueryNumber %d", statsData['QueryNumber'])
            self.logger.info( "SearchMiles %d", statsData['SearchMiles'])
            self.logger.info( "CPU Usage %d", statsData['CpuUsage'])
            self.logger.info( "RoundTripQueryTime %s", statsData['RoundTripQueryTime'])
            self.logger.info( "GpCellCount  %d", statsData['GpCellCount'])
            self.logger.info( "MeanCellResolution  %f", statsData['MeanCellResolution'])
            self.logger.info( "CacheHit  %d", statsData['CacheHit'])
            self.logger.info( "Found  %d", statsData['Found'])
            self.logger.info( "InBounds  %d", statsData['InBounds'])
            self.logger.info( "HasShops %d", statsData['HasShops'])
            self.logger.info( "MeanNonCacheSearchTime %f", statsData['MeanNonCacheSearchTime'])
            self.logger.info( "StdNonCacheSearchTime %f", statsData['StdNonCacheSearchTime'])
            self.logger.info( "MeanAllSearchTime %f", statsData['MeanAllSearchTime'])
            self.logger.info( "StdAllSearchTime %f", statsData['StdAllSearchTime'])


    def Mean(self,numberList):
        count = len(numberList)
        mean = 0.0
        if not count:
            return mean
        sum = 0.0
        for number in numberList:
            sum += float(number)
        if count > 0:
            mean = sum / float(count)
        return mean

    def Std(self,numberList):
        count = len(numberList)
        std = 0.0
        mean = self.Mean(numberList)
        if not count:
            return std
        squareSum = 0.0
        for number in numberList:
            numberFloat = float(number) - mean
            squareSum = numberFloat * numberFloat
        variance = squareSum / float(count)
        std = math.sqrt(variance)
        return std

    def WriteAllRawStatsToCsvFile(self,directoryPath,fileName):
        # Create a filePath and open the file
        filePath = os.path.join(directoryPath,fileName)
        try:
            csvFile = open(filePath,'w')
        except csv.Error as e:
            sys.exit('Failed to open file {} : {}'.format(filePath,e))
         # Create a list of fields (column names) in desired order
        fieldNames = [
             "QueryNumber",
             "GpGridCell",
             "StartTime",
             "EndTime",
             "CacheHit",
             "Found",
             "InBounds",
             "HasShops" ]

        writer = csv.DictWriter(csvFile,fieldNames)
        columnDic = {}
        for fieldName in fieldNames:
            columnDic[fieldName] = fieldName
        columnDic['QueryNumber'] = "Query Number"
        columnDic['GpGridCell'] = "GpGridCell"
        columnDic['StartTime'] = "Start Time"
        columnDic['EndTime'] = "End Time"
        columnDic['CacheHit'] = "Cache Hit"
        columnDic['Found'] = "Found Count"
        columnDic['InBounds'] = "In Bounds Count"
        columnDic['HasShops'] = "Has Shops Count"

        # Write a row of headings
        writer.writerow(columnDic)
        for statsData in self.AllStatsDataRaw:
            writer.writerow(statsData)

        csvFile.close()

    def WriteAllStatsToCsvFile(self,directoryPath,fileName):

        # Create a filePath and open the file
        filePath = os.path.join(directoryPath,fileName)
        try:
            csvFile = open(filePath,'w')
        except csv.Error as e:
            sys.exit('Failed to open file {} : {}'.format(filePath,e))

        # Create a list of fields (column names) in desired order
        fieldNames = [
             "QueryNumber",
             "SearchMiles",
             "CpuUsage",
             "RoundTripQueryTime",
             "MeanCellResolution",
             "GpCellCount",
             "CacheHit",
             "Found",
             "InBounds",
             "HasShops",
             "MeanNonCacheSearchTime",
             "StdNonCacheSearchTime",
             "MeanAllSearchTime",
             "StdAllSearchTime"]
        writer = csv.DictWriter(csvFile,fieldNames)
        columnDic = {}
        for fieldName in fieldNames:
            columnDic[fieldName] = fieldName
        columnDic['QueryNumber'] = "Query Number"
        columnDic['SearchMiles'] = "Search Miles"
        columnDic['CpuUsage'] = "CPU Usage"
        columnDic['RoundTripQueryTime'] = "Round Trip Query Time"
        columnDic['MeanCellResolution'] = "Mean Cell Resolution"
        columnDic['GpCellCount'] = "GpCell Count"
        columnDic['CacheHit'] = "Cache Hit"
        columnDic['MeanNonCacheSearchTime'] = "Mean Non-Cache Search Time"
        columnDic['StdNonCacheSearchTime'] = "STD Non-Cache Search Time"
        columnDic['MeanAllSearchTime'] = "Mean All Search Time"
        columnDic['StdAllSearchTime'] = "STD All Search Time"

        # Write a row of headings
        writer.writerow(columnDic)
        for statsData in self.AllStatsData:
            writer.writerow(statsData)
   
        csvFile.close()

    def WriteAllResultsToCsvFile(self,directoryPath,fileName):

           # Create a filePath and open the file
        filePath = os.path.join(directoryPath,fileName)
        try:
            csvFile = open(filePath,'w')
        except csv.Error as e:
            sys.exit('Failed to open file {} : {}'.format(filePath,e))

        # Reformat the results data dictionary
        allResultsData = []

        for queryNumber in self.ResultsData:
            resultsData = {}
            resultsDataDic = self.ResultsData[queryNumber]
        
            for entity in resultsDataDic:
                resultsData["QueryNumber"] = queryNumber
                resultsData["KeyName"] = entity
                attributeDic = resultsDataDic[entity]
                #resultsData['distanceMiles'] = attributeDic['distanceMiles']
                resultsData['lattitude'] = attributeDic['lattitude']
                resultsData['longitude'] = attributeDic['longitude']
                #resultsData['has_shops'] = attributeDic['has_shops']
                #resultsData['vendor'] = attributeDic['vendor']
            allResultsData.append(resultsData)

        # Create a list of fields (column names) in desired order
        fieldNames = [
             "QueryNumber",
             "KeyName",
             #"distanceMiles",
             "lattitude",
             "longitude",
             #"has_shops",
             #"vendor"
              ]
        writer = csv.DictWriter(csvFile,fieldNames)
        columnDic = {}
        for fieldName in fieldNames:
            columnDic[fieldName] = fieldName
        columnDic['QueryNumber'] = "Query Number"
        columnDic['KeyName'] = "KeyName"
        #columnDic['distanceMiles'] = "Distance Miles"
        #columnDic['has_shops'] = "Has Shops"
        columnDic['lattitude'] = "Lattitude"
        columnDic['longitude'] = "Longitude"
        #columnDic['vendor'] = "Vendor"

        # Write a row of headings
        writer.writerow(columnDic)
        for resultsData in allResultsData:
            writer.writerow(resultsData)

        csvFile.close()