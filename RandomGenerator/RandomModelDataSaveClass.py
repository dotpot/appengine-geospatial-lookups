import os

__author__ = 'Brian'

from Util import ChangeSetClass
from RandomGenerator import RandomGeneratorClass
from Util import CsvFileIO

class RandomModelDataSave:

    changeSet = ChangeSetClass.ChangeSet()
    MaxEntitiesPerChangeSet = 100
    
    randomGenerator = RandomGeneratorClass.RandomDataGenerator()
    # Dictionaries of created data
    VendorKeyNames = []

    VendorLocationDic = {}
    shopTemplateKeyNames = []
    VendorShopTemplateDic = {}
    # Local copies of entire contents uploaded to DataStore
    VendorAllEntityAttributeDic = {}
    ShopTemplateAllEntityAttributeDic = {}
    LocationAllEntityAttributeDic = {}
    ShopAllEntityAttributeDic = {}

    LastVendorIndex = 0
    LastLocationIndex = 0

    ModelDataDirectory = "TestVectorCsvData1\\ModelData\\"
    LocationModelDataDirectory = 'Location\\'
    VendorModelDataDirectory = 'Vendor\\'

    def CreateAndSaveVendorData(self,firstVendorIndex,numberVendors):
        """Create random Vendor data and save to csv file."""
        VendorDirectory = os.path.join(self.ModelDataDirectory,self.VendorModelDataDirectory)

        wd =os.getcwd()
        print "Working Directory =",wd
        print "Vendor Directory = ",VendorDirectory

        indices = range(numberVendors)
        entityCount = 0
        vendorDic = {}
        for index in indices:
            vendorIndex = firstVendorIndex + index
            indexString = str(vendorIndex)
            vendorKeyName = 'Ven' + indexString.rjust(4,'0')
            entityAttributeDic = self.randomGenerator.CreateVendorEntityAttributeDic(vendorKeyName)
            # Build list of all vendor keyNames
            self.VendorKeyNames.append(vendorKeyName)
            # Save local all Vendor entity-attribute dictionary locally
            self.VendorAllEntityAttributeDic[vendorKeyName] = entityAttributeDic[vendorKeyName]
            vendorDic[vendorKeyName] = entityAttributeDic[vendorKeyName]
            entityCount += 1
            if  entityCount >=  self.MaxEntitiesPerChangeSet:
                # Bundle current location dictionary into a ChangeSet and save
                CsvFileIO.WriteDicToCsvFile(VendorDirectory,vendorDic)
                vendorDic = {}
                entityCount = 0

        if  entityCount > 0:
            # Bundle and save any remaining entities
            CsvFileIO.WriteDicToCsvFile(VendorDirectory,vendorDic)

    def CreateAndSaveLocationData(self,firstLocationIndex,numberLocationsPerVendor = 2):
        """Create random Location data and save to csv file """
        LocationDirectory = os.path.join(self.ModelDataDirectory,self.LocationModelDataDirectory)

        print "Location Directory = ",LocationDirectory
        locationIndex = firstLocationIndex
        entityCount = 0
        locationDic = {}
        for vKeyName in self.VendorKeyNames:
            locationKeyNames = []
            for locationCount in range(numberLocationsPerVendor):
                # Create a keyName for a Location entity
                locationIndexString = str(locationIndex)
                locationIndex += 1
                locationKeyName = 'Loc' + locationIndexString.rjust(6,'0')
                locationKeyNames.append(locationKeyName)
                # Create random data for this entity
                entityAttributeDic =  self.randomGenerator.CreateLocationEntityAttributeDic(vKeyName,locationKeyName)
                self.LocationAllEntityAttributeDic[locationKeyName] = entityAttributeDic[locationKeyName]
                locationDic[locationKeyName] = entityAttributeDic[locationKeyName]
                entityCount += 1
                if  entityCount >=  self.MaxEntitiesPerChangeSet:
                    # Bundle current location dictionary into a ChangeSet and upload
                    CsvFileIO.WriteDicToCsvFile(LocationDirectory, locationDic)
                    locationDic = {}
                    entityCount = 0

            self.VendorLocationDic[vKeyName] = locationKeyNames
        # Save any remaining entities
        if entityCount > 0 :
            CsvFileIO.WriteDicToCsvFile(LocationDirectory, locationDic)

        

    def SetRegionBoundary(self,regionGpBox):
        """ Set boundaries for random lat-lon generation"""
        self.RegionGpBox = regionGpBox
        self.randomGenerator.minimumLattitude = regionGpBox.SouthLattitude
        self.randomGenerator.maximumLattitude = regionGpBox.NorthLattitude
        self.randomGenerator.minimumLongitude = regionGpBox.WestLongitude
        self.randomGenerator.maximumLongitude = regionGpBox.EastLongitude