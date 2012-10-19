from command_base import *

################################
# Default Commands Definitions #
################################
class Random(Command):
    formatArg=[('state',int)]

class PlayId(Command):
    formatArg=[('songId',OptInt)]

class Play(Command):
    formatArg=[('songPos',OptInt)]

class Pause(Command):
    """ Override :func:`handle_pause` and :func:`handle_unpause` method """
    formatArg=[('state',int)]
    def handle_args(self,state): 
        if state==1:
            self.handle_pause()
        else :
            self.handle_unpause()
    def handle_pause(self):
        """When pause is set"""
        pass
    def handle_unpause(self):
        """When pause is unset"""
        pass

class Seek(Command):
    """Skip to a specified point toSec in a song songPosition on the playlist"""
    formatArg=[('songPosition',int),('toSec',int)]

class Outputs(CommandItems):
    def items(self):
        return [('outputid',0),        # <int output> the output number                              
                ('outputname','gstreamer'), # <str name> the name as defined in the MPD configuration file
                ('outputenabled',1)    # <int enabled> 1 if enabled, 0 if disabled                   
                ]

class CurrentSong(CommandSongs):pass

class Stats(CommandItems):
    def items(self):
        return [("artists",-1),  #number of artists
                ("albums",-1),  #number of albums
                ("songs",-1),  #number of songs
                ("uptime",-1),  #daemon uptime (time since last startup) in seconds
                ("playtime",-1),  #time length of music played
                ("db_playtime",-1),  #sum of all song times in db
                ("db_update",-1)]  #last db update in UNIX time 

class Status(CommandItems):
    """ Manage mpd status """
    def helper_status_common(self,volume=0,repeat=0,random=0,xfade=0):
        "Status is set to 'stop' by default. Use :method:play or :method:pause to set status"
        return [('volume',volume), #(0-100)  
                ('repeat',repeat), #(0 or 1) 
                ('random',random), #(0 or 1) 
                ('playlist',self.playlist.version()), #(31-bit unsigned integer, the playlist version number)
                ('playlistlength',self.playlist.length()),   #(integer, the length of the playlist)                 
                ('xfade',xfade)]                     #(crossfade in seconds)                                
#               ('bitrate') + #<int bitrate> (instantaneous bitrate in kbps)
#               ('audio') + #<int sampleRate>:<int bits>:<int channels>
#               ('updating_db') + #<int job id>
#               ('error') + #if there is an error, returns message here
#               ('nextsong: 0\n') + #(next song, playlist song number >=mpd 0.15)
#               ('nextsongid: 0\n') + #(next song, playlist songid>=mpd 0.15)

    def helper_status_stop(self,volume=0,repeat=0,random=0,xfade=0):
        "Status is set to 'stop' by default. Use :method:play or :method:pause to set status"
        return (self.helper_status_common(volume,repeat,random,xfade) +
                [('state',"stop")]) #("play", "stop", or "pause")
    
    def helper_status_play(self,volume=0,repeat=0,random=0,xfade=0,elapsedTime=10,durationTime=100,playlistSongNumber=-1,playlistSongId=-1):
        return (self.helper_status_common(volume,repeat,random,xfade) +
                [('state',"play"),
                 ('song',playlistSongNumber), #(current song stopped on or playing, playlist song number)
                 ('songid',playlistSongId),   #(current song stopped on or playing, playlist songid)
                 ('time',"%d:%d"%(elapsedTime,durationTime))]) #<int elapsed>:<time total> (of current playing/paused song)

    def helper_status_pause(self,volume=0,repeat=0,random=0,xfade=0,elapsedTime=10,durationTime=100,playlistSongNumber=-1,playlistSongId=-1):
        return (self.helper_status_common(volume,repeat,random,xfade) +
                [('state',"pause"),
                 ('song',playlistSongNumber),
                 ('songid',playlistSongId),
                 ('time',"%d:%d"%(elapsedTime,durationTime))])

    def items(self):
        return self.helper_status_stop()

class NotCommands(CommandItems): pass# Not used by gmpc
    # def items(self):
    #     return [('command','tagtypes'),
    #             ('command','lsinfo')]
