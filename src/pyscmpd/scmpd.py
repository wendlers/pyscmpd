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
import mpdserver
import soundcloud

import pyscmpd.scprovider as provider 
import pyscmpd.gstplayer as gstplayer 

class ScMpdServerDaemon(mpdserver.MpdServerDaemon):

	scp 	= None
	scroot  = None
	player	= None
 
	def __init__(self, rootUsers, player, serverPort = 9900):
		
		provider.ResourceProvider.ROOT_USERS = rootUsers
 
		ScMpdServerDaemon.player 	= player
		ScMpdServerDaemon.scp 		= provider.ResourceProvider(True)
		ScMpdServerDaemon.scroot 	= ScMpdServerDaemon.scp.getRoot()

		mpdserver.MpdServerDaemon.__init__(self, serverPort)

		self.requestHandler.RegisterCommand(mpdserver.Outputs)
		self.requestHandler.RegisterCommand(Play)
		self.requestHandler.RegisterCommand(PlayId)
		self.requestHandler.RegisterCommand(Stop)
		self.requestHandler.RegisterCommand(LsInfo)
		self.requestHandler.RegisterCommand(Add)
		self.requestHandler.RegisterCommand(AddId)
		self.requestHandler.RegisterCommand(Clear)

		self.requestHandler.Playlist = MpdPlaylist

class Play(mpdserver.Play):

	def handle_args(self, songPos=0):

		ScMpdServerDaemon.player.play(songPos)

class PlayId(mpdserver.PlayId):

	def handle_args(self, songId=0):

		logging.debug("Playid %d" % songId)

		ScMpdServerDaemon.player.playId(songId)

class Stop(mpdserver.Command):

	def handle_args(self):

		ScMpdServerDaemon.player.stop()

class Clear(mpdserver.Command):

	def handle_args(self):

		logging.info("Clear playlist")

		ScMpdServerDaemon.player.stop()
		ScMpdServerDaemon.player.delAllChildren()

class LsInfo(mpdserver.LsInfo):

	currdir = None
	directory = None

	def handle_args(self, directory="/"):

		logging.info("List directory [%s]" % directory)

		if directory == "/":
			self.directory = None
		else:
			self.directory = directory
		
	def items(self):

		i = []
		path = ""

		if self.directory == None:
			r = ScMpdServerDaemon.scroot.getAllChildren()
		else:
			r = ScMpdServerDaemon.scroot.getChildByName(self.directory)
			path = r.getName()

			if r == None:
				return i	

			r = r.getAllChildren()

		for e in r:

			logging.debug("LsInfo sending item: %s/%s" % (path, e.__str__()))

			if e.getType() == 1:
				t = "directory"
			else:
				t = "file"
 
			if path == "":
				i.append((t, e.getMeta("directory")))
			else: 
				i.append((t, e.getMeta("file")))
				if e.getType() == 2:
					i.append(("Artist", e.getMeta("Artist")))
					i.append(("Title", e.getMeta("Title")))
					i.append(("Time", int(e.getMeta("Time") % 1000)))

		return i 

class Add(mpdserver.Add):

	def handle_args(self, song):

		logging.info("Adding song [%s] to playlist" % song) 

		(user, sep, track) = song.partition("/")

		if track == "":
			logging.error("Could not extract track from [%s]", song)
			return	

		u = ScMpdServerDaemon.scroot.getChildByName(user)

		if user == None:
			logging.error("Could not find directory for [%s]", user)
			return

		t = u.getChildByName(track)

		if t == None:
			logging.error("Track [%s] not found in directory [%s]" % (track, user))
			return

		ScMpdServerDaemon.player.addChild(t)
		
		logging.info("Successfully added song: %s" % t.__str__())

class AddId(mpdserver.AddId):

	uniqueId = 0

	def handle_args(self, song):

		logging.info("Adding song [%s] to playlist" % song) 

		(user, sep, track) = song.partition("/")

		if track == "":
			logging.error("Could not extract track from [%s]", song)
			return	

		u = ScMpdServerDaemon.scroot.getChildByName(user)

		if user == None:
			logging.error("Could not find directory for [%s]", user)
			return

		t = u.getChildByName(track)

		if t == None:
			logging.error("Track [%s] not found in directory [%s]" % (track, user))
			return

		ScMpdServerDaemon.player.addChild(t)
		
		logging.info("Successfully added song: %s" % t.__str__())

	def items(self):

		self.uniqueId = self.uniqueId + 1

		return [("id", self.uniqueId)]


class MpdPlaylist(mpdserver.MpdPlaylist):

    def songIdToPosition(self, songId):

		logging.info("Request to convert Id [%d] to position" % songId)
		return 0

    def handlePlaylist(self):

		# TODO: only recreate list if player indicates new playlist version

		pl 	= []
		i 	= 1
		c 	= ScMpdServerDaemon.player.getAllChildren()
		l 	= len(c)

		for t in c: 

			s = mpdserver.MpdPlaylistSong(
				artist = t.getMeta("Artist").encode('ASCII', 'ignore'), 
				title = t.getMeta("Title").encode('ASCII', 'ignore'), 
				file = t.getMeta("file").encode('ASCII', 'ignore'),
				track = "%d/%d" % (i, l),
				time = "%d" % (t.getMeta("Time") / 1000),
				songId = t.getId())

			pl.append(s)

		return pl 

    def version(self):
		return ScMpdServerDaemon.player.playlistVersion 

    def move(self, fromPos, toPos):
		pass


