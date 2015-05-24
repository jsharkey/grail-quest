
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

import subprocess, re, os, sys
from scipy import signal

re_ident = re.compile(
	"Red:.+?mean: ([\d.]+).+?"
	"Green:.+?mean: ([\d.]+).+?"
	"Blue:.+?mean: ([\d.]+).+?"
	"Overall:.+?mean: ([\d.]+).+?", re.DOTALL)

# Quickly estimate luminance using DNG thumbnail
files = [ "%08d.DNG" % (n) for n in range(16, 378) ]
lum_in = []
for dng in files:
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


# Aim for the best brightness ramping over time
lum_out = signal.savgol_filter(lum_in, 21, 3)

for i in range(len(lum_in)):
	print files[i], lum_in[i], "-->", lum_out[i],

	exp_in = (0.03353246037*lum_in[i])-1.3650011411500929
	exp_out = (0.03353246037*lum_out[i])-1.3650011411500929
	exp_delta = 1 + (exp_out - exp_in)

	print "\t", exp_delta
	with open("%s.pp3" % (files[i]), 'w') as f:
		f.write("""
[Exposure]
Compensation=%f
""" % (exp_delta))


for dng in files:
	print "Processing %s..." % (dng)
	jpg = "post_%s.jpg" % (dng)
	if not os.path.isfile(jpg):
		subprocess.check_output(["rawtherapee",
			"-o", jpg,
			"-p", "template.pp3",
			"-p", "%s.pp3" % (dng),
			"-c", dng], stderr=subprocess.STDOUT)





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
