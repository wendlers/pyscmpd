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
import soundcloud 

import pyscmpd.resource as resource

from threading import Lock

class ResourceProvider:

	sc 			= None 
	root 		= None

	def __init__(self, favoriteUsers, favoriteGroups):

		ResourceProvider.sc = soundcloud.Client(client_id='aa13bebc2d26491f7f8d1e77ae996a64')

		self.root = Root(favoriteUsers, favoriteGroups)

	def getRoot(self):

		return self.root

class Root(resource.DirectoryResource):

	def __init__(self, favoriteUsers, favoriteGroups):

		resource.DirectoryResource.__init__(self, 0, "pyscmpd", "pyscmpd")

		uall = Users("random-users")

		ufavgrp = "favorite-users"
		ufav = resource.DirectoryResource(0, ufavgrp, ufavgrp )
		ufav.setMeta({"directory" : ufavgrp})		

		for fav in favoriteUsers:
			f = FavoriteUsers(fav["name"], fav["users"], ufavgrp)		
			ufav.addChild(f)

		grps = Groups("random-groups")


		gfavgrp = "favorite-groups"
		gfav = resource.DirectoryResource(0, gfavgrp, gfavgrp )
		gfav.setMeta({"directory" : gfavgrp})		

		for fav in favoriteGroups:
			logging.info("Adding favorite group: %s" % fav)
			f = FavoriteGroup(fav, gfavgrp)
			gfav.addChild(f)

		self.addChild(ufav)
		self.addChild(uall)
		self.addChild(grps)
		self.addChild(gfav)

class Users(resource.DirectoryResource):

	retriveLock = None

	def __init__(self, category):

		resource.DirectoryResource.__init__(self, 0, category, category)

		self.setMeta({"directory" : category})		

		self.children = None 
		self.retriveLock = Lock()

	def getAllChildren(self):

		self.retriveLock.acquire()

		if self.children == None:
			self.retriveChildren()

		self.retriveLock.release()

		return self.children
		
	def retriveChildren(self):

		self.children = []

		try:
			allUsers = ResourceProvider.sc.get("/users")

			for user in allUsers:

				try:

					u = User(resource.ID_OFFSET + user.id, user.uri, user.permalink, 
						user.username, self.name)
					u.setMeta({"directory" : self.name + "/" + user.permalink})		

					self.addChild(u)

					logging.info("successfully retrieved data for URI %s: id=%d; name=%s" % 
						(user.uri, u.getId(), user.permalink))

				except Exception as e:
					logging.warn("Unable to retrive data for URI %s: %s" % (uri, `e`))
		
		except Exception as e:
			logging.warn("Unable to retrive data for URI users: %s" % `e`)

class FavoriteUsers(resource.DirectoryResource):

	retriveLock = None
	users 		= None
	category	= None

	def __init__(self, name, users, category):

		logging.info("Adding new favorites folder [%s] with users [%s]" %
			(name, users))

		resource.DirectoryResource.__init__(self, 0, name, name)

		self.category	 = category
		self.children 	 = None 
		self.users 		 = users
		self.retriveLock = Lock()

		self.setMeta({"directory" : self.category + "/" + self.name})

	def getAllChildren(self):

		self.retriveLock.acquire()

		if self.children == None:
			self.retriveChildren()

		self.retriveLock.release()

		return self.children
		
	def retriveChildren(self):

		self.children = []

		for uri in self.users:

			try:

				user = ResourceProvider.sc.get("/users/" + uri)
				u = User(resource.ID_OFFSET + user.id, user.uri, user.permalink, user.username, 
					self.category + "/" + self.name)
				u.setMeta({"directory" : self.category + "/" + self.name + "/" + user.permalink})		
				self.addChild(u)

				logging.info("successfully retrieved data for URI %s: id=%d; name=%s" % 
					(uri, u.getId(), user.permalink))

			except Exception as e:
				logging.warn("Unable to retrive data for URI %s: %s" % (uri, `e`))

class FavoriteGroup(resource.DirectoryResource):

	retriveLock = None
	category	= None

	def __init__(self, name, category):

		resource.DirectoryResource.__init__(self, 0, name, name)

		self.category	 = category
		self.children 	 = None 
		self.retriveLock = Lock()

		self.setMeta({"directory" : self.category + "/" + self.name})

	def getAllChildren(self):

		self.retriveLock.acquire()

		if self.children == None:
			self.retriveChildren()

		self.retriveLock.release()

		return self.children
		
	def retriveChildren(self):

		self.children = []

		try:

			group = ResourceProvider.sc.get("/resolve", url="http://soundcloud.com/groups/%s" %
					self.name)

			users = ResourceProvider.sc.get("/groups/%d/users" % group.id)

			for user in users:
				u = User(resource.ID_OFFSET + user.id, user.uri, user.permalink, 
					user.username, self.category + "/" + self.name)
				u.setMeta({"directory" : self.category + "/" + self.name + "/" + user.permalink})		
				self.addChild(u)

				logging.info("successfully retrieved user data: id=%d; name=%s" % 
					(u.getId(), user.permalink))

		except Exception as e:
			logging.warn("Unable to retrive data for groups: %s" % `e`)


