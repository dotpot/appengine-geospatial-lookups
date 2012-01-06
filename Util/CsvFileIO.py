
import os
import sys
import csv

__author__ = 'Brian'


def WriteDicToCsvFile(directoryPath, Dic):
    """ Write a Dictionary to a csv file.

        arg:
            directoryPath - Full path to directory for the csv files
            Dic - dictionary to write to a csv file. The dictionary is organized as
            {keyName:{attributeName:attributeValue}}

        output:
            file is named from the keyName of the first entry in the dictionary
    """
    # Create a filePath and open the file
    keyName = Dic.keys()[0]
    fileName = keyName + '.csv'
    filePath = os.path.join(directoryPath,fileName)
    try:
        csvFile = open(filePath,'w')
    except csv.Error as e:
        sys.exit('Failed to open file {} : {}'.format(filePath,e))

    # Create a list of fields (column names)
    fieldNames = []
    keyName = Dic.keys()[0]
    print "KeyName =",keyName
    fieldNames.append('KeyName')
    attributeDic = Dic[keyName]
    print "attributeDic = ",attributeDic

    columnDic = {"KeyName":"KeyName"}
    for attribute in attributeDic:
        fieldNames.append(attribute)
        columnDic[attribute]=attribute
    writer = csv.DictWriter(csvFile,fieldNames)
    # Write a row of headings
    writer.writerow( columnDic)

    # Restructure the dictionary so that the KeyName is at the
    # same level of hierarchy as the attributes.
    for keyName in Dic:
        rowDic = {'KeyName':keyName}
        attributeDic = Dic[keyName]
        for attribute in attributeDic:
            rowDic[attribute] = attributeDic[attribute]
        writer.writerow(rowDic)

    csvFile.close()

def ReadCsvFilesToDic(directoryPath,keyName,logger):
    """ Read all csv files in a directory into a Dictionary.

        arg:
            directoryPath - Full path to directory containing the csv files
        return:
            dictionary {entity_KeyName:{attributeName:attributeValue}}
    """
    csvFileList = GetCsvFileList(directoryPath, logger)
    if len(csvFileList) == 0:
        logger.error("No csv files found in directory: %s",directoryPath)
    DirectoryCsvDic = {}
    for fileName in csvFileList:
        filePath = os.path.join(directoryPath,fileName)
        fileCsvDic = ReadCsvFileToDic(filePath, keyName)
        DirectoryCsvDic.update(fileCsvDic)
    return DirectoryCsvDic

def ReadCsvFileToDic(filePath, keyName):
    """ Read a single csv file into a dictionary of {ColumnKeyValue: {ColumnName:RowColumnCellValue}}

        arg:
            filePath: csv file full path
            keyName: Name of column that contains the keys for the resultant dictionary
        return:
            dictionary {ColumnKeyValue: {ColumnName:RowColumnCellValue}}
        description:
            Each row in the csv file is a dictionary of {ColumnName:RowColumnValue}. The value in the
            designated key column is extracted from the row dictionary and used as a key for the created
            dictionary. The remainder of the row dictionary is the value associated with the key.
    """
    csvFile = open(filePath,'r')
    reader = csv.DictReader(csvFile)
    CsvDic = {}
    for rowDic in reader:
        keyValue = rowDic[keyName]
        del rowDic[keyName]
        CsvDic[keyValue] = rowDic
    return CsvDic

def ReadCsvFileToItemDic(filePath):
    """ Read a single csv file into a dictionary of {itemNumber: {ColumnName:RowColumnCellValue}}

        arg:
            filePath: csv file full path
            keyName: Name of column that contains the keys for the resultant dictionary
        return:
            dictionary {ColumnKeyValue: {ColumnName:RowColumnCellValue}}
        description:
            Each row in the csv file is a dictionary of {ColumnName:RowColumnValue}. 
    """
    csvFile = open(filePath,'r')
    reader = csv.DictReader(csvFile)
    CsvDic = {}
    item = 0
    for rowDic in reader:
        CsvDic[item] = rowDic
        item += 1
    return CsvDic

def GetCsvFileList(directoryPath, logger):
    """ Return a list of csv files in a directory.

        Verifies that the directory is valid then returns a list of all
        fileNames in the directory that have a .csv or .CSV extension
    """
    if  not os.access(directoryPath,os.F_OK):
        logger.error("Error - cant access directory: %s",directoryPath)
        return []
    dirList = os.listdir(directoryPath)
    csvFileList = []
    logger.info("Reading files:")
    for fileName in dirList:
        baseName,extension = os.path.splitext(fileName)
        logger.info("  %s%s",baseName,extension)
        if extension.lower() == '.csv':
            csvFileList.append(fileName)
    return csvFileList
