#!/usr/bin/env python

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


import numpy as np
import cv, cv2
#import video
#from common import anorm2, draw_str
from time import clock
import time
import math

A=[3307,2934,3299,2931,3329,2918,3312,2898,3310,2904,3336,2874,3348,2871,3333,2879,3326,2870,3346,2863,3324,2861,3325,2856,3340,2855,3308,2851,3340,2857,3337,2864,3335,2858,3330,2848,3322,2843,3335,2851,3317,2848,3307,2872,3312,2866,3326,2867,3331,2853,3298,2857,3317,2860,3318,2863,3315,2873,3330,2841,3335,2861,3333,2858,3338,2848,3333,2875,3300,2862,3291,2888,3296,2871,3311,2860,3284,2876,3324,2847,3313,2881,3321,2854,3306,2873,3304,2858,3303,2851,3311,2821,3322,2862,3332,2837,3293,2859,3327,2861,3320,2855,3313,2873,3302,2863,3300,2860,3318,2879,3312,2864,3312,2848,3314,2843,3281,2847,3323,2851,3274,2856,3310,2849,3290,2853,3310,2849,3308,2853,3268,2849,3271,2834,3289,2850,3291,2828,3299,2840,3321,2814,3322,2793,3278,2797,3319,2792,3312,2760,3262,2875,3294,2796]
A=zip(A[::2], A[1::2])

B=[675,2834,662,2838,705,2831,686,2811,687,2793,731,2763,748,2756,726,2760,715,2764,744,2757,711,2766,717,2740,739,2737,697,2718,739,2734,730,2751,729,2745,730,2707,719,2706,735,2714,712,2701,689,2738,699,2724,721,2711,732,2696,683,2706,711,2702,712,2705,704,2721,735,2675,737,2698,736,2689,744,2683,732,2706,689,2689,670,2713,679,2704,702,2696,663,2698,727,2665,700,2711,725,2655,698,2678,701,2657,703,2641,715,2626,724,2660,747,2620,685,2651,733,2651,727,2632,713,2652,696,2653,693,2651,718,2655,714,2636,719,2614,725,2600,676,2609,735,2610,660,2627,718,2598,687,2607,720,2591,713,2605,655,2606,664,2582,693,2576,699,2556,710,2559,744,2539,748,2521,686,2524,748,2507,742,2481,663,2549,712,2510,710,2660]
B=zip(B[::2], B[1::2])

knownA = {}
knownB = {}
for i in range(len(A)):
    knownA[i*10] = A[i]
    knownB[i*10] = B[i]

knownA[483-170] = (3307,2858)
knownA[509-170] = (3309,2860)
knownA[587-170] = (3307,2847)
knownA[757-170] = (3311,2862)
knownA[893-170] = (3263,2786)

knownA[357-170] = (3324,2856)
knownA[549-170] = (3285,2858)
knownA[840-170] = (3304,2850)

knownB[322-170] = (729,2743)
knownB[355-170] = (716,2730)
knownB[387-170] = (702,2712)
knownB[449-170] = (685,2713)
knownB[602-170] = (659,2654)
knownB[679-170] = (715,2644)
knownB[734-170] = (716,2618)
knownB[779-170] = (737,2583)
knownB[789-170] = (710,2602)
knownB[804-170] = (714,2586)
knownB[839-170] = (706,2574)


#for i in range(170,930):
#    print "mv A_%04d.JPG a_%04d.jpg" % (i, i-170)
#exit()

lk_params = dict( winSize  = (30, 30),
                  maxLevel = 4,
                  criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 30, 0.01))

feature_params = dict( maxCorners = 500,
                       qualityLevel = 0.4,
                       minDistance = 4,
                       blockSize = 24 )

