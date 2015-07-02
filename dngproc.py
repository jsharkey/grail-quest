
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

from __future__ import division, print_function, absolute_import

import numpy as np
from scipy.linalg import lstsq
from math import factorial
from scipy.ndimage import convolve1d
#from ._arraytools import axis_slice

def axis_slice(a, start=None, stop=None, step=None, axis=-1):
    """Take a slice along axis 'axis' from 'a'.
    Parameters
    ----------
    a : numpy.ndarray
        The array to be sliced.
    start, stop, step : int or None
        The slice parameters.
    axis : int
        The axis of `a` to be sliced.
    Examples
    --------
    >>> a = array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    >>> axis_slice(a, start=0, stop=1, axis=1)
    array([[1],
           [4],
           [7]])
    >>> axis_slice(a, start=1, axis=0)
    array([[4, 5, 6],
           [7, 8, 9]])
    Notes
    -----
    The keyword arguments start, stop and step are used by calling
    slice(start, stop, step).  This implies axis_slice() does not
    handle its arguments the exacty the same as indexing.  To select
    a single index k, for example, use
        axis_slice(a, start=k, stop=k+1)
    In this case, the length of the axis 'axis' in the result will
    be 1; the trivial dimension is not removed. (Use numpy.squeeze()
    to remove trivial axes.)
    """
    a_slice = [slice(None)] * a.ndim
    a_slice[axis] = slice(start, stop, step)
    b = a[a_slice]
    return b

def savgol_coeffs(window_length, polyorder, deriv=0, delta=1.0, pos=None,
                  use="conv"):
    """Compute the coefficients for a 1-d Savitzky-Golay FIR filter.
    Parameters
    ----------
    window_length : int
        The length of the filter window (i.e. the number of coefficients).
        `window_length` must be an odd positive integer.
    polyorder : int
        The order of the polynomial used to fit the samples.
        `polyorder` must be less than `window_length`.
    deriv : int, optional
        The order of the derivative to compute.  This must be a
        nonnegative integer.  The default is 0, which means to filter
        the data without differentiating.
    delta : float, optional
        The spacing of the samples to which the filter will be applied.
        This is only used if deriv > 0.
    pos : int or None, optional
        If pos is not None, it specifies evaluation position within the
        window.  The default is the middle of the window.
    use : str, optional
        Either 'conv' or 'dot'.  This argument chooses the order of the
        coefficients.  The default is 'conv', which means that the
        coefficients are ordered to be used in a convolution.  With
        use='dot', the order is reversed, so the filter is applied by
        dotting the coefficients with the data set.
    Returns
    -------
    coeffs : 1-d ndarray
        The filter coefficients.
    References
    ----------
    A. Savitzky, M. J. E. Golay, Smoothing and Differentiation of Data by
    Simplified Least Squares Procedures. Analytical Chemistry, 1964, 36 (8),
    pp 1627-1639.
    See Also
    --------
    savgol_filter
    Notes
    -----
    .. versionadded:: 0.14.0
    Examples
    --------
    >>> savgol_coeffs(5, 2)
    array([-0.08571429,  0.34285714,  0.48571429,  0.34285714, -0.08571429])
    >>> savgol_coeffs(5, 2, deriv=1)
    array([  2.00000000e-01,   1.00000000e-01,   2.00607895e-16,
            -1.00000000e-01,  -2.00000000e-01])
    Note that use='dot' simply reverses the coefficients.
    >>> savgol_coeffs(5, 2, pos=3)
    array([ 0.25714286,  0.37142857,  0.34285714,  0.17142857, -0.14285714])
    >>> savgol_coeffs(5, 2, pos=3, use='dot')
    array([-0.14285714,  0.17142857,  0.34285714,  0.37142857,  0.25714286])
    `x` contains data from the parabola x = t**2, sampled at
    t = -1, 0, 1, 2, 3.  `c` holds the coefficients that will compute the
    derivative at the last position.  When dotted with `x` the result should
    be 6.
    >>> x = array([1, 0, 1, 4, 9])
    >>> c = savgol_coeffs(5, 2, pos=4, deriv=1, use='dot')
    >>> c.dot(x)
    6.0000000000000018
    """

    # An alternative method for finding the coefficients when deriv=0 is
    #    t = np.arange(window_length)
    #    unit = (t == pos).astype(int)
    #    coeffs = np.polyval(np.polyfit(t, unit, polyorder), t)
    # The method implemented here is faster.

    # To recreate the table of sample coefficients shown in the chapter on
    # the Savitzy-Golay filter in the Numerical Recipes book, use
    #    window_length = nL + nR + 1
    #    pos = nL + 1
    #    c = savgol_coeffs(window_length, M, pos=pos, use='dot')

    if polyorder >= window_length:
        raise ValueError("polyorder must be less than window_length.")

    halflen, rem = divmod(window_length, 2)

    if rem == 0:
        raise ValueError("window_length must be odd.")

    if pos is None:
        pos = halflen

    if not (0 <= pos < window_length):
        raise ValueError("pos must be nonnegative and less than "
                         "window_length.")

    if use not in ['conv', 'dot']:
        raise ValueError("`use` must be 'conv' or 'dot'")

    # Form the design matrix A.  The columns of A are powers of the integers
    # from -pos to window_length - pos - 1.  The powers (i.e. rows) range
    # from 0 to polyorder.  (That is, A is a vandermonde matrix, but not
    # necessarily square.)
    x = np.arange(-pos, window_length - pos)
    if use == "conv":
        # Reverse so that result can be used in a convolution.
        x = x[::-1]

    order = np.arange(polyorder + 1).reshape(-1, 1)
    if order.size == 1:
        # Avoid spurious DeprecationWarning in numpy 1.8.0 for
        # ``[1] ** [[2]]``, see numpy gh-4145.
        A = np.atleast_2d(x ** order[0, 0])
    else:
        A = x ** order

    # y determines which order derivative is returned.
    y = np.zeros(polyorder + 1)
    # The coefficient assigned to y[deriv] scales the result to take into
    # account the order of the derivative and the sample spacing.
    y[deriv] = factorial(deriv) / (delta ** deriv)

    # Find the least-squares solution of A*c = y
    coeffs, _, _, _ = lstsq(A, y)

    return coeffs


