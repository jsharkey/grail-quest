

# range 

"""

============================ GUESSES

guess = 0.14775168
guess = 0.153821225
guess = 0.055939325
guess = 0.142723725





early was 180
mid was 520
late was 830







for two given exact same points, the *distance* should be the same, but not necessarily the angle







"""


#rad = 0.016578*(0.8*0.8)


#sqrt((5760*0.8)^2 + (3840*0.8)^2)
#rad = 5538.12675911

import math, sys, collections


def dist(a, b):
    ax, ay = a
    bx, by = b
    dx = (ax - bx)
    dy = (ay - by)
    return math.sqrt(dx * dx + dy * dy)

def correct(paramA, pt):
    paramB=0
    paramC=0
    paramD=0

    width=5760
    height=3840
    x,y = pt
    #x=width*1
    #y=height*0.5

    d = min(width, height) / 2

    centerX = (width) / 2.0
    centerY = (height) / 2.0

    deltaX = (x - centerX) / d
    deltaY = (y - centerY) / d

    print deltaX, deltaY

    dstR = math.sqrt(deltaX * deltaX + deltaY * deltaY)

    #print (paramA * dstR * dstR * dstR + paramB * dstR * dstR + paramC * dstR + paramD)
    srcR = (paramA * dstR * dstR * dstR + paramB * dstR * dstR + paramC * dstR + paramD) - dstR

    # if we already have dst, need to work backwards
    print dstR, "-->", srcR

    factor = abs(dstR / srcR);
    print factor

    srcXd = centerX + (deltaX * factor * d);
    srcYd = centerY + (deltaY * factor * d);

    #print x, y, "-->", srcXd, srcYd
    return (srcXd, srcYd)


"""
early1 = (3219,2864)
early2 = (2510,2907)
mid1 = (3212,2821)
mid2 = (2506,2841)
late1 = (3195,2764)
late2 = (2491,2762)
guess = 0.14775168
jump = 0.1
"""

"""
early1 = (2136,2790)
early2 = (3281,2695)
late1 = (2131,2627)
late2 = (3269,2602)
guess = 0.153821225
jump = 0.0000001
"""

"""
early1 = (736,2763)
early2 = (2931,2606)
late1 = (742,2513)
late2 = (2928,2494)
guess = 0.055939325
jump = 0.000001
"""

"""
early1 = (3330,2899)
early2 = (2029,2898)
late1 = (3303,2805)
late2 = (2017,2726)
guess = 0.142723725
jump = 0.0000001
"""


pts = collections.defaultdict(list)

for line in sys.stdin:
    if len(line) < 5: continue

    x, y, name = line.split("\t")
    x = int(x)
    y = int(y)

    name = name.strip()
    name = name[-6:]
    
    pts[name].append((x,y))

"""
import numpy

paramA = 0.107
delta = 0.000001
best = 1024
while paramA < 1:
    paramA += delta

    calc_dist = []
    for name in pts.keys():
        a, b = pts[name]
        a = correct(-paramA, a)
        b = correct(-paramA, b)
        calc_dist.append(dist(a, b))

    # looking to minimize stddev
    dev = numpy.std(calc_dist)
    if dev < best:
        best = dev
        #print calc_dist
        print "paramA=%0.8f, dev=%0.8f" % (paramA, dev)
"""

# 10.jpg --> 270

def round(p):
    x,y=p
    return (int(x),int(y))

paramA = 0.10705000
for name in sorted(pts.keys()):
    a, b = pts[name]
    print name
    ax = correct(-paramA, a)
    bx = correct(-paramA, b)
    print "\t", a, "-->", round(ax)
    print "\t", b, "-->", round(bx)

# BEST FIT: paramA=0.10705000, dev=1.42170719




"""
paramA = guess-jump
while paramA < guess+jump:

    e1 = correct(-paramA, early1)
    e2 = correct(-paramA, early2)
    m1 = correct(-paramA, mid1)
    m2 = correct(-paramA, mid2)
    l1 = correct(-paramA, late1)
    l2 = correct(-paramA, late2)
    
    ed = dist(e1, e2)
    md = dist(m1, m2)
    ld = dist(l1, l2)
    
    print paramA, ed, md, ld, (ed-md), (ed-ld) 

    paramA += jump/20




print correct((0,0))
"""



"""

                  <stCamera:FocalLength>14.000000</stCamera:FocalLength>
                  <stCamera:ApertureValue>6.918863</stCamera:ApertureValue>
                     <stCamera:ImageXCenter>0.500064</stCamera:ImageXCenter>
                     <stCamera:ImageYCenter>0.516091</stCamera:ImageYCenter>
                     <stCamera:RadialDistortParam1>-0.016578</stCamera:RadialDistortParam1>

                  <stCamera:FocalLength>18.000000</stCamera:FocalLength>
                  <stCamera:ApertureValue>6.918863</stCamera:ApertureValue>
                     <stCamera:ImageXCenter>0.502970</stCamera:ImageXCenter>
                     <stCamera:ImageYCenter>0.504482</stCamera:ImageYCenter>
                     <stCamera:RadialDistortParam1>-0.005184</stCamera:RadialDistortParam1>


                  <stCamera:FocalLength>24.000000</stCamera:FocalLength>
                  <stCamera:ApertureValue>6.918863</stCamera:ApertureValue>
                     <stCamera:ImageXCenter>0.504516</stCamera:ImageXCenter>
                     <stCamera:ImageYCenter>0.538311</stCamera:ImageYCenter>
                     <stCamera:RadialDistortParam1>-0.000279</stCamera:RadialDistortParam1>
"""

