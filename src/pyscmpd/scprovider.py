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

	# favorites 	= None 
	sc 			= None 
	root 		= None

	def __init__(self, favorites):

		ResourceProvider.sc = soundcloud.Client(client_id='aa13bebc2d26491f7f8d1e77ae996a64')

		self.root = Root(favorites)

	def getRoot(self):

		return self.root

class Root(resource.DirectoryResource):

	def __init__(self, favorites):

		resource.DirectoryResource.__init__(self, 0, "pyscmpd", "pyscmpd")

		uall = RandomUsers(2)
		uall.setMeta({"directory" : "random"})		

		i = 1

		for fav in favorites:
			ufav = Favorites(i, fav["name"], fav["users"])
			self.addChild(ufav)
			i = i + 1 

		self.addChild(uall)


class RandomUsers(resource.DirectoryResource):

	def __init__(self, resourceId):

		resource.DirectoryResource.__init__(self, resourceId, "random", "random")

		self.children = None 

	def getAllChildren(self):

		if self.children == None:
			self.retriveChildren()

		return self.children
		
	def retriveChildren(self):

		self.children = []

		allUsers = ResourceProvider.sc.get("/users")

		for user in allUsers:

			try:

				u = User(user.id, user.uri, user.permalink, user.username, self.name)				
				u.setMeta({"directory" : self.name + "/" + user.permalink})		

				self.addChild(u)

				logging.info("successfully retrieved data for URI %s: id=%d; name=%s" % 
					(user.uri, user.id, user.permalink))

			except Exception as e:
				logging.warn("Unable to retrive data for URI %s" % uri)

class Favorites(resource.DirectoryResource):

	users = None

	def __init__(self, resourceId, name, users):

		logging.info("Adding new favorites folder [%s] with users [%s]" %
			(name, users))

		resource.DirectoryResource.__init__(self, resourceId, name, name)

		self.setMeta({"directory" : name})

		self.children 	= None 
		self.users 		= users

	def getAllChildren(self):

		if self.children == None:
			self.retriveChildren()

		return self.children
		
	def retriveChildren(self):

		self.children = []

		# for uri in ResourceProvider.favorites:
		for uri in self.users:

			try:

				user = ResourceProvider.sc.get("/users/" + uri)
				u = User(user.id, user.uri, user.permalink, user.username, self.name)				
				u.setMeta({"directory" : self.name + "/" + user.permalink})		

				self.addChild(u)

				logging.info("successfully retrieved data for URI %s: id=%d; name=%s" % 
					(uri, user.id, user.permalink))

			except Exception as e:
				logging.warn("Unable to retrive data for URI %s" % uri)

class User(resource.DirectoryResource):

	artist 		= None
	category 	= None

	def __init__(self, resourceId, resourceLocation, name, artist, category):

		self.artist 	= artist
		self.category 	= category

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
					"file" : self.category + "/" + self.name + "/" + track.permalink,
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

