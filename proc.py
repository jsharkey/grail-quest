
#
# Copyright (C) 2015 Jeff Sharkey, http://jsharkey.org/
# All Rights Reserved.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import sys
import collections
import math, re

# 0270 --> 10


def dist(a, b):
    ax, ay = a
    bx, by = b
    dx = (ax - bx)
    dy = (ay - by)
    return math.sqrt(dx * dx + dy * dy)


def correct(pt):
    paramA,paramB,paramC,paramD = [-0.06, -0.0879, 0, 0]

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

    #print deltaX, deltaY

    dstR = math.sqrt(deltaX * deltaX + deltaY * deltaY)

    #print (paramA * dstR * dstR * dstR + paramB * dstR * dstR + paramC * dstR + paramD)
    srcR = (paramA * dstR * dstR * dstR + paramB * dstR * dstR + paramC * dstR + paramD) - dstR

    # if we already have dst, need to work backwards
    #print dstR, "-->", srcR

    factor = abs(dstR / srcR);
    #print factor

    srcXd = centerX + (deltaX * factor * d);
    srcYd = centerY + (deltaY * factor * d);

    #print x, y, "-->", srcXd, srcYd
    return (srcXd, srcYd)




pts = collections.defaultdict(dict)

"""
for line in sys.stdin:
    if "==" in line:
        pt = line.strip()[3:]
        print "];\nvar set=[",
    
    if "stage" in line:
        x,y,frame = re.split("\s+", line.strip())
        frame = frame[-6:]
        pts[frame][pt] = (int(x),int(y))
        print "[%s,%s]," % (x,y),
        if "0.jpg" in frame: print "\n\t",

print "];"

frames = sorted([ k for k in pts.keys() if len(pts[k]) == 4 ])
"""

print "== STAGE TWO =="

"""
A=[3307,2934,3299,2931,3329,2918,3312,2898,3310,2904,3336,2874,3348,2871,3333,2879,3326,2870,3346,2863,3324,2861,3325,2856,3340,2855,3308,2851,3340,2857,3337,2864,3335,2858,3330,2848,3322,2843,3335,2851,3317,2848,3307,2872,3312,2866,3326,2867,3331,2853,3298,2857,3317,2860,3318,2863,3315,2873,3330,2841,3335,2861,3333,2858,3338,2848,3333,2875,3300,2862,3291,2888,3296,2871,3311,2860,3284,2876,3324,2847,3313,2881,3321,2854,3306,2873,3304,2858,3303,2851,3311,2821,3322,2862,3332,2837,3293,2859,3327,2861,3320,2855,3313,2873,3302,2863,3300,2860,3318,2879,3312,2864,3312,2848,3314,2843,3281,2847,3323,2851,3274,2856,3310,2849,3290,2853,3310,2849,3308,2853,3268,2849,3271,2834,3289,2850,3291,2828,3299,2840,3321,2814,3322,2793,3278,2797,3319,2792,3312,2760,3262,2875,3294,2796]
A=zip(A[::2], A[1::2])
print "var set=", A.__repr__().replace("(", "[").replace(")", "]"), ";"

B=[675,2834,662,2838,705,2831,686,2811,687,2793,731,2763,748,2756,726,2760,715,2764,744,2757,711,2766,717,2740,739,2737,697,2718,739,2734,730,2751,729,2745,730,2707,719,2706,735,2714,712,2701,689,2738,699,2724,721,2711,732,2696,683,2706,711,2702,712,2705,704,2721,735,2675,737,2698,736,2689,744,2683,732,2706,689,2689,670,2713,679,2704,702,2696,663,2698,727,2665,700,2711,725,2655,698,2678,701,2657,703,2641,715,2626,724,2660,747,2620,685,2651,733,2651,727,2632,713,2652,696,2653,693,2651,718,2655,714,2636,719,2614,725,2600,676,2609,735,2610,660,2627,718,2598,687,2607,720,2591,713,2605,655,2606,664,2582,693,2576,699,2556,710,2559,744,2539,748,2521,686,2524,748,2507,742,2481,663,2549,712,2510,710,2660]
B=zip(B[::2], B[1::2])
print "var set=", B.__repr__().replace("(", "[").replace(")", "]"), ";"

for i in range(len(A)):
    frame = "%02d.jpg" % (i)
    pts[frame]['A'] = A[i]
    pts[frame]['B'] = B[i]

frames = sorted([ k for k in pts.keys() if len(pts[k]) == 2 ])
"""

A={}
for line in open("../best1.txt"):
    i,j,x,y = line.split(" ")
    A[int(j)] = (int(x),int(y))

B={}
for line in open("../best2.txt"):
    i,j,x,y = line.split(" ")
    B[int(j)] = (int(x),int(y))


#A=[ for x in ]


# 1048,2681
# 2964,2780
"""
x1 = 1048; y1 = 2681
x2 = 2964; y2 = 2780

fx, fy = correct( (1048,2681) )
#fx, fy = (1048,2681)

defang = math.atan2(y2-y1, x2-x1) * 180 / math.pi
"""

