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

import pyscmpd.resource.core as core

class Root(core.DirectoryResource):

	def __init__(self, resourceId, resourceLocation):

		core.DirectoryResource.__init__(self, resourceId, resourceLocation, "Soundcloud Users")

		for uri in ResourceProvider.ROOT_USERS:

			try:
				user = ResourceProvider.sc.get(uri)
				self.addChild(User(user.id, user.uri, user.username))
				logging.debug("successfully retrieved data for URI %s: id=%d; name=%s" %  (uri, user.id, user.username))
			except Exception as e:
				logging.warn("Unable to retrive data for URI %s" % uri)


class User(core.DirectoryResource):

	def __init__(self, resourceId, resourceLocation, name = "UNKNOWN"):

		core.DirectoryResource.__init__(self, resourceId, resourceLocation, name)

		# TODO: do not load in advance, but use lazy loading when first call to "getAllChildren" is made
		try:
			logging.debug("Trying to get tracks for user [%s]" % name)
			tracks = ResourceProvider.sc.get(self.location + "/tracks")

			for track in tracks:
				tr = Track(track.id, track.stream_url, track.title)
				tr.setMeta({"Artist" : name, "Title" : track.title})
				self.addChild(tr)
				logging.debug("Added tracki to user [%s]: %s" % (self.getName(), tr.__str__()))

		except Exception as e:
			logging.warn("Unable to retrive tracks for [%s]" % self.getName())
	
		logging.info("successfully retrieved %d tracks for user [%s]" % (len(self.children), self.getName()))


class Track(core.FileResource):

	def getStreamUri(self):
		
		stream_url = ResourceProvider.sc.get(self.location, allow_redirects=False)
		logging.debug("Stream url for URI %s is %s" % (self.location, stream_url.location))
		return stream_url.location


class ResourceProvider:

	ROOT_USERS = None 

	sc 		= None 
	root 	= None

	def __init__(self):

		ResourceProvider.sc = soundcloud.Client(client_id='aa13bebc2d26491f7f8d1e77ae996a64')

		self.root = Root(1, "http://www.soundcloud.com")

	def getRoot(self):

		return self.root
