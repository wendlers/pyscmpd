#!/usr/bin/python
""" This is a simple howto example."""
import mpdserver

# Define a playid command based on mpdserver.PlayId squeleton
class PlayId(mpdserver.PlayId):
    # This method is called when playid command is sent by a client
    def handle_args(self,songId):print "*** Play a file with Id '%d' ***" %songId
class Play(mpdserver.Command):
    def handle_args(self):
        print "*** Set player to play state ***"

# Define a MpdPlaylist based on mpdserver.MpdPlaylist
# This class permits to generate adapted mpd respond on playlist command.
class MpdPlaylist(mpdserver.MpdPlaylist):
    playlist=[mpdserver.MpdPlaylistSong(file='file0',songId=0)]
    # How to get song position from a song id in your playlist
    def songIdToPosition(self,i):
        for e in self.playlist:
            if e.id==i : return e.playlistPosition
    # Set your playlist. It must be a list a MpdPlaylistSong
    def handlePlaylist(self):
        return self.playlist
    # Move song in your playlist
    def move(self,i,j):
        self.playlist[i],self.playlist[j]=self.playlist[j],self.playlist[i]

# Create a deamonized mpd server that listen on port 9999
mpd=mpdserver.MpdServerDaemon(9999)
# Register provided outputs command 
mpd.requestHandler.RegisterCommand(mpdserver.Outputs)
# Register your own command implementation
mpd.requestHandler.RegisterCommand(PlayId)
mpd.requestHandler.RegisterCommand(Play)
# Set the user defined playlist class
mpd.requestHandler.Playlist=MpdPlaylist
#mpd.requestHandler.Playlist=mpdserver.MpdPlaylistDummy

print """Starting a mpd server on port 9999
Type Ctrl+C to exit

To try it, type in another console
$ mpc -p 9999 play
Or launch a MPD client with port 9999
"""
if __name__ == "__main__":
    try:
        while mpd.wait(1) : pass
    except KeyboardInterrupt:
        print "Stopping MPD server"
        mpd.quit()

