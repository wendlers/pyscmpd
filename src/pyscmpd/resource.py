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

import logging

class Resource:

	TYPE_GENERIC	= 0
	TYPE_DIRECTORY	= 1
	TYPE_FILE		= 2
	TYPE_ARTIST		= 3
	TYPE_ALBUM		= 4
	TYPE_TRACK		= 5 
	TYPE_PLAYLIST	= 6 

	id 			= None
	location	= None
	meta		= None 
	name		= None

	def __init__(self, resourceId, resourceLocation, name = "UNKNOWN"):

		self.meta 	  		= {}
		self.id 	  		= resourceId
		self.location 		= resourceLocation
		self.name 			= name

	def setMeta(self, meta):

		self.meta = meta

	def getName(self):

		return self.name

	def getMeta(self, key = None):
	
		if key == None:
			return self.meta

		return self.meta.get(key, None)

	def getLocation(self):
		
		return self.location
 
	def getType(self):

		return self.TYPE_GENERIC

	def getId(self):
		
		return self.id

	def __str__(self):

		return ("%s [id=%s; location=%s; type=%d, meta=%s]" % 
			(self.name, self.id, self.location, self.getType(), self.meta))


class DirectoryResource(Resource):

	children = None 

	def __init__(self, resourceId, resourceLocation, name = "UNKNOWN"):

		self.children = []

		Resource.__init__(self, resourceId, resourceLocation, name)

	def addChild(self, child):
	
		self.children.append(child)

	def getChild(self, resourceId):

		for c in self.children:
			if c.getId() == resourceId: 
				return c

		return None

	def getChildByName(self, name):

		children = self.getAllChildren()

		for c in children:
			if c.getName() == name: 
				return c

		return None
		
	def getChildByPath(self, path):

		p = path
		c = self

		while True:
			(l, s, r) = p.partition("/")

			logging.info("Consuming path [%s]/[%s]" % (l, r))

			if l == "" or not c.getType() == Resource.TYPE_DIRECTORY:
				return None

			c = c.getChildByName(l)
		
			if r == "":
				break
			
			p = r	

		return c 

	def getAllChildren(self):

		return self.children

	def delChild(self, child):	
	
		self.children.remove(child)

	def delAllChildren(self):

		self.children = []

	def getType(self):

		return self.TYPE_DIRECTORY
		
	def __str__(self):

		return ("%s [id=%s; location=%s; type=%d, meta=%s]" % 
			(self.name, self.id, self.location, self.getType(), self.meta))


class FileResource(Resource):

	def __init__(self, resourceId, resourceLocation, name = "UNKNOWN"):

		Resource.__init__(self, resourceId, resourceLocation, name)

	def getType(self):

		return self.TYPE_FILE

	def getStreamUri(self):
		
		return "file://" + self.location

	def __str__(self):

		return ("%s [id=%s; location=%s; type=%d, meta=%s]" % 
			(self.name, self.id, self.location, self.getType(), self.meta))

