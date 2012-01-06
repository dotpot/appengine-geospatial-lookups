""" Copyright (c) 2011 FriendzyShop, LLC. All rights reserved """
__author__ = 'Brian Sargent'

from GlobalPositionLib.GpPointClass import GpPoint
from GlobalPositionLib.GpGridPointClass import GpGridPoint
from GlobalPositionLib.GpGridCellClass import GpGridCell
from GlobalPositionLib.GpModel import GpGridCellLongToShortString, GetGridPointResolution, GetParentShortGridCellString
from GlobalPositionLib.GpModel import GpGridCellShortToLongString
from GlobalPositionLib import MAXIMUM_RESOLUTION
from GlobalPositionLib import MINIMUM_RESOLUTION

import GpMath
from Util.SortTupleListClass import SortTupleList

MAXIMUM_GRID_POINT_WEIGHT = 10000.0

class GpSearch:
    """ This class supports a proximity search for locations within a radius from a center point.

        The result for the search computations is a list of GpGridCells to use in a search query.
    """

    SearchBoundaryMeters = None
    MAX_SEARCH_GP_GRID_POINTS = 100000
    MaxSearchCellCount = 10
    # Dictionary of {GpGridCellShortString : CellSearchData} at MaxSearchResolution
    maxResolutionSearchDic = {}
    MaxSearchResolution =  MAXIMUM_RESOLUTION
    FinalSearchResolution = MAXIMUM_RESOLUTION

    # Dictionary of {resolution: {cellStringShort: [nChildGridCellsInBound, cumulativeWeightForCell]}}
    AllLevelCellSearchDataDic = {}
    # Dictionary of {cellStringLong: [nChildGridCellsInBound, cumulativeWeightForCell]}
    SearchCellDic = {}
    # A list of tuples (priority, GpGridCellsLongString), where priority is 0 to len(SearchCellList) - 1.
    # This list is sent to Appengine in search parameters
    SearchCellList = []

    def __init__(self):
        self.maxResolutionSearchDic = {}
        self.SearchCellDic = {}
        self.AllLevelCellSearchDataDic = {}
        self.SearchCellList = []

    
    def ComputeSearchListForMilesProximity(self,centerGpPoint, distanceMiles):
        distanceMeters = GpMath.milesToMeters(distanceMiles)
        self.ComputeSearchListForMetersProximity(centerGpPoint, distanceMeters)

    def ComputeSearchListForMetersProximity(self,centerGpPoint, distanceMeters):
        """ Compute a list of GpGridCells to use in a proximity search query.

            The final list is contained in SearchCellList[]. The cells in the search list are ordered
            by closeness of contained GpPoints to the Center Point.
        """
        self.SearchBoundaryMeters = distanceMeters
        self.CenterGpPoint = centerGpPoint
        self._GetBoundingBoxCells()
        self._LimitMaxSearchResolution()
        self._GetGridPointsWithinRadius()
        self._GetGridCellsWithinRadius()
        self._ReduceSearchCells()
        self._SplitSearchCellsToReduceSearchArea()
        self._PrioritizeCellSearchList()

    def _GetBoundingBoxCells(self):
        """ Get three GpGridPoint corners of a Bounding Box for distanceMeters from a center point.

        The corner points are set to the MaxSearchResolution
        """
        centerGpPoint = self.CenterGpPoint
        degreesOffset = GpMath.distanceMetersToDegrees(centerGpPoint, self.SearchBoundaryMeters)
        # Get bounding corner points
        swCornerF = GpPoint(centerGpPoint.lat - degreesOffset.lat, \
                           centerGpPoint.lon - degreesOffset.lon)
        self.SWCornerGridPoint = GpGridPoint()
        self.SWCornerGridPoint.InitFromGpPoint(swCornerF, self.MaxSearchResolution)

        nwCornerF = GpPoint(centerGpPoint.lat + degreesOffset.lat, \
                           centerGpPoint.lon - degreesOffset.lon)
        self.NWCornerGridPoint = GpGridPoint()
        self.NWCornerGridPoint.InitFromGpPoint(nwCornerF,self.MaxSearchResolution)

        seCornerF = GpPoint(centerGpPoint.lat - degreesOffset.lat, \
                           centerGpPoint.lon + degreesOffset.lon)
        self.SECornerGridPoint = GpGridPoint()
        self.SECornerGridPoint.InitFromGpPoint(seCornerF,self.MaxSearchResolution)


    def _LimitMaxSearchResolution(self):
        """ Limit the initial (maximum) search resolution so the number of GpGridPoints is < MAX_SEARCH_GP_GRID_POINTS.

        This limits the number of calculations to find the GpGridCell list for the search.
        """
        latCount = self.NWCornerGridPoint.LattitudeInt - self.SWCornerGridPoint.LattitudeInt
        lonCount = self.SWCornerGridPoint.LongitudeInt - self.SECornerGridPoint.LongitudeInt
        resolutionDecrease = 0
        maxResolutionDecrease = MAXIMUM_RESOLUTION - MINIMUM_RESOLUTION
        while latCount*lonCount > self.MAX_SEARCH_GP_GRID_POINTS:
            latCount  >>= 1
            lonCount  >>= 1
            resolutionDecrease += 1
            if resolutionDecrease > maxResolutionDecrease:
                break
        self.MaxSearchResolution = MAXIMUM_RESOLUTION - resolutionDecrease

    def _GetGridPointsWithinRadius(self):
        """ Create a dictionary of GpGridPoints within distanceMeters from a center point.
        
        Scan through the GridPoints in the bounding box region. Add all in-bound points to the dictionary.
        Associate a weight with each GridPoint that is inversely proportional to its distance from the
        center point.
        """
        radiusMeters = self.SearchBoundaryMeters
        self.gpGridPointsInBoundsDic = {}
        stepSize = MAXIMUM_RESOLUTION - self.MaxSearchResolution + 1
        for latInt in range(self.SWCornerGridPoint.LattitudeInt,self.NWCornerGridPoint.LattitudeInt + stepSize, \
                            stepSize):
            for lonInt in range (self.SWCornerGridPoint.LongitudeInt,self.SECornerGridPoint.LongitudeInt + stepSize, \
                                 stepSize):
                gridPoint = GpGridPoint()
                gridPoint.InitFromIntLatLon(latInt,lonInt,self.MaxSearchResolution)
                gpPoint = GpPoint(gridPoint.LattitudeFloat,gridPoint.LongitudeFloat)
                distanceMeters = GpMath.distance(self.CenterGpPoint,gpPoint)
                if distanceMeters <= radiusMeters:
                    weight = self._WeightGridPointByDistance(distanceMeters)
                    self.gpGridPointsInBoundsDic[gridPoint.ToShortString()] = weight

    def _WeightGridPointByDistance(self,distanceMeters):
        """ Create a GridPoint weight that is inversely proportional to its distance from the center point.

            This allows GridCells containing GridPoints close to the center point to be searched at a higher
            priority for a proximity query.
        """
        radiusMeters = self.SearchBoundaryMeters
        if distanceMeters > radiusMeters:
            weight = 0.0
        elif distanceMeters == 0.0:
            weight = MAXIMUM_GRID_POINT_WEIGHT
        else:
            weight = float(radiusMeters) / distanceMeters
            if weight > MAXIMUM_GRID_POINT_WEIGHT:
                weight = MAXIMUM_GRID_POINT_WEIGHT
        return weight
    

    def _GetGridCellsWithinRadius(self):
        """ Create a dictionary of {GpGridCell:(nCornerPointsInBound,inBoundPointsWeight)} for top GpGridCell
            resolution.

        The weight is a measure of the closeness of contained points to the center point"""
        stepSize = MAXIMUM_RESOLUTION - self.MaxSearchResolution + 1
        self.maxResolutionSearchDic = {}
        # Iterate through GridPoints the bounding box
        for latInt in range(self.SWCornerGridPoint.LattitudeInt,self.NWCornerGridPoint.LattitudeInt + stepSize,\
                            stepSize):
            for lonInt in range (self.SWCornerGridPoint.LongitudeInt,self.SECornerGridPoint.LongitudeInt + stepSize,
                             stepSize):
                # Construct a GpGridCell at each GridPoint
                originPoint = GpGridPoint()
                originPoint.InitFromIntLatLon(latInt,lonInt,self.MaxSearchResolution)

                gridCell = GpGridCell()
                gridCell.InitFromGridPoint(originPoint)
                
                cellCornerPoints = gridCell.ListCornerPointsShort()
                nCornerPointsInBound = 0
                inBoundPointsWeight = 0.0
                for cell in cellCornerPoints:
                    if cell in self.gpGridPointsInBoundsDic:
                        nCornerPointsInBound += 1
                        inBoundPointsWeight += self.gpGridPointsInBoundsDic[cell]
                if nCornerPointsInBound > 0:
                    self.maxResolutionSearchDic[gridCell.ToShortString()] = \
                           CellSearchData(nCornerPointsInBound,inBoundPointsWeight)

    def _ReduceSearchCells(self):
        """ Successively reduce the resolution until the number of GpGrid cells in bound is <= MaxSearchCellCount

        Add GpGridSells at each resolution to a dictionary called AllLevelCellSearchDataDic
        AllLevelCellSearchDataDic - contains {resolution: {GpGridCellShortString: [nChildCellsInBound,PerCentInBound]}
        """
        # Initialize the search data dictionary
        self.AllLevelCellSearchDataDic= {self.MaxSearchResolution : self.maxResolutionSearchDic}

        nSearchCells = len(self.maxResolutionSearchDic)
        searchLevelDic = self.maxResolutionSearchDic

        currentSearchResolution = self.MaxSearchResolution
        self.FinalSearchResolution = currentSearchResolution

        while nSearchCells > self.MaxSearchCellCount:
            if currentSearchResolution == MINIMUM_RESOLUTION:
                break
            # Build a parent search dictionary (at next lower level of resolution)
            parentSearchLevelDic = {}
            for gridCellShortStr in searchLevelDic:
                parentCell = GetParentShortGridCellString(gridCellShortStr,currentSearchResolution)
                childCellData = searchLevelDic[gridCellShortStr]

                if parentCell in parentSearchLevelDic:
                    parentCellData = parentSearchLevelDic[parentCell]
                    # Accumulate proximity weights from child cells
                    if childCellData.nChildCellsInBounds > 0:
                        parentCellData.nChildCellsInBounds += 1
                    # Accumulate proximity weights from child cells
                    parentCellData.ProximityWeight += childCellData.ProximityWeight

                else:
                    if childCellData.nChildCellsInBounds > 0:
                        parentSearchLevelDic[parentCell] = CellSearchData(1, childCellData.ProximityWeight)
                    else:
                        parentSearchLevelDic[parentCell] = CellSearchData(0, 0.0)

            nSearchCells = len(parentSearchLevelDic)
            searchLevelDic = parentSearchLevelDic
            currentSearchResolution -= 1
            self.AllLevelCellSearchDataDic[currentSearchResolution] =  parentSearchLevelDic
            self.FinalSearchResolution = currentSearchResolution

        # Create dictionary at final search resolution of {GpCellLongString: CellSearchData}
        self.FinalLevelLongStringSearchDic = {}
        finalLevelDic = self.AllLevelCellSearchDataDic[self.FinalSearchResolution]
        for cell in finalLevelDic:
            cellLong =  GpGridCellShortToLongString(cell,self.FinalSearchResolution)
            self.FinalLevelLongStringSearchDic[cellLong] = finalLevelDic[cell]


    def _SplitSearchCellsToReduceSearchArea(self):
        """ Find GpGridCells in the search list that can be split into higher resolution cells.

        If any GpGridCells in the search list have only 1 child cell that is in bounds, then replace the
        parent cell with the in-bounds child cell. Iterate up the resolution chain until a cell with more
        than one in-bounds child cell is found or the top of the tree is reached.
        """
        # Do a deep copy to save the single level results
        self.MultipleLevelSearchDic = {}
        for cell in self.FinalLevelLongStringSearchDic:
            self.MultipleLevelSearchDic[cell] = self.FinalLevelLongStringSearchDic[cell]
        hasSingleInBoundsChildCells = True
        while hasSingleInBoundsChildCells:
            hasSingleInBoundsChildCells = False
            for cell in self.MultipleLevelSearchDic:
                resolution = GetGridPointResolution(cell)
                # Check to see if top of search tree has been reached
                if resolution ==  self.MaxSearchResolution:
                    break
                searchData =  self.MultipleLevelSearchDic[cell]
                if searchData.nChildCellsInBounds == 1:
                    hasSingleInBoundsChildCells = True
                    self._SplitCell(cell)

        return

    def _SplitCell(self,GpCellLongString):
        # Delete the cell entry from the dictionary
        del self.MultipleLevelSearchDic[GpCellLongString]
        # Get the 4 child cells
        ResolutionAndGpCellShort = GpGridCellLongToShortString(GpCellLongString)
        parentCell = GpGridCell()
        parentCell.InitFromShortCellString(ResolutionAndGpCellShort[1],ResolutionAndGpCellShort[0])
        childCellList = parentCell.ListChildCellsShort()
        childResolution = ResolutionAndGpCellShort[0] + 1
        # Get the search data dictionary at the resolution of the child cells
        childLevelSearchDic = self.AllLevelCellSearchDataDic[childResolution]
        # Check for the cell entry in the All Level Search Data Dic
        for cell in childCellList:
            if cell in childLevelSearchDic:
                cellData = childLevelSearchDic[cell]
                if cellData.nChildCellsInBounds > 0:
                    # Add this cell to the Multiple Level Search Dictionary
                    longCellString = GpGridCellShortToLongString(cell, childResolution)
                    self.MultipleLevelSearchDic[longCellString] = cellData

    def _PrioritizeCellSearchList(self):
        """ Create a list of search geoCells in order of priority based on proximity weights."""

        CellAndWeight = []
        for cell in self.MultipleLevelSearchDic:
            cellSearchData = self.MultipleLevelSearchDic[cell]
            cellAndWeight = cell, cellSearchData.ProximityWeight
            CellAndWeight.append(cellAndWeight)
        sortTuple = SortTupleList(1,True)
        CellAndWeightSorted = sortTuple.doSort(CellAndWeight)
        order = 0
        for cell in CellAndWeightSorted:
            orderAndCell = order,cell[0]
            self.SearchCellList.append(orderAndCell)
            order += 1

class CellSearchData:
    """ Data attached to GpGridCells to support searching
    """
    nChildCellsInBounds = 0
    ProximityWeight = 0.0

    def __init__(self,nChildCells,weight):
        self.nChildCellsInBounds = nChildCells
        self.ProximityWeight = weight


