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
import pyscmpd.resource.core as core

class GstPlayer(core.DirectoryResource):

	player 		= None 
	
	def __init__(self):	

		core.DirectoryResource.__init__(self, 0, None, "Current Playlist")

		self.player = gst.element_factory_make("playbin", "player")

	def addChild(self, child):

		if not child.getType() == core.Resource.TYPE_FILE:
			logging.error("Only file resources allowed for playlists. Got: %s" % child.__str__())
			return

		self.children.append(child)


	def play(self, filePos=0):

		if filePos > len(self.children): 
			logging.error("Invalid filePos (%d) given. Only %d files in current playlist." % (filePos, len(self.children)))
			return 

		f = self.children[filePos]

		logging.info("Playing file at playlist pos %d: %s" % (filePos, f.__str__()))

		self.player.set_state(gst.STATE_NULL)
		self.player.set_property('uri', f.getStreamUri())
		self.player.set_state(gst.STATE_PLAYING)


	def stop(self):

		self.player.set_state(gst.STATE_NULL)
		logging.info("Player stopped")
