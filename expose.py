
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


import math

# use blue sky to figure out consistent exposure
# look at blue filter at y > 3000

for line in open("best1.txt"):
    i,j,x,y = line.split(" ")

# Exposure Time                   : 1/3200
# each "EV" doubles the shutter speed
#File Name
#Exposure Time

# assuming target is 1/8000
target = float(8000)

def delta(a,b):
    return math.log(float(b)/float(a),2)


for line in open("exp.txt"):
    if "Name" in line: i = int(line[-9:-5])
    if "Time" in line and "/" in line:
        val = float(line[line.index("/")+1:].strip())
        
        print i, val, delta(target,val)
        



#print delta(4000,8000)
#print delta(8000,16000)
#print delta(4000,16000)
#print delta(8000,4000)
