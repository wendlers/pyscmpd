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
	reqLimit	= 200
	reqMaxitems	= 1000 

	def __init__(self, favoriteUsers, favoriteGroups, favoriteFavorites, maxitems):

		if ResourceProvider.reqLimit > maxitems:
			ResourceProvider.reqLimit = maxitems

		ResourceProvider.reqMaxitems = maxitems 

		logging.info("Retriving a maximum of %d items per scapi request" % ResourceProvider.reqMaxitems)
		ResourceProvider.sc = soundcloud.Client(client_id='aa13bebc2d26491f7f8d1e77ae996a64')

		self.root = Root(favoriteUsers, favoriteGroups, favoriteFavorites)

	def getRoot(self):

		return self.root

class Root(resource.DirectoryResource):

	def __init__(self, favoriteUsers, favoriteGroups, favoriteFavorites):

		resource.DirectoryResource.__init__(self, 0, "pyscmpd", "pyscmpd")

		self.__populateFavoriteUsers(favoriteUsers)
		self.__populateFavoriteGroups(favoriteGroups)
		self.__populateFavoriteFavorites(favoriteFavorites)
		self.__populateRandom()

	def __populateFavoriteUsers(self, favoriteUsers):

		ufavgrp = "users"
		ufav = resource.DirectoryResource(0, ufavgrp, ufavgrp)
		ufav.setMeta({"directory" : ufavgrp})		

		for fav in favoriteUsers:
			f = FavoriteUsers(fav["name"], fav["users"], ufavgrp)		
			ufav.addChild(f)

		self.addChild(ufav)

	def __populateFavoriteGroups(self, favoriteGroups):

		gfavgrp = "groups"
		gfav = resource.DirectoryResource(0, gfavgrp, gfavgrp)
		gfav.setMeta({"directory" : gfavgrp})		

		for fav in favoriteGroups:

			logging.info("Adding new favorites folder [%s] with groups [%s]" %
				(fav["name"], fav["groups"]))

			d = resource.DirectoryResource(0, gfavgrp + "/" + fav["name"], fav["name"])
			d.setMeta({"directory" : gfavgrp + "/" + fav["name"]})		

			for group in fav["groups"]:
				g = Group(-1, group, gfavgrp + "/" + fav["name"])
				d.addChild(g)
			
			gfav.addChild(d)

		self.addChild(gfav)

	def __populateFavoriteFavorites(self, favoriteFavorites):

		ffavgrp = "favorites"
		ffav = resource.DirectoryResource(0, ffavgrp, ffavgrp)
		ffav.setMeta({"directory" : ffavgrp})		

		for fav in favoriteFavorites:
			
			logging.info("Adding new favorites folder [%s] with favorites [%s]" %
				(fav["name"], fav["users"]))

			d = resource.DirectoryResource(0, ffavgrp + "/" + fav["name"], fav["name"])
			d.setMeta({"directory" : ffavgrp + "/" + fav["name"]})		

			for user in fav["users"]:
				u = User(0, "/users/" + user + "/favorites", user, user, ffavgrp + "/" + fav["name"])
				u.setMeta({"directory" : ffavgrp + "/" + fav["name"] + "/" + user})		
				d.addChild(u)

			ffav.addChild(d)

		self.addChild(ffav)

	def __populateRandom(self):

		d = resource.DirectoryResource(0, "random", "random")
		d.setMeta({"directory" : "random"})		
		d.addChild(RandomGroups("random", "groups"))
		d.addChild(RandomUsers("random", "users"))

		self.addChild(d)

class FavoriteUsers(resource.DirectoryResource):

	retriveLock 	= None
	users 			= None
	category		= None

	def __init__(self, name, users, category):

		logging.info("Adding new favorites folder [%s] with users [%s]" %
			(name, users))

		resource.DirectoryResource.__init__(self, 0, name, name)
		self.setMeta({"directory" : category + "/" + name})

		self.category	 = category
		self.children 	 = None 
		self.users 		 = users
		self.retriveLock = Lock()

	def getAllChildren(self):

		self.retriveLock.acquire()

		if self.children == None:
			self.retriveChildren()

		self.retriveLock.release()

		return self.children
		
	def retriveChildren(self):

		children = []

		for uname in self.users:

			try:

				user = ResourceProvider.sc.get("/users/" + uname)

				u = User(resource.ID_OFFSET + user.id, user.uri + "/tracks", user.permalink, user.username, 
					self.category + "/" + self.name)

				u.setMeta({"directory" : self.category + "/" + self.name + "/" + user.permalink})		
				
				children.append(u)

				logging.info("Successfully retrieved data for URI %s: id=%d; name=%s" % 
					(uname, u.getId(), user.permalink))
			
			except Exception as e:
				logging.warn("Unable to retrive data for URI %s: %s" % (uname, `e`))

		self.children = children