def _polyder(p, m):
    """Differentiate polynomials represented with coefficients.
    p must be a 1D or 2D array.  In the 2D case, each column gives
    the coefficients of a polynomial; the first row holds the coefficients
    associated with the highest power.  m must be a nonnegative integer.
    (numpy.polyder doesn't handle the 2D case.)
    """

    if m == 0:
        result = p
    else:
        n = len(p)
        if n <= m:
            result = np.zeros_like(p[:1, ...])
        else:
            dp = p[:-m].copy()
            for k in range(m):
                rng = np.arange(n - k - 1, m - k - 1, -1)
                dp *= rng.reshape((n - m,) + (1,) * (p.ndim - 1))
            result = dp
    return result


def _fit_edge(x, window_start, window_stop, interp_start, interp_stop,
              axis, polyorder, deriv, delta, y):
    """
    Given an n-d array `x` and the specification of a slice of `x` from
    `window_start` to `window_stop` along `axis`, create an interpolating
    polynomial of each 1-d slice, and evaluate that polynomial in the slice
    from `interp_start` to `interp_stop`.  Put the result into the
    corresponding slice of `y`.
    """

    # Get the edge into a (window_length, -1) array.
    x_edge = axis_slice(x, start=window_start, stop=window_stop, axis=axis)
    if axis == 0 or axis == -x.ndim:
        xx_edge = x_edge
        swapped = False
    else:
        xx_edge = x_edge.swapaxes(axis, 0)
        swapped = True
    xx_edge = xx_edge.reshape(xx_edge.shape[0], -1)

    # Fit the edges.  poly_coeffs has shape (polyorder + 1, -1),
    # where '-1' is the same as in xx_edge.
    poly_coeffs = np.polyfit(np.arange(0, window_stop - window_start),
                             xx_edge, polyorder)

    if deriv > 0:
        poly_coeffs = _polyder(poly_coeffs, deriv)

    # Compute the interpolated values for the edge.
    i = np.arange(interp_start - window_start, interp_stop - window_start)
    values = np.polyval(poly_coeffs, i.reshape(-1, 1)) / (delta ** deriv)

    # Now put the values into the appropriate slice of y.
    # First reshape values to match y.
    shp = list(y.shape)
    shp[0], shp[axis] = shp[axis], shp[0]
    values = values.reshape(interp_stop - interp_start, *shp[1:])
    if swapped:
        values = values.swapaxes(0, axis)
    # Get a view of the data to be replaced by values.
    y_edge = axis_slice(y, start=interp_start, stop=interp_stop, axis=axis)
    y_edge[...] = values


def _fit_edges_polyfit(x, window_length, polyorder, deriv, delta, axis, y):
    """
    Use polynomial interpolation of x at the low and high ends of the axis
    to fill in the halflen values in y.
    This function just calls _fit_edge twice, once for each end of the axis.
    """
    halflen = window_length // 2
    _fit_edge(x, 0, window_length, 0, halflen, axis,
              polyorder, deriv, delta, y)
    n = x.shape[axis]
    _fit_edge(x, n - window_length, n, n - halflen, n, axis,
              polyorder, deriv, delta, y)