f ="""
5305    1182    file:///home/jsharkey/grail-quest/rt00.jpg
5249    1280    file:///home/jsharkey/grail-quest/rt10.jpg
5220    1307    file:///home/jsharkey/grail-quest/rt20.jpg
5176    1301    file:///home/jsharkey/grail-quest/rt30.jpg
5225    1272    file:///home/jsharkey/grail-quest/rt40.jpg
5162    1324    file:///home/jsharkey/grail-quest/rt50.jpg
5257    1311    file:///home/jsharkey/grail-quest/rt60.jpg
5116    1389    file:///home/jsharkey/grail-quest/rt70.jpg
"""

f ="""
3746    982 file:///home/jsharkey/grail-quest/rt05.jpg
3743    992 file:///home/jsharkey/grail-quest/rt15.jpg
3769    1005    file:///home/jsharkey/grail-quest/rt25.jpg
3769    974 file:///home/jsharkey/grail-quest/rt35.jpg
3733    1058    file:///home/jsharkey/grail-quest/rt45.jpg
3724    1018    file:///home/jsharkey/grail-quest/rt55.jpg
3764    1030    file:///home/jsharkey/grail-quest/rt65.jpg
3739    1019    file:///home/jsharkey/grail-quest/rt75.jpg
"""

f = """
3215    972 file:///bandroid/lapse/100EOS5D/grail-quest/rt05.jpg
3215    984 file:///bandroid/lapse/100EOS5D/grail-quest/rt15.jpg
3239    998 file:///bandroid/lapse/100EOS5D/grail-quest/rt25.jpg
3237    966 file:///bandroid/lapse/100EOS5D/grail-quest/rt35.jpg
3208    1049    file:///bandroid/lapse/100EOS5D/grail-quest/rt45.jpg
3197    1008    file:///bandroid/lapse/100EOS5D/grail-quest/rt55.jpg
3236    1024    file:///bandroid/lapse/100EOS5D/grail-quest/rt65.jpg
3211    1010    file:///bandroid/lapse/100EOS5D/grail-quest/rt75.jpg
"""

shift = {}

defang = 1024

"""
for line in f.split("\n"):
    if len(line) < 5: continue

    x, y, name = re.split(r"\s+", line)
    x = int(x)
    y = int(y)

    name = name.strip()
    name = name[-6:]
    
    shift[name] = (x,y)
    
    x -= 3204; y -= 1005;
    print "convert rt%s -virtual-pixel black -distort ScaleRotateTranslate '0,0 1,1 0 %d,%d' xrt%s.jpg" % (name, -x, -y, name)
"""

def rot(p, ang):
    
    x,y=p
    print x,y, "--> ", ang,
    
    ang *= 0.0174532925
    width=5760
    height=3840

    x-=width/2
    y-=height/2

    xx = (x*math.cos(ang)) - (y*math.sin(ang))
    yy = (y*math.cos(ang)) + (x*math.sin(ang))
    
    xx+=width/2
    yy+=height/2
    
    """
    d = min(width, height) / 2
    centerX = (width) / 2.0
    centerY = (height) / 2.0
    deltaX = (x - centerX) / d
    deltaY = (y - centerY) / d

    xx = (deltaX*math.cos(ang)) - (deltaY*math.sin(ang))
    yy = (deltaY*math.cos(ang)) + (deltaX*math.sin(ang))

    xx = centerX + (xx * d);
    yy = centerY + (yy * d);
    """

    print "-->",  xx, yy
    return (xx,yy)



for j in range(1,760):
    x1, y1 = A[j]
    x2, y2 = B[j]
    
    # always correct first
    x1, y1 = correct( (x1,y1) )
    x2, y2 = correct( (x2,y2) )

    #print dist( (x1,y1), (x2,y2) )

    #print x1,y1
    #print "----"
    
    ang = math.atan2(y2-y1, x2-x1) * 180 / math.pi

    #xd = x1; yd = y1

    if defang == 1024:
        defang = ang
        fx = x1; fy = y1
    ang -= defang

    x1,y1 = rot((x1,y1),-ang)

    xd = 0; yd = 0
    xd = x1 - fx; yd = y1 - fy

    #x1 -= 1048; y1 -= 2681
    #x2 -= 2964; y2 -= 2780

    #ang = 0
    #ang += -2.71

    with open("proc%04d.pp3" % (j), 'w') as f:
        f.write("""
[Version]
AppVersion=4.2.242
Version=324

[Coarse Transformation]
Rotate=0
HorizontalFlip=true
VerticalFlip=true

[Common Properties for Transformations]
AutoFill=false

[Rotation]
Degree=%f
xshift=%f
yshift=%f

[Distortion]
Amount=0

[LensProfile]
LCPFile=../guess.lcp
UseDistortion=true
UseVignette=false
UseCA=false

""" % (ang, -xd, -yd))

    #orig = (int(p[0:2])+17)*10
    i=j+170
    print "~/rt_default_release_patched/rawtherapee -p ../pass1.pp3 -p proc%04d.pp3 -Y -o proc%04d.jpg -c /bandroid/lapse2/DCIM/101EOS5D/R59A%04d.CR2 " % (j,j,i)
    #print """convert %s -virtual-pixel black -distort ScaleRotateTranslate '%d,%d 1,1 %f 1048,2681' -rotate 180 %s.post.jpg &""" % (p, x1, y1, ang, p)
