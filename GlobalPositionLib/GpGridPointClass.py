""" Copyright (c) 2011 FriendzyShop, LLC. All rights reserved """
__author__ = 'Brian Sargent'

from GlobalPositionLib import MAXIMUM_RESOLUTION
from GlobalPositionLib import DIRECTION_VECTORS
from GlobalPositionLib import TO_INT_SCALE
from GlobalPositionLib import TO_FLOAT_SCALE
from GlobalPositionLib.GpModel import ToLongGpGridPointString, ToShortGpGridPointString, GetLattitudeResolution, GetLongitudeResolution

# A Global Position Grid Point (GpGridPoint) represents the lattitude-longitude coordinates of a point
# on a lattitude-longitude grid.
#
# The lattitude grid is in the range -90.0 degrees to +90.0 degrees. This range is divided into a grid
# of 2**MAXIMUM_RESOLUTION points. Integer lattitude is in the range of (0 to 2**MAXIMUM_RESOLUTION - 1).
# GpGridPoint.LatitudeInt = 0 corresponds to -90.0 degrees.
#
# The longitude grid is in the range -180.0 degrees to +180.0 degrees. The range is divided into a grid
# of 2**(MAXIMUM_RESOLUTION + 1) points. Integer longitude is in the range of (0 to 2**(MAXIMUM_RESOLUTION +1)-1).
# GpGridPoint.LongitudeInt = 0 corresponds to -180.0 degrees.
#
# Decreasing the Resolution from MAXIMUM_RESOLUTION by 1 doubles the distance between adjacent GpGridPoints.
# The number of bits used to represent LattitudeInt and Longitude in remains the same as the resolution is decreased.

class GpGridPoint:

    LattitudeFloat = None   # Range -90.0 to +90.0
    LongitudeFloat = None   # Range -180.0 to +180.0
    LattitudeInt = None  # Represents -90.0 to +90.0 as positive integer of MAXIMUM_RESOLUTION bits
    LongitudeInt = None  # Represents -9180.0 to +180.0 as positive integer of MAXIMUM_RESOLUTION + 1 bits
    Resolution = MAXIMUM_RESOLUTION

    def InitFromGpPoint(self, GpPoint, resolution):
        """ Initialize from a GpPoint at specified resolution."""
        self.InitFromCoordinates(GpPoint.lat, GpPoint.lon ,resolution)

    def InitFromCoordinates(self, lattitude, longitude, resolution):
        """ Initialize a GpGridPoint from lattitude, longitude coordinates and resolution

        args:
            resolution - lattitude of -90.0 to +90.0 is divided into 2**resolution points.
                       - longitude of -180.0 to +180.0 is divided into 2**(resolution + 1) points.
        """
        lattitudeFloat = float(lattitude)
        longitudeFloat = float(longitude)

        self.Resolution = resolution

        # Represent coordinates with positive integer of maximum number of bits
        lattitudeInt = int(TO_INT_SCALE *(lattitudeFloat + 90.0))
        longitudeInt = int(TO_INT_SCALE *(longitudeFloat + 180.0))

        # Convert to integers of the specified resolution by shifting zeros into least-significant bits
        shift = MAXIMUM_RESOLUTION - self.Resolution
        self.LattitudeInt = (lattitudeInt >> shift) << shift
        self.LongitudeInt = (longitudeInt >> shift) << shift

        # Convert latitude,longitude integers to floats
        self._initLatLonFloats()

    def InitFromIntLatLon(self,lattitudeInt,longitudeInt,resolution):
        """ Initialize from integers at the maximum resolution 
        args:
            lattitudeInt - scaled at 2**MAX_RESOLUTION
            longitudeInt - scaled at 2**(MAX_RESOLUTION + 1)"""
        self.Resolution = resolution
        shift =  MAXIMUM_RESOLUTION - self.Resolution
        self.LattitudeInt = (lattitudeInt >> shift) << shift
        self.LongitudeInt = (longitudeInt >> shift) << shift
        self._initLatLonFloats()

    def InitFromLongString(self, gpGridPointString):
        """ Initialize from a long gpGridPoint string representation.

        An example of the long format is 10_a345_102b6, where 10 is the resolution (16 in hex),
        a345 is the latitude integral value, and 102b6 is the longitude integral value.
        """
        # Split into the three sub-strings
        args = gpGridPointString.rsplit('_')
        self.Resolution = int(args[0],16)
        self.LattitudeInt = int(args[1],16)
        self.LongitudeInt = int(args[2],16)
        # Convert latitude,longitude integers to floats
        self._initLatLonFloats()

    def InitFromShortString(self, gpGridPointString, resolution):
         """ Initialize from a short string representation of a GpGridPoint. """
         # Split into two sub-strings
         args = gpGridPointString.rsplit('_')
         self.Resolution = resolution
         shift = MAXIMUM_RESOLUTION - resolution
         # Scale integer coordinates to the maximum resolution
         self.LattitudeInt = int(args[0],16) << shift
         self.LongitudeInt = int(args[1],16) << shift
         # Convert latitude,longitude integers to floats
         self._initLatLonFloats()

    def ToLongString(self):
        """ Represent the GpGridPoint with a hex string containing resolution and integral lattitude, longitude
        coordinates.

        """
        return ToLongGpGridPointString(self.LattitudeInt,self.LongitudeInt,self.Resolution)


    def ToShortString(self):
        """ Represent the GpGridPoint with a short hex string. """
        shift = MAXIMUM_RESOLUTION - self.Resolution
        lat = self.LattitudeInt >> shift
        lon = self.LongitudeInt >> shift
        return ToShortGpGridPointString(lat,lon,self.Resolution)

    def GetAdjacentPoint(self,direction):
        """ Get an adjacent point of the same resolution in the specified direction.

        direction - A one or two character key in DIRECTION_VECTORS  ('N', 'NW', 'S','E',...)
        """
        if not direction in DIRECTION_VECTORS:
             raise ValueError("Invalid direction vector: %s" % str(direction))
        vector = DIRECTION_VECTORS[direction]
        shift = MAXIMUM_RESOLUTION - self.Resolution
        scale = 1 << shift
        lattitudeInt = self.LattitudeInt + scale * vector[0]
        longitudeInt = self.LongitudeInt + scale * vector[1]
        shiftedGpGridPoint = GpGridPoint()
        shiftedGpGridPoint.InitFromIntLatLon(lattitudeInt,longitudeInt,self.Resolution)
        return shiftedGpGridPoint

    def _initLatLonFloats(self):
         """ Convert integers fields to floats."""
         self.LattitudeFloat = self.LattitudeInt * TO_FLOAT_SCALE - 90.0
         self.LongitudeFloat = self.LongitudeInt *  TO_FLOAT_SCALE - 180.0

  
    def DecreaseResolution(self):
        """ Decrease the resolution by one step """
        self.Resolution -= 1
        self.LattitudeInt = (self.LattitudeInt >> 1) << 1
        self.LongitudeInt = (self.LongitudeInt >> 1) << 1
        self._initLatLonFloats()