class Groups(resource.DirectoryResource):

	retriveLock = None
	category	= None

	def __init__(self, category):

		resource.DirectoryResource.__init__(self, 0, category, category)

		self.category	 = category
		self.children 	 = None 
		self.retriveLock = Lock()

		self.setMeta({"directory" : self.category})

	def getAllChildren(self):

		self.retriveLock.acquire()

		if self.children == None:
			self.retriveChildren()

		self.retriveLock.release()

		return self.children
		
	def retriveChildren(self):

		self.children = []

		try:
				
			groups = ResourceProvider.sc.get("/groups")

			for group in groups:
				logging.info("processing group %s" % group.permalink)
				g = Group(resource.ID_OFFSET + group.id, group.permalink, self.category)
				g.setMeta({"directory" : self.category + "/" + group.permalink})		
				self.addChild(g)

				logging.info("successfully retrieved data for URI %s: id=%d; name=%s" % 
					(group.uri, g.getId(), group.permalink))

		except Exception as e:
			logging.warn("Unable to retrive data for groups: %s" % `e`)

class Group(resource.DirectoryResource):

	retriveLock = None
	users 		= None
	category	= None

	def __init__(self, groupId, name, category):

		logging.info("Adding new group folder [%s]" % name)

		resource.DirectoryResource.__init__(self, groupId, name, name)

		self.category	 = category
		self.children 	 = None 
		self.retriveLock = Lock()

		self.setMeta({"directory" : self.category + "/" + self.name})

	def getAllChildren(self):

		self.retriveLock.acquire()

		if self.children == None:
			self.retriveChildren()

		self.retriveLock.release()

		return self.children
		
	def retriveChildren(self):

		self.children = []
		groupId = self.getId() - resource.ID_OFFSET

		try:
			users = ResourceProvider.sc.get("/groups/%d/users" % groupId)

			for user in users:
				u = User(resource.ID_OFFSET + user.id, user.uri, user.permalink, user.username, self.category + "/" + self.name)
				u.setMeta({"directory" : self.category + "/" + self.name + "/" + user.permalink})		
				self.addChild(u)

				logging.info("successfully retrieved user data: id=%d; name=%s" % 
					(u.getId(), user.permalink))

		except Exception as e:
			logging.warn("Unable to retrive data for group %d: %s" % (groupId, `e`))

class User(resource.DirectoryResource):

	retriveLock = None
	artist 		= None
	category 	= None

	def __init__(self, resourceId, resourceLocation, name, artist, category):

		self.artist 	= artist
		self.category 	= category

		resource.DirectoryResource.__init__(self, resourceId, resourceLocation, name)

		self.children 	 = None 
		self.retriveLock = Lock()

	def getAllChildren(self):

		self.retriveLock.acquire()

		if self.children == None:
			self.retriveChildren()

		self.retriveLock.release()

		return self.children
	
	def retriveChildren(self):

		self.children = []

		try:

			logging.debug("Trying to get tracks for user [%s] with uri [%s]" % (self.name, self.location))
			tracks = ResourceProvider.sc.get(self.location + "/tracks")

			for track in tracks:
				tr = Track(resource.ID_OFFSET + track.id, track.stream_url, track.permalink)
				tr.setMeta({
					"file" : self.category + "/" + self.name + "/" + track.permalink,
					"Artist" : self.artist, 
					"Title" : track.title, 
					"Time" : track.duration})

				self.addChild(tr)

				logging.info("Added track to use [%s]: %s" % (self.getName(), tr.__str__()))

		except Exception as e:

			logging.warn("Unable to retrive tracks for [%s]" % self.getName())
	
		logging.info("successfully retrieved %d tracks for user [%s]" % (len(self.children), self.getName()))

class Track(resource.FileResource):

	def getStreamUri(self):
		
		stream_url = ResourceProvider.sc.get(self.location, allow_redirects=False)
		logging.debug("Stream url for URI %s is %s" % (self.location, stream_url.location))
		return stream_url.location

