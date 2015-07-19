
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

"""
for line in sys.stdin:
    if "==" in line:
        pt = line.strip()[3:]
    
    if "stage" in line:
        x,y,frame = re.split("\s+", line.strip())
        frame = frame[-6:]
        pts[frame][pt] = (int(x),int(y))

"""

A=[3307,2934,3299,2931,3329,2918,3312,2898,3310,2904,3336,2874,3348,2871,3333,2879,3326,2870,3346,2863,3324,2861,3325,2856,3340,2855,3308,2851,3340,2857,3337,2864,3335,2858,3330,2848,3322,2843,3335,2851,3317,2848,3307,2872,3312,2866,3326,2867,3331,2853,3298,2857,3317,2860,3318,2863,3315,2873,3330,2841,3335,2861,3333,2858,3338,2848,3333,2875,3300,2862,3291,2888,3296,2871,3311,2860,3284,2876,3324,2847,3313,2881,3321,2854,3306,2873,3304,2858,3303,2851,3311,2821,3322,2862,3332,2837,3293,2859,3327,2861,3320,2855,3313,2873,3302,2863,3300,2860,3318,2879,3312,2864,3312,2848,3314,2843,3281,2847,3323,2851,3274,2856,3310,2849,3290,2853,3310,2849,3308,2853,3268,2849,3271,2834,3289,2850,3291,2828,3299,2840,3321,2814,3322,2793,3278,2797,3319,2792,3312,2760,3262,2875,3294,2796]
A=zip(A[::2], A[1::2])
B=[675,2834,662,2838,705,2831,686,2811,687,2793,731,2763,748,2756,726,2760,715,2764,744,2757,711,2766,717,2740,739,2737,697,2718,739,2734,730,2751,729,2745,730,2707,719,2706,735,2714,712,2701,689,2738,699,2724,721,2711,732,2696,683,2706,711,2702,712,2705,704,2721,735,2675,737,2698,736,2689,744,2683,732,2706,689,2689,670,2713,679,2704,702,2696,663,2698,727,2665,700,2711,725,2655,698,2678,701,2657,703,2641,715,2626,724,2660,747,2620,685,2651,733,2651,727,2632,713,2652,696,2653,693,2651,718,2655,714,2636,719,2614,725,2600,676,2609,735,2610,660,2627,718,2598,687,2607,720,2591,713,2605,655,2606,664,2582,693,2576,699,2556,710,2559,744,2539,748,2521,686,2524,748,2507,742,2481,663,2549,712,2510,710,2660]
B=zip(B[::2], B[1::2])

for i in range(len(A)):
    frame = "%02d.jpg" % (i)
    pts[frame]['A'] = A[i]
    pts[frame]['B'] = B[i]

frames = sorted([ k for k in pts.keys() if len(pts[k]) == 2 ])

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
    srcR = ((paramA * math.pow(dstR, 3)) + (paramB * math.pow(dstR, 2)) + (paramC * math.pow(dstR, 1)) + (paramD)) - dstR

    factor = abs(dstR / srcR);

    srcXd = centerX + (deltaX * factor * d);
    srcYd = centerY + (deltaY * factor * d);

    return (srcXd, srcYd)

def correct2(params, pt):
    paramA,paramB,paramC,paramD=params
    paramA=-paramA
    paramB=-paramB

    width=5760
    height=3840
    x,y = pt

    d = min(width, height) / 2

    centerX = (width) / 2.0
    centerY = (height) / 2.0

    deltaX = (x - centerX) / d
    deltaY = (y - centerY) / d

    dstR = math.sqrt(deltaX * deltaX + deltaY * deltaY)
    srcR = ((paramA * math.pow(dstR, 3)) + (paramB * math.pow(dstR, 2)) + (paramC * math.pow(dstR, 1)) + (paramD)) - dstR

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

def round_int(a):
    x,y=a
    return (int(x),int(y))


def guess(params):
    res = collections.defaultdict(list)
    for frame in frames:
        pt = pts[frame]
        # C is down in another plane
        # B is far off on right side
        res['AB'].append(correct_dist(params, pt['A'], pt['B']))
        #res['AC'].append(correct_dist(params, pt['A'], pt['C']))
        #res['AD'].append(correct_dist(params, pt['A'], pt['D']))
        #res['BC'].append(correct_dist(params, pt['B'], pt['C']))
        #res['BD'].append(correct_dist(params, pt['B'], pt['D']))
        #res['CD'].append(correct_dist(params, pt['C'], pt['D']))
    #if max(res['AB']) < 1400: raise ValueError()
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



# ========================= r3, r2, r

#params = [-0.1164, -0.0739, -0.6689, 0.0168]
#params = [-0.06, -0.0879, 0, 0]
#params = [-0.0467, -0.1192, 0, 0]

#[0, 0, 0, 0] [10.061564166358261]  <-- worst case

#[-0.09256000000000145, 0, 0, 0] [2.6666136482583762]
#[-0.09256000000000145, -0.0013900000000046336, 0, 0] [2.666179691339674]
#[-0.09198000000000167, -0.0013900000000046336, 0, 0] [2.6657489091518998]
#[-0.09198, -0.00275, 0, 0] [2.6653302961767009]

params = [-0.09198, -0.00275, 0, 0]

a = (3336,2874)
b = round_int(correct(params,a))
c = round_int(correct2(params,b))

print a
print b
print c



exit()

index = 0
while True:
    params = search(params, index)
    index = (index + 1) % 2
    print "== BEST SO FAR", params






















