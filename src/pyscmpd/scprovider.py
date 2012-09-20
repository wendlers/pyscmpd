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

import pickle
import logging
import soundcloud 

import pyscmpd.resource as resource

class ResourceProvider:

	favorites 	= None 
	sc 			= None 
	root 		= None

	def __init__(self):

		ResourceProvider.sc = soundcloud.Client(client_id='aa13bebc2d26491f7f8d1e77ae996a64')

		self.root = Root(1, "http://www.soundcloud.com")

	def getRoot(self):

		return self.root

class CatRoot(resource.DirectoryResource):

	def __init__(self, resourceId, resourceLocation):

		resource.DirectoryResource.__init__(self, resourceId, resourceLocation, "Soundcloud Users")

		catAll = Category(2, "all", "all")
		catAll.setMeta({"directory" : "all"})		

		catFav = Category(3, "favorites", "favorites")
		catFav.setMeta({"directory" : "favorites"})
		catFav.addChild(UserRoot(4, "http://www.soundcloud.com/users"))

		self.addChild(catAll)
		self.addChild(catFav)

class Category(resource.DirectoryResource):

	pass

class Root(resource.DirectoryResource):

	def __init__(self, resourceId, resourceLocation):

		resource.DirectoryResource.__init__(self, resourceId, resourceLocation, "Soundcloud Users")

		self.children = None 

	def getAllChildren(self):

		if self.children == None:
			self.retriveChildren()

		return self.children
		
	def retriveChildren(self):

		self.children = []

		for uri in ResourceProvider.favorites:

			try:
				user = ResourceProvider.sc.get("/users/" + uri)
				u = User(user.id, user.uri, user.permalink, user.username)				
				u.setMeta({"directory" : user.permalink})		
				self.addChild(u)
				logging.info("successfully retrieved data for URI %s: id=%d; name=%s" % 
					(uri, user.id, user.permalink))
			except Exception as e:
				logging.warn("Unable to retrive data for URI %s" % uri)

class User(resource.DirectoryResource):

	artist = None

	def __init__(self, resourceId, resourceLocation, name, artist):

		self.artist = artist

		resource.DirectoryResource.__init__(self, resourceId, resourceLocation, name)

		self.children = None 

	def getAllChildren(self):

		if self.children == None:
			self.retriveChildren()

		return self.children
	
	def retriveChildren(self):

		self.children = []

		try:
			logging.debug("Trying to get tracks for user [%s] with uri [%s]" % (self.name, self.location))
			tracks = ResourceProvider.sc.get(self.location + "/tracks")

			for track in tracks:
				tr = Track(track.id, track.stream_url, track.permalink)
				tr.setMeta({
					"file" : self.name + "/" + track.permalink,
					"Artist" : self.artist, 
					"Title" : track.title, 
					"Time" : track.duration})
				self.addChild(tr)

				logging.debug("Added tracki to use [%s]: %s" % (self.getName(), tr.__str__()))

		except Exception as e:
			logging.warn("Unable to retrive tracks for [%s]" % self.getName())
	
		logging.info("successfully retrieved %d tracks for user [%s]" % (len(self.children), self.getName()))

class Track(resource.FileResource):

	def getStreamUri(self):
		
		stream_url = ResourceProvider.sc.get(self.location, allow_redirects=False)
		logging.debug("Stream url for URI %s is %s" % (self.location, stream_url.location))
		return stream_url.location

