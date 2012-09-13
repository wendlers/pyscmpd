'''
Simple test:

* connect to soundcloud
* read all titles  of one artists (GRiZ)
* instance of gst playbin
* instance of mpd-server

NOTE: code is ugly as hell yet !!!!

The server currently supports:

* ls: list all the tracks (permalink) found for artist (GRiZ)
* add: add a track (permalink) to playlist
* playlist: show current playlist
* play <num>: play song <num> from playlist
* stop: stop playing
* clear: clear playlist

Sample usage:

* start the server:

	python mpdsrv.py

* list titles with mpc client:

	mpc -p 9999 ls

* add songis to playlist with mpc client:

	mpc -p 9999 add 03-rock-n-roll
	mpc -p 9999 add cant-tell-me-nothing-griz
	
* show songs on playlist with mpc client:

	mpc -p 9999 playlist

* play song #3 with mpc client:

	mpc -p 9999 play 3

* stop playing with mpc client:

	mpc -p 9999 stop

* clear playlist with mpc client:

	mpc -p 9999 clear

'''

import mpdserver
import soundcloud
import gst

# soundcloud client instance
client = soundcloud.Client(client_id='aa13bebc2d26491f7f8d1e77ae996a64')
user_tracks = client.get('/users/griz/tracks');

#creates a playbin (plays media form an uri) 
player = gst.element_factory_make("playbin", "player")

class Play(mpdserver.Play):
	def handle_args(self, songPos=0):
		print "*** Set player to play state %s ***" % songPos 

		p = mpd.requestHandler.Playlist.playlist[songPos]

		for res in user_tracks:
			if res.permalink == p.file:
				print "*** found track: %s" % res.title
				stream_url = client.get(res.stream_url, allow_redirects=False)
				print "*** stream url is: %s" % stream_url.location
				player.set_state(gst.STATE_NULL)
				#set the uri
				player.set_property('uri', stream_url.location)
				#start playing
				player.set_state(gst.STATE_PLAYING)

class Stop(mpdserver.Command):
	def handle_args(self):
		print "*** Set player to stop state ***"
		player.set_state(gst.STATE_NULL)

class Clear(mpdserver.Command):
	def handle_args(self):
		print "*** Clear playlist ***"
		player.set_state(gst.STATE_NULL)
		mpd.requestHandler.Playlist.playlist = []

class LsInfo(mpdserver.LsInfo):
	def handle_args(self, directory="/"):
		print "*** List directory %s ***" % directory

	def items(self):
		print "items called"

		i = []

		for res in user_tracks:
			i.append(("file", res.permalink))	

		return i 

class Add(mpdserver.Add):
	def handle_args(self, song):
		print "*** Adding song to playlist %s ***" % song 
		for res in user_tracks:
			if res.permalink == song:
				mpd.requestHandler.Playlist.playlist.append(mpdserver.MpdPlaylistSong(artist='GRiZ', 
				title=res.title.encode('ASCII'), file=res.permalink.encode('ASCII'), songId=res.id))

class MpdPlaylist(mpdserver.MpdPlaylist):
    playlist=[]

    def songIdToPosition(self,i):
        for e in self.playlist:
            if e.id==i : return e.playlistPosition

    def handlePlaylist(self):
        return self.playlist

    def move(self,i,j):
        self.playlist[i],self.playlist[j]=self.playlist[j],self.playlist[i]

mpd=mpdserver.MpdServerDaemon(9999)
mpd.requestHandler.RegisterCommand(mpdserver.Outputs)
mpd.requestHandler.RegisterCommand(Play)
mpd.requestHandler.RegisterCommand(Stop)
mpd.requestHandler.RegisterCommand(LsInfo)
mpd.requestHandler.RegisterCommand(Add)
mpd.requestHandler.RegisterCommand(Clear)
mpd.requestHandler.Playlist=MpdPlaylist

print """Starting a soundcloud mpd server on port 9999
Type Ctrl+C to exit
"""

if __name__ == "__main__":
    try:
        while mpd.wait(1) : pass
    except KeyboardInterrupt:
        print "Stopping SoundCloud MPD server"
        mpd.quit()