class Commands(CommandItems): pass# Not used by gmpc

class LsInfo(CommandItems): # Since 0.12
    formatArg=[('directory',OptStr)]

class MoveId(Command): # Since 0.12
    formatArg=[('idFrom',int),('positionTo',int)]
    def handle_args(self,idFrom,positionTo):
        self.playlist.moveId(idFrom,positionTo)
class Move(Command): # Since 0.12
    """ To move a song at positionFrom to postionTo."""
    formatArg=[('positionFrom',int),('positionTo',int)]
    def handle_args(self,positionFrom,positionTo):
        self.playlist.move(positionFrom,positionTo)

class Delete(Command): # Since 0.12
    """ To delete the song at songPosition from current playlist. """
    formatArg=[('songPosition',int)]
    def handle_args(self,songPosition):
        self.playlist.delete(songPosition)
class DeleteId(Command): # Since 0.12
    formatArg=[('songId',int)]
    def handle_args(self,songId):
        self.playlist.deleteId(songId)

        
    
class ListPlaylistInfo(CommandSongs): # Since 0.12
    """ List playlist 'playlistname' content """
    formatArg=[('playlistName',str)]

class Add(Command): # todo return type
    formatArg=[('song',str)]

class AddId(CommandItems): # todo return type

    formatArg=[('song',str)]

    def items(self):
		return [("id", 0)]

class TagTypes(Command):pass # Since 0.12

class PlaylistInfo(CommandSongs):
    """ Without song position, list all song in current playlist. With
    song position argument, get song details. """
    formatArg=[('songPosition',OptInt)]
    def songs(self):
        try :
            pos=self.args['songPosition']
        except KeyError:
            return self.playlist.generateMpdPlaylist()
        return [self.playlist.generateMpdPlaylist()[pos]]



class PlaylistId(CommandSongs):
    """ Without song position, list all song in current playlist. With
    song position argument, get song details. """
    formatArg=[('songId',OptInt)]
    def handle_args(self,songId):pass
    def songs(self):
        try :
            idx=self.playlist.songIdToPosition(self.args['songId'])
            return [self.playlist.generateMpdPlaylist()[idx]]
        except KeyError:pass
        return self.playlist.generateMpdPlaylist()


class SetVol(Command):
    formatArg=[('volume',int)]
    
class PlChanges(CommandSongs):
    formatArg=[('playlistVersion',int)]
    def songs(self):
        return self.playlist.generateMpdPlaylistDiff(self.args['playlistVersion'])
    
class PlChangesPosId(CommandItems):
    formatArg=[('playlistVersion',int)]
    def items(self):
        p=self.playlist.generateMpdPlaylistDiff(self.args['playlistVersion'])
        acc=[]
        for s in p:
            acc.append(('cpos',s.playlistPosition))
            acc.append(('Id',s.songId))
        return acc

class Password(Command):
    """ Set username of connexion."""
    formatArg=[('pwd',str)]
    def handle_args(self,pwd):
        if not self.frontend.set(pwd):
            raise MpdCommandError("User '%s' doesn't exist"%pwd,"password")

# Playlist Management
class ListPlaylists(CommandItems):
    def handle_playlists(self):
        """ Should return list of plyalist name"""
        pass
    def items(self):
        return [("playlist",p) for p in self.handle_playlists()]

class Load(Command):
    """ Load a playlist in current playlist. Songs are added to
    current playlist."""
    formatArg=[('playlistName',str)]

class Save(Command):
    formatArg=[('playlistName',str)]

class Rm(Command):
    formatArg=[('playlistName',str)]

class PlaylistClear(Command):
    formatArg=[('playlistName',str)]

class PlaylistMove(Command):
    formatArg=[('playlistName',str), ('songId', int), ('songPos', int) ]

class PlaylistDelete(Command):
    formatArg=[('playlistName',str), ('songPos', int) ]

class Rename(Command):
    formatArg=[('playlistName',str), ('playlistNameNew',str)]

class PlaylistAdd(Command):
    formatArg=[('playlistName', str), ('song',str)]

class Decoders(CommandItems):
	def items(self):
		return [('plugin','gstreamer'),                                      
				('suffix','mp3'), 
				]
