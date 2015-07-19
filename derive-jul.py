
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

import sys, re, collections, math, numpy

pts = collections.defaultdict(dict)

for line in sys.stdin:
    if "==" in line:
        pt = line.strip()[3:]
    
    if "stage" in line:
        x,y,frame = re.split("\s+", line.strip())
        frame = frame[-6:]
        pts[frame][pt] = (int(x),int(y))

frames = sorted([ k for k in pts.keys() if len(pts[k]) == 4 ])

def correct(params, pt):
    paramA,paramB,paramC,paramD=params

    width=5760
    height=3840
    x,y = pt

    d = min(width, height) / 2

    centerX = (width) / 2.0
    centerY = (height) / 2.0

    deltaX = (x - centerX) / d
    deltaY = (y - centerY) / d

    dstR = math.sqrt(deltaX * deltaX + deltaY * deltaY)
    srcR = ((paramA * dstR * dstR * dstR) + (paramB * dstR * dstR) + (paramC * dstR) + (paramD)) - dstR

    factor = abs(dstR / srcR);

    srcXd = centerX + (deltaX * factor * d);
    srcYd = centerY + (deltaY * factor * d);

    return (srcXd, srcYd)

def dist(a, b):
    ax,ay = a
    bx,by = b
    return math.sqrt(math.pow(bx-ax,2) + math.pow(by-ay,2))

def correct_dist(params, a, b):
    return dist(correct(params, a), correct(params, b))

def guess(params):
    res = collections.defaultdict(list)
    for frame in frames:
        pt = pts[frame]
        res['AB'].append(correct_dist(params, pt['A'], pt['B']))
        #res['AC'].append(correct_dist(params, pt['A'], pt['C']))
        res['AD'].append(correct_dist(params, pt['A'], pt['D']))
        #res['BC'].append(correct_dist(params, pt['B'], pt['C']))
        res['BD'].append(correct_dist(params, pt['B'], pt['D']))
        #res['CD'].append(correct_dist(params, pt['C'], pt['D']))
    if max(res['AB']) < 1400: raise ValueError()
    #print min(res['AB']), max(res['AB'])
    return [ numpy.std(res[k]) for k in sorted(res) ]



# within each frame, we know that all points should be equadistant on a flat plane

def search(params, index):
    var = 0.05
    best_res = 1024
    best_params = params
    while var > -0.8:
        var -= 0.0001
        params[index] = var
        #params = [-0.094,var,0,0]
        # -0.094,-0.047
        # -0.075,-0.091
        # -0.057,-0.133

        try:
            dev = guess(params)
            res = sum(dev)
            if res < best_res:
                best_params = list(params)
                best_res = res
                print params, dev
        except:
            continue
    return best_params



params = [-0.1164, -0.0739, -0.6689, 0.0168]
index = 0
while True:
    params = search(params, index)
    index = (index + 1) % 4
    print "== BEST SO FAR", params






















