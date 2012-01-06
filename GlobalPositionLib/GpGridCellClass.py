""" Copyright(c) 2011 FriendzyShop, LLC. All rights reserved """
__author__ = 'Brian Sargent'

import logging
from GlobalPositionLib import MAXIMUM_RESOLUTION

from GlobalPositionLib.GpGridPointClass import GpGridPoint

# A Global Position Cell (GpGridCell) represents a rectangular region in lattitude-longitude coordinates.
#
# The lattitude resolution is the number of bits in the integer representation of the cell's lattitude.
# The longitude resolution is set to 1 more than the lattitude resolution. This makes the cells nearly
# square in distance near the equator. Cells decrease in width (west-east measurement) away from the
# equator. At 60 degrees lattitude, the width is 1/2 of the height.
#
# Each GpGridCell of resolution m-1 encloses 4 cells of resolution m.
#
# A cell is uniquely identified by the lattitude-longitude coordinates of its SouthWest corner plus its resolution.
# The cell width and height are the degrees spanned by one bit interval at the specified resolution.
# If the four corners of the cell are NW,NE,SW,SW, a lattitude-longitude point is contained by the cell if
#    W <= point.longitude < E and S <= point.longitude < N


class GpGridCell():
    Origin = GpGridPoint()
    
    def InitFromGridPoint(self,gpGridPoint):
        self.Origin.InitFromIntLatLon(gpGridPoint.LattitudeInt,gpGridPoint.LongitudeInt,gpGridPoint.Resolution)

    def InitFromCoordinates(self, lattitude, longitude, resolution):
        self.Origin.InitFromCoordinates( lattitude, longitude, resolution)

    def InitFromShortCellString(self, cellShortString, resolution):
        self.Origin = GpGridPoint()
        self.Origin.InitFromShortString(cellShortString, resolution)
        
    def ToLongString(self):
        """ Return a long string representation of this GridCell.

        The cell is identified by the long string representation of its origin."""
        return self.Origin.ToLongString()

    def ToShortString(self):
        """ Return a short string representation of this GridCell.

        The cell is identified by the short string representation of its origin along with
        its resolution."""
        return self.Origin.ToShortString()

    def ListCornerPointsShort(self):
        """Return a list of the four corner points for this cell in the short string format.

        The points are identified by their short string representation"""
        cellList= []
        cellList.append(self.Origin.ToShortString())
        nwPoint = self.Origin.GetAdjacentPoint('N')
        cellList.append(nwPoint.ToShortString())
        nePoint = nwPoint.GetAdjacentPoint('E')
        cellList.append(nePoint.ToShortString())
        sePoint = nePoint.GetAdjacentPoint('S')
        cellList.append(sePoint.ToShortString())
        return cellList

    def ListChildCellsShort(self):
        """ Return a list of the 4 child cells in GpGridPointShortString format"""
        # Get the origin point of child cell that is co-located with the Origin Point
        parentResolution = self.Origin.Resolution
        if parentResolution == MAXIMUM_RESOLUTION:
            logging.debug("GpGridCell is at maximum resolution %d, so there are no child cells" %\
                             parentResolution)
            return []
        childOriginGridPoint = GpGridPoint()
        childOriginGridPoint.InitFromIntLatLon(self.Origin.LattitudeInt,self.Origin.LongitudeInt,\
                                               self.Origin.Resolution +1)
        # Create a GpGridCell at the child origin
        swChildGridCell = GpGridCell()
        swChildGridCell.InitFromGridPoint(childOriginGridPoint)
        # The 4 corner points of the SW child GridCell are the origins of the 4 child cells
        return swChildGridCell.ListCornerPointsShort()
