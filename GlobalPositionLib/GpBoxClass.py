""" Copyright (c) 2011 FriendzyShop, LLC. All rights reserved """
from GlobalPositionLib.GpPointClass import GpPoint

__author__ = 'Brian Sargent'


class GpBox():

    """ Represents a rectangular region in lattitude-longitude.

        The box is bounded by  NorthWest and SouthEast corner points, defined with floats.
    """

    def __init__(self,northLattitude,westLongitude,southLattitude,eastLongitude):
        self.NorthLattitude = float(northLattitude)
        self.WestLongitude = float(westLongitude)
        self.SouthLattitude = float(southLattitude)
        self.EastLongitude = float(eastLongitude)

        self.NW_GpPoint = GpPoint(self.NorthLattitude,self.WestLongitude)
        self.SE_GpPoint = GpPoint( self.SouthLattitude,self.EastLongitude)


    def __eq__(self, other):
        return self.NW_GpPoint == other.NW_GpPoint and self.SE_GpPoint == other.SE_GpPoint

    def __str__(self):
        return 'NW(%f, %f) SE(%f, %f)' % \
               (self.NorthLattitude, self.WestLongitude,self.SouthLattitude,self.EastLongitude)
    