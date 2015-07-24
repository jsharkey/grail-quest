


#px = 3307; py = 2934
px = 675; py = 2834

for i in range(170,930):
    print "convert /home/jsharkey/vacat/DCIM/101EOS5D/R59A%04d.JPG -crop 800x800+%d+%d B_%04d.JPG" % (i, px-400, py-600, i-170)

exit()





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


for i in range(180,930,10):
    # this is how much to shift compared to previous image
    a = scipy.ndimage.imread("data/A_%04d.JPG" % (i-10), flatten=True)
    b = scipy.ndimage.imread("data/A_%04d.JPG" % (i), flatten=True)
    c = cross_image(a, b)
    scipy.misc.imsave("data/delta_%04d.png" % (i), c)
    x,y = np.unravel_index(np.argmax(c), c.shape)
    x-=200; y-=200
    px+=x; py+=y;
    print (i-170), (px), (py)


# 1048 +/- 200
# 2681 +/- 200
