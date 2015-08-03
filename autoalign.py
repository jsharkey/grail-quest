
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

#BASE_PATH = "/home/jsharkey/vacat/DCIM/101EOS5D"
BASE_PATH = "/bandroid/lapse2/DCIM/101EOS5D"

parsed = {}

for line in open("../alignout.txt"):
    if "RES" not in line: continue
    res, fr, x, y = line.strip().split(" ")
    parsed[int(fr)] = (int(x),int(y))


#px = 3307; py = 2934
#px = 675; py = 2834

#parsed[0] = (675,2834)
#parsed[665] = (749,2589)

#parsed[0] = (3307,2934)
parsed[0] = (2614,319)

for i in range(170,930):
    j=i-170
    
    x, y = parsed[0]
    #print "convert %s/R59A%04d.JPG -crop 800x800+%d+%d A_%04d.JPG" % (BASE_PATH, i, x-400, y-600, j)
    #print "convert %s/R59A%04d.JPG -crop 400x400+%d+%d A_%04d.JPG" % (BASE_PATH, i, x-200, y-300, j)
    
    x, y = parsed[0]
    #print "convert %s/R59A%04d.JPG -crop 100x100+%d+%d FF_%04d.JPG" % (BASE_PATH, i, x-50, y-50, j)
    #print "convert ../data2/proc%04d.jpg -crop 100x100+%d+%d FF_%04d.JPG" % (j, x-50, y-50, j)
    
    parsed[j] = parsed[0]

#exit()





import numpy as np
import scipy.signal

def cross_image(im1, im2):
   # get rid of the color channels by performing a grayscale transform
   # the type cast into 'float' is to avoid overflows
   #im1_gray = np.sum(im1.astype('float'), axis=2)
   #im2_gray = np.sum(im2.astype('float'), axis=2)
   im1_gray = im1
   im2_gray = im2

   # get rid of the averages, otherwise the results are not good
   im1_gray -= np.mean(im1_gray)
   im2_gray -= np.mean(im2_gray)

   # calculate the correlation image; note the flipping of onw of the images
   return scipy.signal.fftconvolve(im1_gray, im2_gray[::-1,::-1], mode='same')


dx,dy = (0,0)
skip=1
skip_long=50

resolved = {}

for i in range(171+skip,930,skip):
    j=i-170
    #scipy.misc.imsave("delta_%04d.png" % (j), c)

    a = scipy.misc.imread("FF_%04d.JPG" % (j-skip), flatten=True)
    b = scipy.misc.imread("FF_%04d.JPG" % (j), flatten=True)
    c = cross_image(a, b)
    #scipy.misc.imsave("delta_%04d.png" % (j), c)
    y,x = np.unravel_index(np.argmax(c), c.shape)
    x-=50; y-=50
    dx+=x; dy+=y;

    # okay, we think we've aligned things
    rx,ry = parsed[j]
    rx-=dx; ry-=dy;
    
    if j-skip_long in resolved and j-skip_long>20:
        a = scipy.misc.imread("FF_%04d.JPG" % (j-skip_long), flatten=True)
        c = cross_image(a, b)
        y,x = np.unravel_index(np.argmax(c), c.shape)
        x-=50; y-=50
        
        nax,nay = parsed[j-skip_long]
        nbx,nby = parsed[j]
        nx=nbx-nax; ny=nby-nay;

        estx,esty = resolved[j-skip_long]
        estx+=nx; esty+=ny;
        estx-=x; esty-=y;
        
        errx=estx-rx; erry=esty-ry;
        #print j, "error", errx, erry
        #print "estimated", estx, esty, "found", rx,ry

        rx = (rx+estx)/2
        ry = (ry+esty)/2

    resolved[j] = (rx,ry)
    
    rx -= parsed[0][0]
    ry -= parsed[0][1]
    ry += 15
    
    print i,j,rx,ry
    #print "convert %s/R59A%04d.JPG -crop 800x800+%d+%d A2_%04d.JPG" % (BASE_PATH, i, rx-400, ry-400, j)
    print "convert ../data2/proc%04d.jpg -extent 4032x2511%+d%+d sun%04d.jpg" % (j, rx, ry, j)


# 1048 +/- 200
# 2681 +/- 200
