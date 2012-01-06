#Define Global constants
MAXIMUM_RESOLUTION = 16
MINIMUM_RESOLUTION = 8

TO_INT_SCALE =  float(1 << MAXIMUM_RESOLUTION) /180.0
TO_FLOAT_SCALE = 180.0 / float(1 << MAXIMUM_RESOLUTION)

# Direction vectors in lattitude, longitude grid coordinate changes
DIRECTION_VECTORS = {'NW':(1,-1), 'N':(1,0), 'NE': (1, 1) ,'E':(0,1),
                     'SW':(-1,-1),'S':(-1,0),'SE': (-1,-1),'W':(0,-1)}