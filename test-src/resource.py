##
# This file is part of the carambot-usherpa project.
#
# Copyright (C) 2012 Stefan Wendler <sw@kaltpost.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
##

'''
This file is part of the pyscmpd project.
'''

from pyscmpd.resource import *

try:

	d1 = DirectoryResource(12345, "/here", "A Directory Resource")
	print(d1)	

	d2 = DirectoryResource(12346, "/here/left", "A Second Directory Resource")
	print(d2)	

	f1 = FileResource(4567, "/here/there", "A File Resource")
	f1.setMeta({"artist" : "an artist", "title" : "the title"})
	print(f1)	
	print(d1)	

	d1.addChild(f1)
	d1.addChild(d2)

	print(d1)	
	print(d1.getChild(4567))	# ok
	print(d1.getChild(4568))	# none
	
	i = 0

	for c in d1.getAllChildren():
		i = i + 1
		print("%d: %s" % (i, c))

	c = d1.getChild(12346)
	d1.delChild(c)

	i = 0

	for c in d1.getAllChildren():
		i = i + 1
		print("%d: %s" % (i, c))

except Exception as e:
	
	print(e)
