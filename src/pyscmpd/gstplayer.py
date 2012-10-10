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
import os

import pyscmpd.resource as resource
import pyscmpd.respersist as persist

from config import *

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

		logging.info("Playing file at playlist pos %d: %s" % (filePos, f.getName()))

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

		cur = self.currentSong()
		c 	= self.children[filePos]

		if not cur == None and cur.getId() == c.getId():
			self.stop()

		self.delChild(c)

		# update position of current song
		if self.currentSongNumber > -1:
			self.currentSongNumber = self.getResourcePosInPlaylist(
				cur,
				self.children)

	def deleteId(self, fileId):

		cur = self.currentSong()

		for c in self.children:
			if c.getId() == fileId:

				if not cur == None and cur.getId() == c.getId():
					self.stop()

				self.delChild(c)

				# update position of current song
				if self.currentSongNumber > -1:
					self.currentSongNumber = self.getResourcePosInPlaylist(
						cur,
						self.children)

				return

		logging.error("No file with id [%d] in playlist" % fileId)

	def getResourcePosInPlaylist(self, res, playlist):

		p = 0 

		for r in playlist:
	
			if res.getId() == r.getId():
				return p

			p = p + 1 

		return -1

	def getIdPosInPlaylist(self, resId, playlist):

		p = 0 

		for r in playlist:
	
			if resId == r.getId():
				return p

			p = p + 1 

		return -1

	def move(self, filePosFrom, filePosTo):

		logging.debug("Move posFrom %d, posTo %d" % (filePosFrom, filePosTo))

		if filePosFrom > len(self.children): 
			logging.error("Invalid filePosFrom (%d) given. Only %d files in current playlist." % 
				(filePosFrom, len(self.children)))
			return 

		if filePosTo > len(self.children): 
			logging.error("Invalid filePosTo (%d) given. Only %d files in current playlist." % 
				(filePosTo, len(self.children)))
			return 

		# work on local copy
		children = self.children[:]

		c = children[filePosFrom]

		logging.debug("File on posFrom: %s" % c.__str__())

		children.remove(c)
		children.insert(filePosTo, c)

		# update position of current song
		if self.currentSongNumber > -1:
			self.currentSongNumber = self.getResourcePosInPlaylist(
				self.currentSong(),
				children)

		self.children = children
		self.playlistVersion = self.playlistVersion + 1

	def moveId(self, fileIdFrom, filePosTo):
		
		if fileIdFrom <= resource.ID_OFFSET:

			logging.debug("Using moveId/move mixup workaround")

			# I think client is doing wrong and mixes up moveId with move
			# (ncmpcpp does this). Anyway, trying to workaorund this ...
			self.move(fileIdFrom, filePosTo)

		else:

			logging.debug("moveId idFrom %d, posTo %d" % (fileIdFrom, filePosTo))

			if filePosTo > len(self.children): 
				logging.error("Invalid filePosTo (%d) given. Only %d files in current playlist." % 
					(filePosTo, len(self.children)))
				return 

			# work on local copy
			children = self.children[:]

			for c in self.children:
				if c.getId() == fileIdFrom:

					children.remove(c)
					children.insert(filePosTo, c)

					# update position of current song
					if self.currentSongNumber > -1:
						self.currentSongNumber = self.getResourcePosInPlaylist(
							self.currentSong(),
							children)

					self.children = children
					self.playlistVersion = self.playlistVersion + 1
					return

			logging.error("No file with id [%d] in playlist" % fileIdFrom)

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

	def duration(self):

		c = self.currentSong()

		return int(c.getMeta("Time") / 1000)
			
	def elapsedTime(self):

		p = 0
		
		try:
			p = int(self.player.query_position(gst.FORMAT_TIME, None)[0] / 1000000000)
		except:
			pass

		return p

	def setVolume(self, percent):
		p = percent / 100.0 + 0.005
		logging.debug("Setting volume to %f" % p)
		self.player.set_property('volume', p)

	def getVolume(self):
		return int(self.player.get_property('volume') * 100)
		
	def storePlaylist(self, plName = CURR_PLAYLIST_KEY):

		logging.info("Storing playlist with key: %s" % plName)
		
		p = persist.ResourceFilePersistence(PLAYLIST_DIR)
		p.store(plName, self.children)

	def retrivePlaylist(self, plName = CURR_PLAYLIST_KEY, makeCurrent = True):

		logging.info("Retriving playlist with key: %s" % plName)

		self.stop()
		self.currentSongNumber = -1 
		self.currentSongId = -1 

		p = persist.ResourceFilePersistence(PLAYLIST_DIR)
		c = p.retrive(plName)
			
		if not c == None and makeCurrent:
			self.children = c
			self.playlistVersion = self.playlistVersion + 1

		return c

	def listPlaylists(self):
	
		plFiles = []

		try:
			for (root, dirs, files) in os.walk(PLAYLIST_DIR):

				logging.debug("Found playlist files: %s" % files)

				for f in files: 
					plFiles.append(f)
			
			return plFiles 

		except Exception as e:
			logging.warn("Unable to retrive playlists: %s" % `e`)

		return plFiles 
