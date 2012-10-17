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

import os
import logging
import pickle

class ResourceFilePersistence:

	baseDir = None

	def __init__(self, baseDir):

		self.baseDir = baseDir

	def store(self, key, obj):

		try:	

			f = open("%s/%s" % (self.baseDir, key), "wb")
			pickle.dump(obj, f)

		except Exception as e:

			logging.error("Unable to store to [%s]: %s" % (key, `e`))

		finally:

			f.close()

	def retrive(self, key):

		obj = None
		f = None

		try:	

			f = open("%s/%s" % (self.baseDir, key), "rb")
			obj = pickle.load(f)

		except Exception as e:

			logging.error("Unable to retrive from [%s]: %s" % (key, `e`))

		finally:

			if not f == None:
				f.close()

		return obj

	def remove(self, key):

		try:
			
			os.remove("%s/%s" % (self.baseDir, key))

		except Exception as e:
			logging.warn("Unable to remove playlist: %s" % `e`)

	def rename(self, srcKey, dstKey):

		try:
			
			os.rename("%s/%s" % (self.baseDir, srcKey), "%s/%s" % (self.baseDir, dstKey))

		except Exception as e:
			logging.warn("Unable to rename playlist: %s" % `e`)


