""" Copyright (c) 2011 FriendzyShop, LLC. All rights reserved """

import logging
import math
from GpPointClass import GpPoint

__author__ = 'Brian Sargent'


RADIUS_OF_EARTH_METERS = 6378135.0
MILES_PER_METER =  0.000621371192
METERS_PER_MILE =  1609.344


def distance(p1, p2):
  """Calculates the great circle distance between two points (law of cosines).

  Args:
    p1: A gpTypes.gpGridPoint indicating the first point.
    p2: A gpTypes.gpGridPoint indicating the second point.

  Returns:
    The 2D great-circle distance between the two given points, in meters.
  """
  p1lat, p1lon = math.radians(p1.lat), math.radians(p1.lon)
  p2lat, p2lon = math.radians(p2.lat), math.radians(p2.lon)
  return RADIUS_OF_EARTH_METERS * math.acos(math.sin(p1lat) * math.sin(p2lat) +
      math.cos(p1lat) * math.cos(p2lat) * math.cos(p2lon - p1lon))


def distanceMetersToDegrees(centerPoint, distanceMeters):
    """ Calculate the offsets in degrees from the centerPoint corresponding to distanceMeters

    Args:
    centerPoint: (lattitude, longitude) GpPoint
    distanceMeters: Distance in meters

    Returns:
    (DeltaLattitude, DeltaLongitude) tuple in degrees. DeltaLattitude is the change in lattitude
    corresponding to distanceMeters. DeltaLongitude is change in longitude along the centerPoint
    lattitude line corresponding to distanceMeters.
    """
    plat = math.radians(centerPoint.lat)
    radiansLongitude = distanceMeters/(float(RADIUS_OF_EARTH_METERS) * math.cos(plat))
    radiansLattitude = distanceMeters / float(RADIUS_OF_EARTH_METERS)
    offsets=GpPoint(math.degrees(radiansLattitude), math.degrees(radiansLongitude))
    return offsets

def distanceMilesToDegrees(centerPoint, distanceMiles):
    meters = milesToMeters(distanceMiles)
    return distanceMetersToDegrees(centerPoint,meters)

def metersToMiles(meters):
    return meters * MILES_PER_METER

def milesToMeters(miles):
    return miles * METERS_PER_MILE
