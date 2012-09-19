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

	player 				= None 
	bus					= None
	playlistVersion 	= 0
	playerStatus		= "stop"	
	currentSongNumber 	= -1
	currentSongId 		= -1

	def __init__(self):	

		resource.DirectoryResource.__init__(self, 0, None, "Current Playlist")

		self.player = gst.element_factory_make("playbin", "player")
		
		self.bus = self.player.get_bus()
		self.bus.enable_sync_message_emission()
		self.bus.add_signal_watch()
		self.bus.connect('message::eos', self.onEos)

	def addChild(self, child):

		if not child.getType() == resource.Resource.TYPE_FILE:
			logging.error("Only file resources allowed for playlists. Got: %s" % child.__str__())
			return

		self.children.append(child)
		self.playlistVersion = self.playlistVersion + 1

	def delChild(self, child):	
	
		resource.DirectoryResource.delChild(self, child)
		self.playlistVersion = self.playlistVersion + 1

	def delAllChildren(self):

		resource.DirectoryResource.delAllChildren(self)
		self.playlistVersion = self.playlistVersion + 1

		self.currentSongNumber = -1 
		self.currentSongId = -1 

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
		self.playerStatus = "play"

		self.currentSongNumber = filePos
		self.currentSongId = f.getId()
 
	def playId(self, fileId):

		p = 0

		for c in self.children:
			if c.getId() == fileId:
				self.play(p)
				self.currentSongNumber = p 
				self.currentSongId = fileId 
				return

			p = p + 1

		logging.error("No file with id [%d] in playlist" % fileId)

	def currentSong(self):

		if self.currentSongNumber < 0 or self.currentSongNumber >= len(self.children):
			return None

		return self.children[self.currentSongNumber] 

	def delete(self, filePos):

		if filePos > len(self.children): 
			logging.error("Invalid filePos (%d) given. Only %d files in current playlist." % 
				(filePos, len(self.children)))
			return 

		c = self.children[filePos]
		self.delChild(c)

	def deleteId(self, fileId):

		for c in self.children:
			if c.getId() == fileId:
				self.delChild(c)
				return

		logging.error("No file with id [%d] in playlist" % fileId)

	def move(self, filePosFrom, filePosTo):

		logging.info("move posFrom %d, posTo %d" % (filePosFrom, filePosTo))

		if filePosFrom > len(self.children): 
			logging.error("Invalid filePosFrom (%d) given. Only %d files in current playlist." % 
				(filePosFrom, len(self.children)))
			return 

		if filePosTo > len(self.children): 
			logging.error("Invalid filePosTo (%d) given. Only %d files in current playlist." % 
				(filePosTo, len(self.children)))
			return 

		c = self.children[filePosFrom]

		logging.info("File on posFrom: %s" % c.__str__())

		self.children.remove(c)
		self.children.insert(filePosTo, c)
		self.playlistVersion = self.playlistVersion + 1

	def moveId(self, fileIdFrom, filePosTo):
		
		self.move(fileIdFrom, filePosTo)

		'''
		logging.info("moveId idFrom %d, posTo %d" % (fileIdFrom, filePosTo))

		if filePosTo > len(self.children): 
			logging.error("Invalid filePosTo (%d) given. Only %d files in current playlist." % 
				(filePosTo, len(self.children)))
			return 

		for c in self.children:
			if c.getId() == fileIdFrom:
				self.children.insert(filePosTo, c)
				self.delChild(c)
				return

		logging.error("No file with id [%d] in playlist" % fileIdFrom)
		'''

	def pause(self):

		if self.playerStatus == "pause":
			self.player.set_state(gst.STATE_PLAYING)
			logging.info("Player resumed")
			self.playerStatus = "play"
		else:
			self.player.set_state(gst.STATE_PAUSED)
			logging.info("Player paused")
			self.playerStatus = "pause"

	def stop(self):

		self.player.set_state(gst.STATE_NULL)
		logging.info("Player stopped")
		self.playerStatus = "stop"

		self.currentSongNumber = -1 
		self.currentSongId = -1 

	def next(self):

		if self.playerStatus == "pause" or self.playerStatus == "play" :

			if self.currentSongNumber + 1 < len(self.children):
				self.play(self.currentSongNumber + 1)
			else:
				self.play()	

	def previous(self):

		if self.playerStatus == "pause" or self.playerStatus == "play" :

			if self.currentSongNumber - 1 >= 0:
				self.play(self.currentSongNumber - 1)
			else:
				self.play(len(self.children) - 1)

	def onEos(self, bus, msg):
		logging.info("EOS, playing next stream in playlist")
		self.next()	