class App:
    def __init__(self, video_src):
        self.track_len = 2
        self.detect_interval = 1
        self.tracks = []
        self.cam = cv2.VideoCapture("data/A_%04d.JPG") # video.create_capture(video_src)
        #self.cam.set(cv.CV_CAP_PROP_POS_FRAMES, 170)
        self.frame_idx = 0

    def run(self):
        px, py = knownA[0]
        while True:
            #time.sleep(0.1)
            ret, frame = self.cam.read()
            if frame is None: break
            frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            vis = frame.copy()
            
            if len(self.tracks) > 0:
                img0, img1 = self.prev_gray, frame_gray
                p0 = np.float32([tr[-1] for tr in self.tracks]).reshape(-1, 1, 2)
                p1, st, err = cv2.calcOpticalFlowPyrLK(img0, img1, p0, None, **lk_params)
                p0r, st, err = cv2.calcOpticalFlowPyrLK(img1, img0, p1, None, **lk_params)
                d = abs(p0-p0r).reshape(-1, 2).max(-1)
                good = d < 1
                new_tracks = []
                for tr, (x, y), good_flag in zip(self.tracks, p1.reshape(-1, 2), good):
                    if not good_flag:
                        continue
                    tr.append((x, y))
                    if len(tr) > self.track_len:
                        del tr[0]
                    new_tracks.append(tr)
                    cv2.circle(vis, (x, y), 2, (0, 255, 0), -1)
                self.tracks = new_tracks
                cv2.polylines(vis, [np.int32(tr) for tr in self.tracks], False, (0, 255, 0))

                movement = []                
                for tr in self.tracks:
                    # how much did last frame move?
                    if len(tr) > 1:
                        ax, ay = tr[-2]
                        bx, by = tr[-1]
                        dx=bx-ax; dy=by-ay
                        ang=math.atan2(dy, dx) * 180 / math.pi
                        movement.append((dx,dy,ang))

                N = len(movement)
                M = 0
                
                if len(movement) > 0:
                    s = np.std(movement, 0)
                    m = np.mean(movement, 0)

                    print "\nFRAME", self.frame_idx
                    print "\traw", len(movement), m, s
                    
                    # exclude points outside of stddev
                    #narrow = [ p for p in movement if abs(p[0]-m[0]) < s[0] and abs(p[1]-m[1]) < s[1] ]
                    narrow = [ p for p in movement if abs(p[2]-m[2]) < 30 ]
                    #narrow = movement
                    
                    M = len(narrow)
                    if len(narrow) > 0:
                        m2 = np.mean(narrow, 0)
                        s2 = np.std(narrow, 0)
                        
                        print "\tfil", len(narrow), m2, s2
                        
                        px += m2[0]; py += m2[1]
                                        
                if self.frame_idx in knownA:
                    kx,ky = knownA[self.frame_idx]
                    print
                    print "\t\terror", (int(round(px))-kx), (int(round(py))-ky)
                    #print "\t\test", int(round(px)),int(round(py))
                    #print "\t\tact", kx,ky
                    print
                    px=kx;py=ky
                elif M < 20 or N < M / 2:
                    print "------------------------------------> NEEDS LOVE <------------------------------------"

                print "\tRES", self.frame_idx, int(round(px)), int(round(py))

                #draw_str(vis, (20, 20), 'track count: %d' % len(self.tracks))


            if self.frame_idx % self.detect_interval == 0:
                mask = np.zeros_like(frame_gray)
                mask[:] = 255
                for x, y in [np.int32(tr[-1]) for tr in self.tracks]:
                    cv2.circle(mask, (x, y), 5, 0, -1)
                p = cv2.goodFeaturesToTrack(frame_gray, mask = mask, **feature_params)
                if p is not None:
                    for x, y in np.float32(p).reshape(-1, 2):
                        self.tracks.append([(x, y)])

            self.frame_idx += 1
            self.prev_gray = frame_gray
            cv2.imshow('lk_track', vis)
            
            #time.sleep(1)

            ch = 0xFF & cv2.waitKey(1)
            if ch == 27:
                break

        print "Finished and found", len(self.tracks), "useful tracks"

        print self.tracks

def main():
    import sys
    try:
        video_src = sys.argv[1]
    except:
        video_src = 0

    App(video_src).run()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
