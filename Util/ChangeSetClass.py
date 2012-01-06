import logging
import sys
import Util.DataConversion as DataConversion
import HttpInterface.HttpInterface as HttpInterface

__author__ = 'Brian'

class ChangeSet:

    ChangeSetDic = {}
    entityAttributeDic = {}
    classEntityDic = {}
    groupVersions = {'Vendor':1,'Location':1,'Shopper':1}

    httpUploadAction = 'PostChangeSet'

    def AddAttributes(self, entityKeyName, attributeDic):
        self.entityAttributeDic[entityKeyName] = attributeDic

    def AddEntityAttributeDic(self, entityAttributeDic):
        for keyName in entityAttributeDic:
            self.AddAttributes(keyName, entityAttributeDic[keyName])

    def EntityCount(self):
        return len(self.entityAttributeDic)

    def AddClassEntities(self, className):
        if len(self.entityAttributeDic) == 0:
            logging.error("'ChangeSet.AddClassEntities(): EntityAttribute Dictionary is empty")
        self.classEntityDic[className] = self.entityAttributeDic
        
    def CloseChangeSet(self, groupName, crudOp):
        self.ChangeSetDic['g'] = groupName
        if not groupName in  self.groupVersions:
            logging.error("'ChangeSet.CloseChangeSet(): No Group %s Found in Versions Dictionary",groupName)
            version = 1
        else:
            version =  self.groupVersions[groupName]

        self.ChangeSetDic['v'] = version
        self.ChangeSetDic[crudOp] = self.classEntityDic

    def ClearChangeSet(self):
        """ Clear the ChangeSet contents and components"""
        self.ChangeSetDic = {}
        self.entityAttributeDic = {}
        self.classEntityDic = {}

    def ToJSON(self):
        """ Convert the ChangeSet to JSON format"""
        try:
            json = DataConversion.dict_to_json(self.ChangeSetDic)
        except:
            logging.error('ChangeSet.ToJSON() Threw Exception %s',sys.exc_info())
            json = ""
        return json

    def Upload(self, httpHostAndPort, httpPage = 'Admin', debug = True):
        """ Upload the ChangeSet to the DataStore"""
        json = self.ToJSON()
        if debug:
            print 'Upload JSON:'
            print json
        # Send to Datastore
        HttpInterface.post_data(httpHostAndPort,httpPage,self.httpUploadAction,json)