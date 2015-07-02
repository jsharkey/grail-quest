#!/usr/bin/env python


import numpy as np
import cv, cv2
#import video
#from common import anorm2, draw_str
from time import clock
import time
import math


#for i in range(18,94):
#    print "mv R59A0%02d0.JPG.jpg %04d.jpg" % (i, i-18)
#exit()

lk_params = dict( winSize  = (15, 15),
                  maxLevel = 2,
                  criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

feature_params = dict( maxCorners = 500,
                       qualityLevel = 0.3,
                       minDistance = 7,
                       blockSize = 7 )

class App:
    def __init__(self, video_src):
        self.track_len = 5000
        self.detect_interval = 5000
        self.tracks = []
        self.cam = cv2.VideoCapture("%04d.jpg") # video.create_capture(video_src)
        #self.cam.set(cv.CV_CAP_PROP_POS_FRAMES, 18)
        self.frame_idx = 0

    def run(self):
        while True:
            ret, frame = self.cam.read()
            #print ret, frame
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
                
                delta = []
                
                for tr, (x, y), good_flag in zip(self.tracks, p1.reshape(-1, 2), good):
                    if not good_flag:
                        continue

                    if len(tr) > 1:
                        lx, ly = tr[-1]
                        delta.append((x-lx, y-ly, tr))

                    tr.append((x, y))
                    if len(tr) > self.track_len:
                        del tr[0]
                    new_tracks.append(tr)                    
                    
                    cv2.circle(vis, (x, y), 2, (0, 255, 0), -1)
                self.tracks = new_tracks
                
                #print delta
                # how much did frame move?
                """
                deltar = [ np.sqrt(np.power(x,2)+np.power(y,2)) for x,y,tr in delta ]
                avg = np.average(deltar)
                std = np.std(deltar)
                filt = []
                for i in range(len(delta)):
                    if np.abs(deltar[i] - avg) < std:
                        filt.append(delta[i])
                        pass #print "+++", delta[i]
                    else:
                        pass #print "---", delta[i]

                #print delta
                #print "-->"
                #print filt
                #print
                #print
                
                #print np.std([x for x, y in delta])
                
                # we're only interested in last frame movement
                #for tr in self.tracks:
                #    print tr
                """
                cv2.polylines(vis, [np.int32(tr) for tr in self.tracks], False, (0, 255, 0))
                #draw_str(vis, (20, 20), 'track count: %d' % len(self.tracks))

            #else:
            #    self.tracks = [[(518,196)],[(662,249)],[(850,232)]]


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
