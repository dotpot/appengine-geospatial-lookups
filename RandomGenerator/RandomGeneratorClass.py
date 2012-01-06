""" Copyright (c) 2011 FriendzyShop, LLC. All rights reserved """

import random
from GlobalPositionLib.GpBoxClass import GpBox

__author__ = 'Brian Sargent'


class RandomDataGenerator:
    """ Generate random model class entity data and random search data """

    RegionGpBox = GpBox(0.0,0.0,0.0,0.0)

    ShopTemplateAllEntityAttributeDic = {}
    LocationAllEntityAttributeDic = {}
    ShopAllEntityAttributeDic = {}

    def SetRegion(self,regionGpBox):
        """ Set boundaries for random location data with a GpBox. """
        self.RegionGpBox = regionGpBox
        self.minimumLattitude = regionGpBox.SouthLattitude
        self.maximumLattitude = regionGpBox.NorthLattitude
        self.minimumLongitude = regionGpBox.WestLongitude
        self.maximumLongitude = regionGpBox.EastLongitude
    
    def CreateRandomName(self,name):
        address = name + str(random.randint(0,1000000))
        return address

    def CreateRandomPhoneNumber(self):
        areaCode = random.randint(100,999)
        prefix = random.randint(100,999)
        number = random.randint(1000,9999)
        phoneNumber = '('+ str(areaCode) + ')' + str(prefix) + '-' + str(number)
        return phoneNumber

    def CreateVendorEntityAttributeDic(self,KeyName):
        """ Create a Single Vendor Entity-Attribute Dictionary with Random Data"""
        vendorDic = {}
        vendorDic['corporate_name'] = self.CreateRandomName('CorporateName')
        vendorDic['address'] = self.CreateRandomName('Address')
        vendorDic['phone_number'] = self.CreateRandomPhoneNumber()
        vendorDic['locality'] = self.CreateRandomName('Locality')
        EntityAttributeDic = {KeyName : vendorDic}
        return EntityAttributeDic

    def CreateLocationEntityAttributeDic(self, VendorKeyName, LocationKeyName):
        """ Create a Single Location Entity-Attribute Dictionary with Random Data"""
        locationDic = {}
        locationDic['vendor'] = VendorKeyName
        locationDic['locality'] = self.CreateRandomName('Locality')
        locationDic['address'] = self.CreateRandomName('Address')
        locationDic['phone_number'] = self.CreateRandomPhoneNumber()
        locationDic['business_name'] = self.CreateRandomName('BusinessName')
        locationDic['lattitude'] = str(random.uniform(self.minimumLattitude, self.maximumLattitude))
        locationDic['longitude'] = str(random.uniform(self.minimumLongitude, self.maximumLongitude))
        locationDic['has_shops'] = 'True'
        EntityAttributeDic = {LocationKeyName : locationDic}
        return EntityAttributeDic
      
    def CreateShopTemplateEntityAttributeDic(self,VendorKeyName,ShopTemplateKeyName):
        """ Create a Single ShopTemplate Entity-Attribute Dictionary with Random Data"""
        templateDic = {}
        templateDic['parent'] = VendorKeyName
        templateDic['vendor'] = VendorKeyName
        templateDic['shop_info'] = self.CreateRandomName('ShopInfo')
        EntityAttributeDic = {ShopTemplateKeyName : templateDic}
        return EntityAttributeDic

    def CreateShopEntityAttributeDic(self, locationKeyName, shopTemplateKeyName, shopKeyName):
        """ Create a Single Shop Entity-Attribute Dictionary with Random Data"""
        shopDic = {}
        shopDic['location'] = locationKeyName
        shopDic['parent']   = locationKeyName
        shopDic['shop_template']   = shopTemplateKeyName
        shopDic['item_ids'] = self.CreateRandomName('ItemIds')
        shopDic['cash'] = str(random.randint(10,1000))
        shopDic['points'] = str(random.randint(10,1000))
        shopDic['status'] = 'available'
        EntityAttributeDic = {shopKeyName : shopDic}
        return EntityAttributeDic

    def CreateRandomLattitudeLongitude(self):
        """ Create a random lattitude, longitude tuple """
        lattitude = random.uniform(self.minimumLattitude, self.maximumLattitude)
        longitude = random.uniform(self.minimumLongitude, self.maximumLongitude)
        return lattitude,longitude

    def CreateRandomNumber(self,minDistance,maxDistance):
        distance = random.uniform(minDistance,maxDistance)
        return distance
