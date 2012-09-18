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
import gst
import pyscmpd.resource as resource

class GstPlayer(resource.DirectoryResource):

	player 			= None 
	playlistVersion = 0
	
	def __init__(self):	

		resource.DirectoryResource.__init__(self, 0, None, "Current Playlist")

		self.player = gst.element_factory_make("playbin", "player")

	def addChild(self, child):

		if not child.getType() == resource.Resource.TYPE_FILE:
			logging.error("Only file resources allowed for playlists. Got: %s" % child.__str__())
			return

		self.playlistVersion = self.playlistVersion + 1

		self.children.append(child)


	def play(self, filePos=0):

		if filePos > len(self.children): 
			logging.error("Invalid filePos (%d) given. Only %d files in current playlist." % 
				(filePos, len(self.children)))
			return 

		f = self.children[filePos]

		logging.info("Playing file at playlist pos %d: %s" % (filePos, f.__str__()))

		self.player.set_state(gst.STATE_NULL)
		self.player.set_property('uri', f.getStreamUri())
		self.player.set_state(gst.STATE_PLAYING)

	def playId(self, fileId):

		p = 0

		for c in self.children:
			if c.getId() == fileId:
				self.play(p)
				return

			p = p + 1

		logging.info("No file with id [%d] in playlist" % fileId)
		
	def stop(self):

		self.player.set_state(gst.STATE_NULL)
		logging.info("Player stopped")
