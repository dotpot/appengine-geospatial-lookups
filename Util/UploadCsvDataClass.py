import os

__author__ = 'Brian Sargent'

from Util import ChangeSetClass
from Util import CsvFileIO

class UpLoadCsvData:

    # Default definitions for HTTP upload
    httpHostAndPort = 'localhost:8080'
    changeSet = ChangeSetClass.ChangeSet()

    # Default data directory
    ModelDataDirectory = os.path.join("TestVectorData","ModelData")

    changeSet = ChangeSetClass.ChangeSet()

    def UploadCsvData(self,region,Group,Kind):
        """Create random Vendor data and upload """
        groupDirectory = region + '_' + Group
        directoryPath = os.path.join(self.ModelDataDirectory,groupDirectory)

        csvFiles = CsvFileIO.GetCsvFileList(directoryPath)
        for csvFile in csvFiles:
            csvFilePath = os.path.join(directoryPath,csvFile)
            entityAttributeDic = CsvFileIO.ReadCsvFileToDic(csvFilePath,"KeyName")
            # Bundle current location dictionary into a ChangeSet and upload
            self.UploadChangeSet(entityAttributeDic,Kind,Group)
       
    def UploadChangeSet(self,entityDic,className,groupName):
        self.changeSet.ClearChangeSet()
        self.changeSet.AddEntityAttributeDic(entityDic)
        self.changeSet.AddClassEntities(className)
        self.changeSet.CloseChangeSet(groupName,'c')
        self.changeSet.Upload(self.httpHostAndPort)



