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

import traceback
import logging

import pyscmpd.scprovider as provider 

try:

	logging.basicConfig(level=logging.DEBUG)

	provider.ResourceProvider.ROOT_USERS =  [ "/users/griz" ]

	p = provider.ResourceProvider()

	r = p.getRoot()

	print("")

	for u in r.getAllChildren():
		print(u)
		for t in u.getAllChildren():
			print(t)

except Exception as e:
	
	print traceback.format_exc()
