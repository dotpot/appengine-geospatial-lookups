""" Copyright (c) 2011 FriendzyShop, LLC. All rights reserved """

__author__ = 'Brian Sargent'


class GpPoint(object):
  """A two-dimensional point in the [-90,90] x [-180,180] lat/lon space.

  Attributes:
    lat: A float in the range [-90,90] indicating the point's latitude.
    lon: A float in the range [-180,180] indicating the point's longitude.
  """

  def __init__(self, lattitude, longitude):
    """Initializes a point with the given latitude and longitude."""
    latF = float(lattitude)
    lonF = float(longitude)

    if -90 > latF or latF > 90:
      raise ValueError("Latitude must be in [-90, 90] but was %f" % latF)
    if -180 > lonF or lonF > 180:
      raise ValueError("Longitude must be in [-180, 180] but was %f" % lonF)

    self.lat = latF
    self.lon = lonF

  def __eq__(self, other):
    return self.lat == other.lat and self.lon == other.lon

  def __str__(self):
    return '(%f, %f)' % (self.lat, self.lon)

