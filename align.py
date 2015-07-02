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



#for i in range(17,95):
#    print "mv %d.jpg %02d.jpg" % (i-17, i-17)
#exit(1)

"""

avconv -framerate 5 -f image2 -i %02d.post.jpg out.mp4

"""


import numpy as np
import numpy
import cv2
#import video
#from common import anorm2, draw_str
from time import clock
import math

def decompose_matrix2(M):
    a,b,tx = M[0]
    c,d,ty = M[1]
    
    a1=math.atan2(-b,a)*(180/math.pi)
    a2=math.atan2(c,d)*(180/math.pi)
    
    return tx, ty, a1, a2
    


lk_params = dict( winSize  = (150, 150),
                  maxLevel = 2,
                  criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

feature_params = dict( maxCorners = 500,
                       qualityLevel = 0.3,
                       minDistance = 70,
                       blockSize = 70 )

class App:
    def __init__(self, video_src):
        self.track_len = 5000
        self.detect_interval = 1
        self.tracks = []
        self.cam = cv2.VideoCapture("%02d.jpg")  # video.create_capture(video_src)
        self.frame_idx = 0
        self.FM = np.float32([[0,0,0],
                              [0,0,0],
                              [0,0,1]])
        print self.FM

    def run(self):
        while True:
            ret, frame = self.cam.read()
            if frame is None:
                print "NO MAOR FRAME!"
                break
            frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            vis = frame.copy()
            
            if len(self.tracks) > 0:
                img0, img1 = self.prev_gray, frame_gray
                p0 = np.float32([tr[-1] for tr in self.tracks]).reshape(-1, 1, 2)
                print "going one way...",
                p1, st, err = cv2.calcOpticalFlowPyrLK(img0, img1, p0, None, **lk_params)
                print "and the other...",
                p0r, st, err = cv2.calcOpticalFlowPyrLK(img1, img0, p1, None, **lk_params)
                d = abs(p0-p0r).reshape(-1, 2).max(-1)
                good = d < 1
                print "d=", len(d)
                new_tracks = []
                for tr, (x, y), good_flag in zip(self.tracks, p1.reshape(-1, 2), good):
                    if not good_flag:
                        continue
                    tr.append((x, y))
                    if len(tr) > self.track_len:
                        del tr[0]
                    new_tracks.append(tr)
                    cv2.circle(vis, (x, y), 2, (0, 255, 0), -1)

                if len(new_tracks) == 0:
                    print "NO NEW TRACKS FOUND"
                    print self.tracks

                if len(new_tracks[0]) > 1:
                    src = np.float32([tr[-1] for tr in new_tracks]).reshape(-1, 1, 2)
                    dst = np.float32([tr[-2] for tr in new_tracks]).reshape(-1, 1, 2)
                    
                    print "search pts", len(src)
                    
                    M, mask = cv2.findHomography(src, dst, cv2.RANSAC, 5)

                    M[2,0] = 0
                    M[2,1] = 0

                    #print M
                    #print decompose_matrix2(M)
                    
                    if self.FM is None:
                        self.FM = M
                    else:
                        self.FM += M

                    print self.FM
                    x,y,r1,r2 = decompose_matrix2(self.FM)
                    print x,y,r1,r2
                    
                    print "convert %02d.jpg -page %+d%+d -background none -flatten %02d.post.jpg" % (self.frame_idx, x,y,self.frame_idx)

                    #print mask.ravel().tolist()
                    
                self.tracks = new_tracks
                cv2.polylines(vis, [np.int32(tr) for tr in self.tracks], False, (0, 255, 0))
                #draw_str(vis, (20, 20), 'track count: %d' % len(self.tracks))

            if self.frame_idx % self.detect_interval == 0:
                print "------------------------- NEW!"
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
            
            #vis2 = cv2.resize(vis, (1440,960), interpolation = cv2.INTER_AREA)
            #cv2.imshow('lk_track', vis2)

            ch = 0xFF & cv2.waitKey(1)
            if ch == 27:
                break
        # TODO: print out tracks!

def main():
    import sys
    try:
        video_src = sys.argv[1]
    except:
        video_src = 0

    print __doc__
    App(video_src).run()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()


