
import sys
import collections
import math

BEST_GUESS = 0.14775168

# python /bandroid/lapse/100EOS5D/grail-quest/proc.py </bandroid/lapse/100EOS5D/grail-quest/res2.txt  |sort
# avconv -r 10  -i "%02d.jpg.post.jpg" out2.mp4

def correct(paramA, pt):
    paramB=0
    paramC=0
    paramD=0

    width=5760
    height=3840
    x,y = pt

    d = min(width, height) / 2

    centerX = (width) / 2.0
    centerY = (height) / 2.0

    deltaX = (x - centerX) / d
    deltaY = (y - centerY) / d

    dstR = math.sqrt(deltaX * deltaX + deltaY * deltaY)
    srcR = (paramA * dstR * dstR * dstR + paramB * dstR * dstR + paramC * dstR + paramD) - dstR

    factor = abs(dstR / srcR);

    srcXd = centerX + (deltaX * factor * d);
    srcYd = centerY + (deltaY * factor * d);

    return (srcXd, srcYd)





pts = collections.defaultdict(list)

for line in sys.stdin:
    if len(line) < 5: continue

    x, y, name = line.split("\t")
    x = int(x)
    y = int(y)
    
    x2,y2 = correct(BEST_GUESS, (x,y))
    print "%d,%d -> %d,%d" % (x,y,x2,y2)

    name = name.strip()
    name = name[-6:]
    
    pts[name].append((x2,y2))


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

    print """rawtherapee -o %s.distort.jpg -p distort.pp3 -c %s &""" % (p, p)
    print """convert %s -virtual-pixel black -distort ScaleRotateTranslate '%d,%d 1,1 %f 1048,2681' -rotate 180 %s.post.jpg &""" % (p, x1, y1, ang, p)
