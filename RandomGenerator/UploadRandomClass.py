
__author__ = 'Brian'

from Util import ChangeSetClass
from RandomGenerator import RandomGeneratorClass

class UploadRandom:

    # Constant definitions for HTTP upload
    httpHostAndPort = 'localhost:8080'
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
    InitialVendorIndex = 0
    LastVendorIndex = 0
    InitialLocationIndex = 0
    LastLocationIndex = 0

    def CreateVendorData(self,numberVendors):
        """Create random Vendor data and upload """
        indices = range(numberVendors)
        entityCount = 0
        vendorDic = {}
        for index in indices:
            vendorIndex = self.InitialVendorIndex + index
            indexString = str(vendorIndex)
            vendorKeyName = 'Ven' + indexString.rjust(4,'0')
            entityAttributeDic = self.randomGenerator.CreateVendorEntityAttributeDic(vendorKeyName)
            # Save all Vendor KeyNames locally
            self.VendorKeyNames.append(vendorKeyName)
            # Save local all Vendor entity-attribute dictionary locally
            self.VendorAllEntityAttributeDic[vendorKeyName] = entityAttributeDic[vendorKeyName]
            vendorDic[vendorKeyName] = entityAttributeDic[vendorKeyName]
            entityCount += 1
            if  entityCount >=  self.MaxEntitiesPerChangeSet:
                # Bundle current location dictionary into a ChangeSet and upload
                self.UploadChangeSet(vendorDic,'Vendor','Vendor')
                vendorDic = {}
                entityCount = 0

        if  entityCount > 0:
            # Bundle and upload any remaining entities
            self.UploadChangeSet(vendorDic,'Vendor','Vendor')

    def CreateLocationData(self,numberLocationsPerVendor = 2):
        """Create random Location data and upload """
        locationIndex = self.InitialLocationIndex
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
                    self.UploadChangeSet(locationDic,'Location','Location')
                    locationDic = {}
                    entityCount = 0

            self.VendorLocationDic[vKeyName] = locationKeyNames
        # Upload any remaining entities
        if entityCount > 0 :
            self.UploadChangeSet(locationDic,'Location','Location')


    def CreateShopTemplateData(self,numberLocationsPerVendor = 2):
        """Create random ShopTemplate data and upload """
        shopTemplateIndex = 0
        for vKeyName in self.VendorKeyNames:
            shopTemplateKeyNames = []
            for locationCount in range(numberLocationsPerVendor):
                shopTemplateIndexString = str(shopTemplateIndex)
                shopTemplateIndex += 1
                shopTemplateOnlyKey = 'ShpTmp' + shopTemplateIndexString.rjust(6,'0')
                shopTemplateKeyName = vKeyName + shopTemplateOnlyKey
                entityAttributeDic = \
                        self.randomGenerator.CreateShopTemplateEntityAttributeDic(vKeyName,shopTemplateKeyName)
                shopTemplateKeyNames.append(shopTemplateKeyName)
                self.VendorShopTemplateDic[vKeyName] = shopTemplateKeyNames
                self.ShopTemplateAllEntityAttributeDic[shopTemplateKeyName] = entityAttributeDic[shopTemplateKeyName]
        # Upload the ChangeSet
        self.changeSet.ClearChangeSet()
        self.changeSet.AddEntityAttributeDic(self.LocationAllEntityAttributeDic)
        self.changeSet.AddClassEntities('ShopTemplate')
        self.changeSet.CloseChangeSet('Vendor','c')
        self.changeSet.Upload(self.httpHostAndPort)

    def CreateShopData(self,numberShopsPerTemplate = 2):
        """ Create and Upload Random Shops """
        shopIndex = 0
        self.ModelKindToUpload = 'Shop'
        self.ModelGroupToUpload = 'Location'
        self.EntityAttributeDicToUpLoad = {}
        for vKeyName in self.VendorKeyNames:
            for locKeyName in self.VendorLocationDic[vKeyName]:
                for shpTemplateKeyName in self.VendorShopTemplateDic[vKeyName]:
                    for shopCount in range (numberShopsPerTemplate):
                        shopIndexString = str(shopIndex)
                        shopIndex += 1
                        shopOnlyKey = 'Shop' + shopIndexString.rjust(6,'0')
                        shopKeyName = locKeyName + shopOnlyKey
                        entityAttributeDic = \
                            self.randomGenerator.CreateShopEntityAttributeDic(locKeyName,
                                                shpTemplateKeyName, shopKeyName)
                        self.ShopAllEntityAttributeDic[shopKeyName] = entityAttributeDic[shopKeyName]
        # Upload the ChangeSet
        self.changeSet.ClearChangeSet()
        self.changeSet.AddEntityAttributeDic(self.ShopAllEntityAttributeDic)
        self.changeSet.AddClassEntities('Shop')
        self.changeSet.CloseChangeSet('Location','c')
        self.changeSet.Upload(self.httpHostAndPort)

    def UploadChangeSet(self,entityDic,className,groupName):
        self.changeSet.ClearChangeSet()
        self.changeSet.AddEntityAttributeDic(entityDic)
        self.changeSet.AddClassEntities(className)
        self.changeSet.CloseChangeSet(groupName,'c')
        self.changeSet.Upload(self.httpHostAndPort)

    def SetGeoBoundaries(self,minLattitude,maxLattitude,minLongitude,maxLongitude):
        """ Set boundaries for random lat-lon generation"""
        self.randomGenerator.minimumLattitude = minLattitude
        self.randomGenerator.maximumLattitude = maxLattitude
        self.randomGenerator.minimumLongitude = minLongitude
        self.randomGenerator.maximumLongitude = maxLongitude

