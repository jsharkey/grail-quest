
import sys
import collections
import math

# 0270 --> 10


def dist(a, b):
    ax, ay = a
    bx, by = b
    dx = (ax - bx)
    dy = (ay - by)
    return math.sqrt(dx * dx + dy * dy)


def correct(pt):
    paramA=-0.10705000
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




pts = collections.defaultdict(list)

for line in sys.stdin:
    if len(line) < 5: continue

    x, y, name = line.split("\t")
    x = int(x)
    y = int(y)

    name = name.strip()
    name = name[-6:]
    
    pts[name].append((x,y))


# we have points that should always be at same location


# 1048,2681
# 2964,2780

x1 = 1048; y1 = 2681
x2 = 2964; y2 = 2780

fx, fy = correct( (1048,2681) )
#fx, fy = (1048,2681)

defang = math.atan2(y2-y1, x2-x1) * 180 / math.pi


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

shift = {}

import re

for line in f.split("\n"):
    if len(line) < 5: continue

    x, y, name = re.split(r"\s+", line)
    x = int(x)
    y = int(y)

    name = name.strip()
    name = name[-6:]
    
    shift[name] = (x,y)
    
    x -= 3744; y -= 982;
    print """convert rt%s -virtual-pixel black -distort ScaleRotateTranslate '0,0 1,1 0 %d,%d' xrt%s.jpg""" % (name, -x, -y, name)

for p in sorted(pts):
    if not p.endswith("jpg"): continue

    #print p

    x1, y1 = pts[p][0]
    x2, y2 = pts[p][1]
    
    #print x1,y1

    
    # always correct first
    x1, y1 = correct( (x1,y1) )
    x2, y2 = correct( (x2,y2) )

    #print dist( (x1,y1), (x2,y2) )

    #print x1,y1
    #print "----"
    
    ang = math.atan2(y2-y1, x2-x1) * 180 / math.pi

    #xd = x1; yd = y1

    #xd = x1 - fx; yd = y1 - fy
    xd = 0; yd = 0
    
    if p in shift:
        xd,yd = shift[p]
        xd -= 3744; yd -= 982;

    xd = 0; yd = 0

    #x1 -= 1048; y1 -= 2681
    #x2 -= 2964; y2 -= 2780

    ang -= defang
    ang += -2.71

    with open("proc%s.pp3" % (p), 'w') as f:
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
LCPFile=/home/jsharkey/grail-quest/guess.lcp
UseDistortion=true
UseVignette=false
UseCA=false

""" % (ang, -xd, -yd))

    orig = (int(p[0:2])+17)*10
    print "~/rt_default_release_patched/rawtherapee -p proc%s.pp3 -Y -o rt%s -c ~/vacat/DCIM/101EOS5D/R59A%04d.CR2" % (p, p, orig)
    #print """convert %s -virtual-pixel black -distort ScaleRotateTranslate '%d,%d 1,1 %f 1048,2681' -rotate 180 %s.post.jpg &""" % (p, x1, y1, ang, p)