def savgol_filter(x, window_length, polyorder, deriv=0, delta=1.0,
                  axis=-1, mode='interp', cval=0.0):
    """ Apply a Savitzky-Golay filter to an array.
    This is a 1-d filter.  If `x`  has dimension greater than 1, `axis`
    determines the axis along which the filter is applied.
    Parameters
    ----------
    x : array_like
        The data to be filtered.  If `x` is not a single or double precision
        floating point array, it will be converted to type `numpy.float64`
        before filtering.
    window_length : int
        The length of the filter window (i.e. the number of coefficients).
        `window_length` must be a positive odd integer.
    polyorder : int
        The order of the polynomial used to fit the samples.
        `polyorder` must be less than `window_length`.
    deriv : int, optional
        The order of the derivative to compute.  This must be a
        nonnegative integer.  The default is 0, which means to filter
        the data without differentiating.
    delta : float, optional
        The spacing of the samples to which the filter will be applied.
        This is only used if deriv > 0.  Default is 1.0.
    axis : int, optional
        The axis of the array `x` along which the filter is to be applied.
        Default is -1.
    mode : str, optional
        Must be 'mirror', 'constant', 'nearest', 'wrap' or 'interp'.  This
        determines the type of extension to use for the padded signal to
        which the filter is applied.  When `mode` is 'constant', the padding
        value is given by `cval`.  See the Notes for more details on 'mirror',
        'constant', 'wrap', and 'nearest'.
        When the 'interp' mode is selected (the default), no extension
        is used.  Instead, a degree `polyorder` polynomial is fit to the
        last `window_length` values of the edges, and this polynomial is
        used to evaluate the last `window_length // 2` output values.
    cval : scalar, optional
        Value to fill past the edges of the input if `mode` is 'constant'.
        Default is 0.0.
    Returns
    -------
    y : ndarray, same shape as `x`
        The filtered data.
    See Also
    --------
    savgol_coeffs
    Notes
    -----
    Details on the `mode` options:
        'mirror':
            Repeats the values at the edges in reverse order.  The value
            closest to the edge is not included.
        'nearest':
            The extension contains the nearest input value.
        'constant':
            The extension contains the value given by the `cval` argument.
        'wrap':
            The extension contains the values from the other end of the array.
    For example, if the input is [1, 2, 3, 4, 5, 6, 7, 8], and
    `window_length` is 7, the following shows the extended data for
    the various `mode` options (assuming `cval` is 0)::
        mode       |   Ext   |         Input          |   Ext
        -----------+---------+------------------------+---------
        'mirror'   | 4  3  2 | 1  2  3  4  5  6  7  8 | 7  6  5
        'nearest'  | 1  1  1 | 1  2  3  4  5  6  7  8 | 8  8  8
        'constant' | 0  0  0 | 1  2  3  4  5  6  7  8 | 0  0  0
        'wrap'     | 6  7  8 | 1  2  3  4  5  6  7  8 | 1  2  3
    .. versionadded:: 0.14.0
    Examples
    --------
    >>> np.set_printoptions(precision=2)  # For compact display.
    >>> x = np.array([2, 2, 5, 2, 1, 0, 1, 4, 9])
    Filter with a window length of 5 and a degree 2 polynomial.  Use
    the defaults for all other parameters.
    >>> y = savgol_filter(x, 5, 2)
    array([ 1.66,  3.17,  3.54,  2.86,  0.66,  0.17,  1.  ,  4.  ,  9.  ])
    Note that the last five values in x are samples of a parabola, so
    when mode='interp' (the default) is used with polyorder=2, the last
    three values are unchanged.  Compare that to, for example,
    `mode='nearest'`:
    >>> savgol_filter(x, 5, 2, mode='nearest')
    array([ 1.74,  3.03,  3.54,  2.86,  0.66,  0.17,  1.  ,  4.6 ,  7.97])
    """
    if mode not in ["mirror", "constant", "nearest", "interp", "wrap"]:
        raise ValueError("mode must be 'mirror', 'constant', 'nearest' "
                         "'wrap' or 'interp'.")

    x = np.asarray(x)
    # Ensure that x is either single or double precision floating point.
    if x.dtype != np.float64 and x.dtype != np.float32:
        x = x.astype(np.float64)

    coeffs = savgol_coeffs(window_length, polyorder, deriv=deriv, delta=delta)

    if mode == "interp":
        # Do not pad.  Instead, for the elements within `window_length // 2`
        # of the ends of the sequence, use the polynomial that is fitted to
        # the last `window_length` elements.
        y = convolve1d(x, coeffs, axis=axis, mode="constant")
        _fit_edges_polyfit(x, window_length, polyorder, deriv, delta, axis, y)
    else:
        # Any mode other than 'interp' is passed on to ndimage.convolve1d.
        y = convolve1d(x, coeffs, axis=axis, mode=mode, cval=cval)

    return y

import subprocess, re, os, sys
#from scipy import signal


