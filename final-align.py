
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

"""

one last alignment pass!
we know that all points should be moving in the same average direction
so look at the window of nearby flow points

areas for testing:
210-220
600-630




shift=395-6-7

"""

import numpy as np
import cv, cv2
import time
import math
import collections, copy

def dist(a,b):
    x1,y1=a
    x2,y2=b                
    dx=x2-x1; dy=y2-y1
    return math.sqrt(dx*dx + dy*dy)

def ang(a,b):
    x1,y1=a
    x2,y2=b                
    return math.atan2(y2-y1, x2-x1) * 180 / math.pi

def add(a,b):
    x1,y1=a
    x2,y2=b                
    return (x1+x2,y1+y2)


lk_params = dict( winSize  = (20, 20),
                  maxLevel = 2,
                  criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 30, 0.01))

feature_params = dict( maxCorners = 500,
                       qualityLevel = 0.4,
                       minDistance = 20,
                       blockSize = 24 )

class App:
    def __init__(self, video_src):
        self.track_len = 3
        self.detect_interval = 3
        self.tracks = []
        self.cam = cv2.VideoCapture("data2/proc%04d.jpg") # video.create_capture(video_src)
        self.cam.set(cv.CV_CAP_PROP_POS_FRAMES, 220)
        self.frame_idx = 0
        self.adjust = collections.defaultdict(lambda: (0,0))

    def run(self):
        while True:
            ret, frame = self.cam.read()
            if self.frame_idx < 20:
                self.frame_idx += 1
                continue

            frame = cv2.resize(frame, (4032/2,2511/2))
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
                    #cv2.circle(vis, (x, y), 2, (0, 255, 0), -1)
                self.tracks = new_tracks
                #cv2.polylines(vis, [np.int32(tr) for tr in self.tracks], False, (0, 255, 0))

            self.tweak(vis)

            if self.frame_idx % self.detect_interval == 0:
                mask = np.zeros_like(frame_gray)
                mask[:] = 255
                #for x, y in [np.int32(tr[-1]) for tr in self.tracks]:
                #    cv2.circle(mask, (x, y), 5, 0, -1)
                p = cv2.goodFeaturesToTrack(frame_gray, mask = mask, **feature_params)
                if p is not None:
                    for x, y in np.float32(p).reshape(-1, 2):
                        self.tracks.append([(x, y)])

            self.frame_idx += 1
            self.prev_gray = frame_gray
            cv2.imshow('lk_track', vis)
            
            ch = 0xFF & cv2.waitKey(1)
            if ch == 27:
                print self.adjust
                break

    def do_care_tracks(self):
        care = []
        for t in self.tracks:
            if len(t) < self.track_len: continue
            if dist(t[0], t[-1]) < 10: continue
            #print dist(t[0], t[-1]), t
            care.append(t)
        return care

    def do_adjust(self, care):
        care = copy.deepcopy(care)
        for t in care:
            for i in range(len(t)):
                t[i] = add(t[i], self.adjust[self.frame_idx-len(t)+i])
        return care

    def do_std(self, care, guess):
        overall = []
        for t in care:
            stat = []
            for i in range(1, len(t)):
                last = t[i-1]
                cur = t[i]
                if i == len(t) - 2:
                    cur = add(cur, guess)
                
                #d = dist(last,cur)
                a = ang(last,cur)
                stat.append(a)

            s = np.std(stat, 0)
            if s < 90: overall.append(s)

        if len(overall) == 0:
            return 1024
        else:
            #print guess, overall
            return np.mean(overall, 0)

    def tweak(self, vis):
        care = self.do_care_tracks()

        cv2.polylines(vis, [np.int32(tr) for tr in care], False, (0, 0, 255))

        care = self.do_adjust(care)
        
        lowest = 1024
        li = 0; lj = 0
        for i in range(-12,13,3):
            for j in range(-12,13,3):
                v = self.do_std(care, (i,j))
                if v < lowest:
                    lowest = v
                    li = i; lj = j
                    #print v, i, j

        print self.frame_idx, li, lj
        #self.adjust[self.frame_idx] = (li,lj)

        #left = self.do_std(care, (-1,0))
        #right = self.do_std(care, (+1,0))

        print "----"


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

