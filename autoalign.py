

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

parsed[0] = (3307,2934)

for i in range(170,930):
    j=i-170
    
    x, y = parsed[0]
    #print "convert %s/R59A%04d.JPG -crop 800x800+%d+%d A_%04d.JPG" % (BASE_PATH, i, x-400, y-600, j)
    #print "convert %s/R59A%04d.JPG -crop 400x400+%d+%d A_%04d.JPG" % (BASE_PATH, i, x-200, y-300, j)
    
    x, y = parsed[j]
    #print "convert %s/R59A%04d.JPG -crop 100x100+%d+%d AA_%04d.JPG" % (BASE_PATH, i, x-50, y-50, j)

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

for i in range(170+skip,930,skip):
    j=i-170
    #scipy.misc.imsave("delta_%04d.png" % (j), c)

    a = scipy.misc.imread("AA_%04d.JPG" % (j-skip), flatten=True)
    b = scipy.misc.imread("AA_%04d.JPG" % (j), flatten=True)
    c = cross_image(a, b)
    y,x = np.unravel_index(np.argmax(c), c.shape)
    x-=50; y-=50
    dx+=x; dy+=y;

    # okay, we think we've aligned things
    rx,ry = parsed[j]
    rx-=dx; ry-=dy;
    
    if j-skip_long in resolved and j-skip_long>20:
        a = scipy.misc.imread("AA_%04d.JPG" % (j-skip_long), flatten=True)
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
    
    print i,j,rx,ry
    #print "convert %s/R59A%04d.JPG -crop 800x800+%d+%d A2_%04d.JPG" % (BASE_PATH, i, rx-400, ry-400, j)


# 1048 +/- 200
# 2681 +/- 200
