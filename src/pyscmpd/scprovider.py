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

class Root(resource.DirectoryResource):

	def __init__(self, resourceId, resourceLocation):

		resource.DirectoryResource.__init__(self, resourceId, resourceLocation, "Soundcloud Users")

		for uri in ResourceProvider.ROOT_USERS:

			try:
				user = ResourceProvider.sc.get(uri)
				u = User(user.id, user.uri, user.permalink, user.username)				
				u.setMeta({"directory" : user.permalink})		
				self.addChild(u)
				logging.debug("successfully retrieved data for URI %s: id=%d; name=%s" % (uri, user.id, user.permalink))
			except Exception as e:
				logging.warn("Unable to retrive data for URI %s" % uri)


class User(resource.DirectoryResource):

	def __init__(self, resourceId, resourceLocation, name, artist):

		resource.DirectoryResource.__init__(self, resourceId, resourceLocation, name)

		# TODO: do not load in advance, but use lazy loading when first call to "getAllChildren" is made
		try:
			logging.debug("Trying to get tracks for user [%s]" % name)
			tracks = ResourceProvider.sc.get(self.location + "/tracks")

			for track in tracks:
				tr = Track(track.id, track.stream_url, track.permalink)
				tr.setMeta({
					"file" : name + "/" + track.permalink,
					"Artist" : artist, 
					"Title" : track.title, 
					"Time" : track.duration})
				self.addChild(tr)
				logging.debug("Added tracki to user [%s]: %s" % (self.getName(), tr.__str__()))

		except Exception as e:
			logging.warn("Unable to retrive tracks for [%s]" % self.getName())
	
		logging.info("successfully retrieved %d tracks for user [%s]" % (len(self.children), self.getName()))


class Track(resource.FileResource):

	def getStreamUri(self):
		
		stream_url = ResourceProvider.sc.get(self.location, allow_redirects=False)
		logging.debug("Stream url for URI %s is %s" % (self.location, stream_url.location))
		return stream_url.location


class ResourceProvider:

	ROOT_USERS = None 

	sc 		= None 
	root 	= None

	def __init__(self, useCache = False, cacheFile = "scroot.cache"):

		ResourceProvider.sc = soundcloud.Client(client_id='aa13bebc2d26491f7f8d1e77ae996a64')

		if useCache:

			try:
				f = open(cacheFile, 'rb')
				self.root = pickle.load(f)		
				f.close()
				logging.info("Cache file [%s] read" % cacheFile)
				return
			except:
				logging.warn("Unable to read cache file [%s], creating new" % cacheFile)	


		self.root = Root(1, "http://www.soundcloud.com")

		try:
			f = open(cacheFile, 'wb')
			pickle.dump(self.root, f)		
			f.close()
			logging.info("Cache file [%s] written" % cacheFile)
		except:
			logging.warn("Unable to write cache file [%s]" % cacheFile)	


	def getRoot(self):

		return self.root
