""" Copyright (c) 2011 FriendzyShop, LLC. All rights reserved """

from GlobalPositionLib.GpBoxClass import GpBox

__author__ = 'Brian Sargent'

class LocationTestData:
    """ This class encapsulations test data for location query tests.

    Define GpBox regions identified by a state abbreviation. All regions are equal in lattitude-longitude
    boundary size, but have location counts varying by powers of 2. (The regions don't represent the actual state
    geographical boundaries).
    """

    SelectedRegion = 'WA'

    def __init__(self):
        # Define equal latitude-longitude sized bounding boxes for different regions
        self.WA_GpBox = GpBox(49.0,-124.0,45.6,-117.0)
        self.MT_GpBox = GpBox(49.0,-114.0,45.6,-107.0)
        self.MN_GpBox = GpBox(49.0, -97.0,45.6, -90.0)
        self.CO_GpBox = GpBox(40.0,-108.0,36.6,-101.0)
        self.MO_GpBox = GpBox(40.0 ,-95.0,36.6 ,-88.0)

        # Create a dictionary of location count and bounding box for all regions
        self.VectorData = {
            'WA' : {'Vendors': 20,'PerVendorLocations':100,'FirstVendorIndex':0   ,'FirstLocationIndex':000000
                    ,'GpBox': self.WA_GpBox},
            'MT' : {'Vendors': 40,'PerVendorLocations':100,'FirstVendorIndex':500 ,'FirstLocationIndex':100000,
                    'GpBox': self.MT_GpBox},
            'MN' : {'Vendors': 80,'PerVendorLocations':100,'FirstVendorIndex':1000,'FirstLocationIndex':200000,
                    'GpBox': self.MN_GpBox},
            'CO' : {'Vendors':160,'PerVendorLocations':100,'FirstVendorIndex':1500,'FirstLocationIndex':300000
                    ,'GpBox': self.CO_GpBox},
            'MO' : {'Vendors':320,'PerVendorLocations':100,'FirstVendorIndex':2000,'FirstLocationIndex':400000,
                    'GpBox': self.MO_GpBox}
        }

        self.StateAbbrevList = []
        for stateAbbrev in self.VectorData:
            self.StateAbbrevList.append(stateAbbrev)

    def SetRegion(self,stateAbbrev):
        """ Select a specific region."""
        if not stateAbbrev in self.VectorData:
            print "Error - No Data for %s available" % stateAbbrev
            print "Valid state abbreviations are:", self.StateAbbrevList
        else:
            self.SelectedRegion = stateAbbrev

    def GetVendorCount(self):
        """ Get the Vendor count for the selected region. """
        regionVectorData = self.VectorData[self.SelectedRegion]
        return regionVectorData['Vendors']

    def GetPerVendorLocationCount(self):
        """ Get the number of location per vendor for the selected region. """
        regionVectorData = self.VectorData[self.SelectedRegion]
        return regionVectorData['PerVendorLocations']

    def GetFirstVendorIndex(self):
        """ Get the first index for Vendor data. """
        regionVectorData = self.VectorData[self.SelectedRegion]
        firstVendorIndex = regionVectorData['FirstVendorIndex']
        return firstVendorIndex

    def GetFirstLocationIndex(self):
        """ Get the index of the first location in the selected region """
        regionVectorData = self.VectorData[self.SelectedRegion]
        return regionVectorData['FirstLocationIndex']

    def GetRegionGpBox(self):
        """ Get the bounding GpBox for the selected region """
        regionVectorData = self.VectorData[self.SelectedRegion]
        return regionVectorData['GpBox']
