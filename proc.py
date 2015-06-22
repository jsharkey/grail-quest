
import sys
import collections
import math

pts = collections.defaultdict(list)

for line in sys.stdin:
    if len(line) < 5: continue

    x, y, name = line.split("\t")
    x = int(x)
    y = int(y)

    name = name.strip()
    name = name[-6:]
    
    pts[name].append((x,y))


# 1048,2681
# 2964,2780

x1 = 1048; y1 = 2681
x2 = 2964; y2 = 2780

defang = math.atan2(y2-y1, x2-x1) * 180 / math.pi

for p in pts:
    if not p.endswith("jpg"): continue

    x1, y1 = pts[p][0]
    x2, y2 = pts[p][1]
    
    ang = math.atan2(y2-y1, x2-x1) * 180 / math.pi

    xd = x1 - 1048; yd = y1 - 2681
    #xd = x1; yd = y1

    #x1 -= 1048; y1 -= 2681
    #x2 -= 2964; y2 -= 2780

    ang -= defang
    ang = -ang

    print """convert %s -virtual-pixel black -distort ScaleRotateTranslate '%d,%d 1,1 %f 1048,2681' -rotate 180 %s.post.jpg &""" % (p, x1, y1, ang, p)
