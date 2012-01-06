""" Copyright (c) 2011 FriendzyShop, LLC. All rights reserved """

__author__ = 'Brian Sargent'

from GlobalPositionLib import MAXIMUM_RESOLUTION

def GetLattitudeResolution(resolution):
    return resolution

def GetLongitudeResolution(resolution):
    return resolution + 1

def GetParentShortGridCellString(GpGridCellShortString, childResolution):
    """ Return the short string representation of the parent (bounding cell)

        args:
            GpGridCellShortString: short string representation of a GpGridCell
            childResolution: resolution of the child cell (number of bits)
    """
    parentResolution = childResolution - 1
    args = GpGridCellShortString.rsplit('_')
    lattitudeInt = int(args[0],16) >> 1
    longitudeInt = int(args[1],16) >> 1
    return ToShortGpGridPointString(lattitudeInt,longitudeInt,parentResolution)

def GetGridPointResolution(GpGridPointLongString):
    """ Return the integer resolution of a GpGridPoint or GpGridCell from a long string representation."""
    args = GpGridPointLongString.rsplit('_')
    resolution = int(args[0],16)
    return resolution

def ToShortGpGridPointString(scaledLattitudeInt,scaledLongitudeInt,resolution):
    latHexString = ToNBitHexString(scaledLattitudeInt,resolution)
    lonHexString = ToNBitHexString(scaledLongitudeInt,resolution + 1)
    shortCellString = latHexString + "_" + lonHexString
    return shortCellString

def ToLongGpGridPointString(LattitudeInt,LongitudeInt,resolution):
    latHexString = ToNBitHexString(LattitudeInt,GetLattitudeResolution(resolution))
    lonHexString = ToNBitHexString(LongitudeInt,GetLongitudeResolution(resolution))
    resString = '%x' % resolution
    longCellString = resString + '_' + latHexString + '_' + lonHexString
    return longCellString

def GpGridCellShortToLongString(GpGridCellShortString, resolution):
    args =  GpGridCellShortString.rsplit('_')
    shift = MAXIMUM_RESOLUTION - resolution
    lattitudeInt = int(args[0],16) << shift
    longitudeInt = int(args[1],16) << shift
    return ToLongGpGridPointString(lattitudeInt,longitudeInt, resolution)

def GpGridCellLongToShortString(GpGridCellLongString):
    """ Return a tuple of (resolution,GpGridCellShortString) converted from a GpGridCellLongString)"""
    
    args =  GpGridCellLongString.rsplit('_')
    resolution = int(args[0],16)
    shift = MAXIMUM_RESOLUTION - resolution
    lattitudeInt = int(args[1],16) >> shift
    longitudeInt = int(args[2],16) >> shift
    return resolution, ToShortGpGridPointString(lattitudeInt,longitudeInt,resolution)

def ToNBitHexString(intValue,nBits):
    """ Convert an integer to a hexadecimal string with a specified number of bits.

    args:
        intValue - integer where 0 <= intValue < 2**nBits
        nBits - Number of bits in the integer. Hex string is zero padded to
                (nBits/4) rounded up hex digits.
    """
    digits  = int(nBits /4)
    # Round up
    modulus = nBits % 4
    if modulus != 0:
        digits += 1
    formatString = "%0."
    formatString += '%dx' % digits
    hexString = formatString % intValue
    return hexString

def IsGpCellXBoundedByGpCellY(gpCellXLongStr,gpCellYLongStr):
    """ Determine if GpCellX is bounded by GpCellY

    Args:
            GpCellX - GpCell X in long string form
            GpCellY - GpCell Y in long string form
    Return:
            True if GpCell X is bounded by GpCell Y (or if the two cells are identical)
            False if GpCel X is not bounded by GpCell Y
    """
    if gpCellXLongStr == gpCellYLongStr:
        return True

    XResolution = GetGridPointResolution(gpCellXLongStr)
    YResolution = GetGridPointResolution(gpCellYLongStr)

    if XResolution >= YResolution:
        # Cannot be bounded with equal resolution and unequal gpCells
        return False

    (xResolution, xShortString) = GpGridCellLongToShortString(gpCellXLongStr)
    while xResolution < YResolution:
        # Increase X resolution until it matches the Y resolution
        xShortString = GetParentShortGridCellString(xShortString, xResolution)
        # resolution of the parent cell
        xResolution += 1
  
    xBoundingGpCellLongStr = GpGridCellShortToLongString(xShortString, xResolution)
    if xBoundingGpCellLongStr == gpCellYLongStr:
        return True
    else:
        return False