class RandomGroups(resource.DirectoryResource):
	
	retriveLock = None
	category    = None

	def __init__(self, category, name):

		resource.DirectoryResource.__init__(self, 0, category, name)

		self.category    = category
		self.children    = None
		self.retriveLock = Lock()

		self.setMeta({"directory" : self.category + "/" + name})

	def getAllChildren(self):

		self.retriveLock.acquire()

		if self.children == None:
			self.retriveChildren()

		self.retriveLock.release()

		return self.children

	def retriveChildren(self):

		self.children = []

		try:

			lim = ResourceProvider.reqLimit
			off = 0

			while True:

				logging.info("Requesting page with limit=%d; offset=%d" % (lim, off))
				groups = ResourceProvider.sc.get("/groups", limit=lim, offset=off)

				if len(groups) == 0:
					break

				for group in groups:

					logging.info("processing group %s" % group.permalink)

					g = Group(resource.ID_OFFSET + group.id, group.permalink, 
							self.category + "/" + self.name)
					g.setMeta({"directory" : self.category + "/" + self.name + "/" 
						+ group.permalink})
					self.addChild(g)

					logging.info("successfully retrieved data for URI %s: id=%d; name=%s" %
						(group.uri, g.getId(), group.permalink))

				off = off + lim

				if off >= ResourceProvider.reqMaxitems:
					logging.info("Maximum request offset exceeded limit of %d. Ending this request." % 
						ResourceProvider.reqMaxitems)
					break

		except Exception as e:
			logging.warn("Unable to retrive data for groups: %s" % `e`)

class RandomUsers(resource.DirectoryResource):

	category = None
	retriveLock = None

	def __init__(self, category, name):

		resource.DirectoryResource.__init__(self, 0, category, name)

		self.setMeta({"directory" : category + "/" + name})

		self.category = category
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

			lim = ResourceProvider.reqLimit
			off = 0

			while True:

				logging.info("Requesting page with limit=%d; offset=%d" % (lim, off))

				allUsers = ResourceProvider.sc.get("/users", limit=lim, offset=off)

				if len(allUsers) == 0:
					break

				for user in allUsers:
					
					try:

						u = User(resource.ID_OFFSET + user.id, user.uri + "/tracks", user.permalink,
							user.username, self.category + "/" + self.name)
						u.setMeta({"directory" : self.category + "/" + self.name + "/" + user.permalink})

						self.addChild(u)

						logging.info("successfully retrieved data for URI %s: id=%d; name=%s" %
							(user.uri, u.getId(), user.permalink))

					except Exception as e:
						logging.warn("Unable to retrive data for user: %s" % `e`)

				off = off + lim

				if off >= ResourceProvider.reqMaxitems:
					logging.info("Maximum request offset exceeded limit of %d. Ending this request." % 
						ResourceProvider.reqMaxitems)
					break

		except Exception as e:
			logging.warn("Unable to retrive data for URI users: %s" % `e`)

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

		children = []

		try:

			if self.getId() == -1:
				group = ResourceProvider.sc.get("/resolve", 
							url="http://soundcloud.com/groups/%s" %
							self.name)

				self.id = group.id 
				groupId = self.id
			else:
				groupId = self.getId() - resource.ID_OFFSET

			lim = ResourceProvider.reqLimit
			off = 0

			while True:

				logging.info("Requesting page with limit=%d; offset=%d" % (lim, off))

				users = ResourceProvider.sc.get("/groups/%d/users" % groupId, limit=lim, offset=off)

				if len(users) == 0:
					break

				for user in users:

					u = User(resource.ID_OFFSET + user.id, user.uri + "/tracks", user.permalink, 
							user.username, self.category + "/" + self.name)

					u.setMeta({"directory" : self.category + "/" + self.name + "/" + user.permalink})		

					children.append(u)

					logging.info("Successfully retrieved user data: id=%d; name=%s" % 
						(u.getId(), user.permalink))

				off = off + lim

				if off >= ResourceProvider.reqMaxitems:
					logging.info("Maximum request offset exceeded limit of %d. Ending this request." % 
						ResourceProvider.reqMaxitems)
					break

		except Exception as e:
			logging.warn("Unable to retrive data for group %d: %s" % (groupId, `e`))

		self.children = children

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

		children = []

		try:

			lim = ResourceProvider.reqLimit
			off = 0

			while True:

				logging.info("Requesting page with limit=%d; offset=%d" % (lim, off))

				tracks = ResourceProvider.sc.get(self.location, limit=lim, offset=off)

				if len(tracks) == 0:
					break

				for track in tracks:
					tr = Track(resource.ID_OFFSET + track.id, track.stream_url, track.permalink)
					tr.setMeta({
						"file" : self.category + "/" + self.name + "/" + track.permalink,
						"Artist" : self.artist, 
						"Title" : track.title, 
						"Time" : track.duration})

					children.append(tr)

					logging.debug("Added track to user [%s]: %s" % (self.getName(), track.title))

				off = off + lim

				if off >= ResourceProvider.reqMaxitems:
					logging.info("Maximum request offset exceeded limit of %d. Ending this request." % 
						ResourceProvider.reqMaxitems)
					break

		except Exception as e:

			logging.warn("Unable to retrive tracks for [%s]" % self.getName())
	
		logging.info("Retrieved %d tracks for user [%s]" % (len(children), self.getName()))

		self.children = children

class Track(resource.FileResource):

	def getStreamUri(self):
		
		stream_url = ResourceProvider.sc.get(self.location, allow_redirects=False)
		logging.debug("Stream url for URI %s is %s" % (self.location, stream_url.location))
		return stream_url.location

