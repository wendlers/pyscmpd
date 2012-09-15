import logging
import mpdserver
import soundcloud

import pyscmpd.resource.scprovider as provider 
import pyscmpd.player.core as coreplayer 

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

		if self.directory == None:
			r = scroot.getAllChildren()
			LsInfo.currdir = scroot 
		else:
			r = scroot.getChildByName(self.directory)

			if r == None:
				return i	

			LsInfo.currdir = r
			logging.info("Setting current dir to: %s" % LsInfo.currdir.__str__())

			r = r.getAllChildren()

		for e in r:

			logging.debug("LsInfo sending item: %s" % e.__str__())

			if e.getType() == 1:
				t = "directory"
			else:
				t = "file"
 
			i.append((t, e.getName()))

		return i 

class Add(mpdserver.Add):

	def handle_args(self, song):

		logging.info("Current dir is: %s" % LsInfo.currdir.__str__())
		logging.info("Adding song [%s] to playlist" % song) 

		if LsInfo.currdir == None:
			logging.error("Change to directory first")
			return
		
		t = LsInfo.currdir.getChildByName(song)

		if t == None:
			logging.error("Track [%s] not found in directory [%s]" % (song, currdir.getName()))
			return

		player.addChild(t)

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

		# connect to soundcloud resources
		scp 	= provider.ResourceProvider()
	

		scroot  = scp.getRoot()
		LsInfo.currdir = scroot

		mpd=mpdserver.MpdServerDaemon(9999)
		mpd.requestHandler.RegisterCommand(mpdserver.Outputs)
		mpd.requestHandler.RegisterCommand(Play)
		mpd.requestHandler.RegisterCommand(Stop)
		mpd.requestHandler.RegisterCommand(LsInfo)
		mpd.requestHandler.RegisterCommand(Add)
		mpd.requestHandler.RegisterCommand(Clear)
		mpd.requestHandler.Playlist=mpdserver.MpdPlaylistDummy
		# mpd.requestHandler.Playlist=MpdPlaylist

		while mpd.wait(1) : pass

	except KeyboardInterrupt:

		logging.info("Stopping SoundCloud MPD server")

	except Exception as e:

		logging.error("Exception occurred: %s" % `e`)

	finally:

		mpd.quit()