from progressbar import AnimatedMarker, Bar, BouncingBar, Counter, ETA, \
    FileTransferSpeed, FormatLabel, Percentage, \
    ProgressBar, ReverseBar, RotatingMarker, \
    SimpleProgress, Timer

re_ident = re.compile(
	"Red:.+?mean: ([\d.]+).+?"
	"Green:.+?mean: ([\d.]+).+?"
	"Blue:.+?mean: ([\d.]+).+?"
	"Overall:.+?mean: ([\d.]+).+?", re.DOTALL)

# Quickly estimate luminance using DNG thumbnail
files = [ "%08d.DNG" % (n) for n in range(16, 378) ]

# Quickly estimate luminance using DNG thumbnail

widgets = ['normalize'.ljust(20), '(', Counter(), '/', str(len(files)), ') ', Percentage(), ' ', Bar(), ' ', ETA()]
pbar = ProgressBar(widgets=widgets, maxval=len(files)).start()

lum_in = []
for i in range(len(files)):
	dng = files[i]
	thumb = "%s.thumb" % (dng)
	if not os.path.isfile(thumb):
		subprocess.check_output(["tiffcp", dng, thumb], stderr=subprocess.STDOUT)
	stats = "%s.stats" % (dng)
	if not os.path.isfile(stats):
		res = subprocess.check_output(["identify", "-verbose", thumb], stderr=subprocess.STDOUT)
		with open(stats, 'w') as f:
			f.write(res)
	else:
		with open(stats, 'r') as f:
			res = f.read()

	r, g, b, over = re_ident.search(res).groups()
	lum = 0.2126 * float(r) + 0.7152 * float(g) + 0.0722 * float(b)
	lum_in.append(lum)
	pbar.update(i)

pbar.finish()


# Aim for the best brightness ramping over time
lum_out = signal.savgol_filter(lum_in, 101, 5)


# echo "set terminal wxt size 1024,768; plot 'comp.plot' using 2 with lines, 'comp.plot' using 3 with lines" | gnuplot -p
with open("comp.plot", 'w') as plot:
	for i in range(len(lum_in)):
		exp_in = (0.03353246037*lum_in[i])-1.3650011411500929
		exp_out = (0.03353246037*lum_out[i])-1.3650011411500929
		exp_delta = 1 + (exp_out - exp_in)

		print >>plot, files[i], "\t", lum_in[i], "\t", lum_out[i], "\t", exp_delta
		with open("%s.pp3" % (files[i]), 'w') as f:
			f.write("""
[Exposure]
Compensation=%f
""" % (exp_delta))


widgets = ['develop'.ljust(20), '(', Counter(), '/', str(len(files)), ') ', Percentage(), ' ', Bar(), ' ', ETA()]
pbar = ProgressBar(widgets=widgets, maxval=len(files)).start()

for i in range(len(files)):
	dng = files[i]
	jpg = "post2_%s.jpg" % (dng)
	if not os.path.isfile(jpg):
		subprocess.check_output(["rawtherapee",
			"-o", jpg,
			"-p", "template.pp3",
			"-p", "%s.pp3" % (dng),
			"-c", dng], stderr=subprocess.STDOUT)
	pbar.update(i)

pbar.finish()




'''
for i in [0,0.25,0.5,0.75,
		  1,1.25,1.5,1.75,
		  2,2.25,2.5,2.75]:
	with open("test.pp3", 'w') as f:
		f.write("""
[Exposure]
Compensation=%f
""" % (i))

	print subprocess.check_output(["rawtherapee",
		"-o", "out%f.jpg" % (i),
		"-p", "template.pp3",
		"-p", "test.pp3",
		"-c", "00000309.DNG"], stderr=subprocess.STDOUT)
'''

"""

exp = 0.03353246037x-1.3650011411500929




0.5 / 1.5 = 0.333333333

85.62613468 /55.81944982= 0.65189734452


exp = 0.03353246037*1.53398385251-1.3650011411500929




out0.000000.jpg 45.27572356 --> 45.27572356
out0.250000.jpg 51.51633756 --> 51.51633756
out0.500000.jpg 55.81944982 --> 55.81944982
out0.750000.jpg 62.80887232 --> 62.80887232
out1.000000.jpg 70.14054262 --> 70.14054262
out1.250000.jpg 77.77240904 --> 77.77240904
out1.500000.jpg 85.62613468 --> 85.62613468
out1.750000.jpg 93.61412692 --> 93.61412692
out2.000000.jpg 96.69328266 --> 96.69328266


tiffcp 00000309.DNG a
identify -verbose a

    Red:
      mean: 74.2578 (0.291207)
    Green:
      mean: 78.2369 (0.306811)
    Blue:
      mean: 93.9917 (0.368595)
  Image statistics:
    Overall:
      mean: 82.1621 (0.322204)




"""
