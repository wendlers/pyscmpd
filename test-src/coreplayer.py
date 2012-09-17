import logging
import mpdserver
import soundcloud
import pickle

import pyscmpd.resource.scprovider as provider 
import pyscmpd.player.core as coreplayer 

mpd	   = None
player = None
scroot = None

class Play(mpdserver.Play):

	def handle_args(self, songPos=0):

		player.play(songPos)

class Stop(mpdserver.Command):

	def handle_args(self):

		player.stop()

class Clear(mpdserver.Command):

	def handle_args(self):

		logging.info("Clear playlist")

		player.stop()
		player.delAllChildren()

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
			r = scroot.getAllChildren()
		else:
			r = scroot.getChildByName(self.directory)
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
					i.append(("Time", e.getMeta("Time")))

		return i 

class Add(mpdserver.Add):

	def handle_args(self, song):

		logging.info("Adding song [%s] to playlist" % song) 

		(user, sep, track) = song.partition("/")

		if track == "":
			logging.error("Could not extract track from [%s]", song)
			return	

		u = scroot.getChildByName(user)

		if user == None:
			logging.error("Could not find directory for [%s]", user)
			return

		t = u.getChildByName(track)

		if t == None:
			logging.error("Track [%s] not found in directory [%s]" % (track, user))
			return

		player.addChild(t)
		
		logging.info("Successfully added song: %s" % t.__str__())

class AddId(mpdserver.Add):

	def handle_args(self, song):

		logging.info("Adding song [%s] to playlist" % song) 

		(user, sep, track) = song.partition("/")

		if track == "":
			logging.error("Could not extract track from [%s]", song)
			return	

		u = scroot.getChildByName(user)

		if user == None:
			logging.error("Could not find directory for [%s]", user)
			return

		t = u.getChildByName(track)

		if t == None:
			logging.error("Track [%s] not found in directory [%s]" % (track, user))
			return

		player.addChild(t)
		
		logging.info("Successfully added song: %s" % t.__str__())


class MpdPlaylist(mpdserver.MpdPlaylist):

    def songIdToPosition(self, songId):

		logging.info("Request to convert Id [%d] to position" % songId)
		return 0

    def handlePlaylist(self):

		pl = []

		logging.info("Playlist requested")	

		for t in player.getAllChildren():

			s = mpdserver.MpdPlaylistSong(
				artist = t.getMeta("Artist").encode('ASCII', 'ignore'), 
				title = t.getMeta("Title").encode('ASCII', 'ignore'), 
				file = t.getMeta("file").encode('ASCII', 'ignore'),
				songId = t.getId())

			pl.append(s)

		logging.info("Returning playlist: %s" % pl)
		return pl 

    def move(self, fromPos, toPos):
		pass

if __name__ == "__main__":
	try:

		logging.basicConfig(level=logging.DEBUG)

		player = coreplayer.GstPlayer() 

		# TODO: do not hardcode root :-)
		provider.ResourceProvider.ROOT_USERS =  [ 
			"/users/griz", 
			"/users/freudeamtanzen", 
			"/users/barelylegit", 
			"/users/maddecent" 				# TODO: this one has unicode / encoding errors
			]

		'''
		# connect to soundcloud resources
		scp 	= provider.ResourceProvider()
	
		scroot  = scp.getRoot()

		f = open('scroot.dump', 'wb')
		pickle.dump(scroot, f)		
		f.close()
		'''

		f = open('scroot.dump', 'rb')
		scroot = pickle.load(f)		
		f.close()
		'''
		'''

		mpd=mpdserver.MpdServerDaemon(9999)
		mpd.requestHandler.RegisterCommand(mpdserver.Outputs)
		mpd.requestHandler.RegisterCommand(Play)
		mpd.requestHandler.RegisterCommand(Stop)
		mpd.requestHandler.RegisterCommand(LsInfo)
		mpd.requestHandler.RegisterCommand(Add)
		mpd.requestHandler.RegisterCommand(AddId)
		mpd.requestHandler.RegisterCommand(Clear)
		# mpd.requestHandler.Playlist=mpdserver.MpdPlaylistDummy
		mpd.requestHandler.Playlist=MpdPlaylist

		while mpd.wait(1) : pass

	except KeyboardInterrupt:

		logging.info("Stopping SoundCloud MPD server")

	except Exception as e:

		logging.error("Exception occurred: %s" % `e`)

	finally:

		if not mpd == None:
			mpd.quit()
