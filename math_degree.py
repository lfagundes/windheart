import math

"""Same trigonometry functions from math, using degrees instead of radians"""

# function wrappers
def convert(function):
    def new_function(angle):
        return function(angle * math.pi / 180)
    return new_function

def aconvert(arc_function):
    def new_function(result):
        return arc_function(result) * 180 / math.pi
    return new_function

sin = convert(math.sin)
cos = convert(math.cos)
tan = convert(math.tan)
asin = aconvert(math.asin)
acos = aconvert(math.acos)
atan = aconvert(math.atan)
