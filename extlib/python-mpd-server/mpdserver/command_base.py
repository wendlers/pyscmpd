""" 
This module permits to define mpd commands. Each command inherits from
:class:`Command` which is a command base class. There are
also some specialized subclasses of :class:`Command`:

- :class:`CommandItems` can be used when respond is a list of items
- :class:`CommandSongs` can be used when respond is a list of songs
- :class:`CommandPlaylist` can be used when respond is a list of songs

MPD songs are represented by classes:

- :class:`MpdPlaylistSong` which contains a song position and a song id.
- :class:`MpdLibrarySong` 

Moreover, you can map your playlist to the mpd playlist by overriding
:class:`MpdPlaylist`. Then when you override this class, a lot of
commands are defined (for example :class:`Move`, :class:`MoveId`,
:class:`Delete`, etc.).

MPD protocol supports playlist diff (for example
command :class:`command_skel.PlChanges`). This feature is internally
management with :class:`PlaylistHistory`.


Note: 'command' and 'notcommand' commands seems to not be used by
gmpc. Then, we have to implement a lot of commands with dummy
respond. However, gmpc use 'command' command to allow user to play,
pause ...
"""
import logging
import mpdserver
logger=mpdserver.logging
#logger.basicConfig(level=logging.DEBUG)


class CommandArgumentException(Exception):pass
        

class Command():
    """ Command class is the base command class. You can define
    argument format by setting :attr:`formatArg`. Command argument
    can be accessed with :attr:`args` dictionnary.

    Each command has a playlist attribute which is given by
    MpdRequestHandler. This playlist must implement MpdPlaylist class
    and by default, this one is used.

    :class:`Command` contains command
    arguments definition via :attr:`Command.formatArg`. You can handle
    them with :func:`Command.handle_args`. An argument is :
    
    - an int
    - a string
    - an optionnal int (:class:`OptInt`)
    - an optionnal string (:class:`OptStr`)

    """

    formatArg=[]
    """ To specify command arguments format. For example, ::
    
       formatArg=[("song",OptStr)] 

    means command accept a optionnal
    string argument bound to `song` attribute name."""
    args={}
    """ A dictionnary of received arguments from mpd client. They must
    be defined in :attr:`formatArg`."""

    def __init__(self,args,playlist,frontend,player):
            self.args=self.__parseArg(args)
            self.playlist=playlist
            self.frontend=frontend
            self.player=player

    def run(self):
        """To treat a command. This class handle_args method and toMpdMsg method."""
        try:
            self.handle_args(**(self.args))
            return self.toMpdMsg()
        except NotImplementedError as e:
            raise mpdserver.CommandNotImplemented(self.__class__,str(e))
        
    @classmethod
    def GetCommandName(cls):
        """ MPD command name. Command name is the lower class
        name. This string is used to parse a client request. You can
        override this classmethod to define particular commandname."""
        return cls.__name__.lower()

    def __parseArg(self,args):
        if len(args) > len(self.formatArg):
            raise CommandArgumentException("Too much arguments: %s command arguments should be %s instead of %s" % (self.__class__,self.formatArg,args))
        try:
            d=dict()
            for i in range(0,len(self.formatArg)):
                if Opt in self.formatArg[i][1].__bases__ :
                    try:
                        d.update({self.formatArg[i][0] : self.formatArg[i][1](args[i])})
                    except IndexError : pass
                else:                        
                    d.update({self.formatArg[i][0] : self.formatArg[i][1](args[i])})
        except IndexError : 
            raise CommandArgumentException("Not enough arguments: %s command arguments should be %s instead of %s" %(self.__class__,self.formatArg,args))
        except ValueError as e:
            raise CommandArgumentException("Wrong argument type: %s command arguments should be %s instead of %s (%s)" %(self.__class__,self.formatArg,args,e))
        return d
    
    def handle_args(self,**kwargs):
        """ Override this method to treat commands arguments."""
        logger.debug("Parsing arguments %s in %s" % (str(kwargs),str(self.__class__)))
    def toMpdMsg(self):
        """ Override this method to send a specific respond to mpd client."""
        logger.debug("Not implemented respond for command %s"%self.__class__)
        return ""

class CommandDummy(Command):
    def toMpdMsg(self):
        logger.info("Dummy respond sent for command %s"%self.__class__)
        return "ACK [error@command_listNum] {%s} Dummy respond for command '%s'\n" % (self.__class__,self.__class__)

class CommandItems(Command):
    """ This is a subclass of :class:`Command` class. CommandItems is
    used to send items respond such as :class:`command.Status` command."""
    def items(self):
        """ Overwrite this method to send items to mpd client. This method
        must return a list a tuples ("key",value)."""
        return []
    def toMpdMsg(self):
        items=self.items()
        acc=""
        for (i,v) in items:
            acc+="%s: %s\n"%(i,str(v))
        return acc

class CommandSongs(Command):
    """ This is a subclass of :class:`Command` class. Respond songs
    informations for mpd clients."""
    def songs(self): 
        """ Override it to adapt this command. This must return a list of
        :class:`MpdPlaylistSong` """
        return [] #self.helper_mkSong("/undefined/")
    def toMpdMsg(self):
        return ''.join([MpdPlaylistSong.toMpdMsg(s) for s in self.songs()])
        
class CommandPlaylist(CommandSongs):
    """ This class of commands is used on mpd internal playlist."""
    def songs(self):
        """ Overide it to specify a real playlist. 
        Should return a list of dict song informations"""
        return [] # self.playlist.generateMpdPlaylist()

class MpdPlaylistSong(object):
    """ To create a mpd song which is in a playtlist.

    MPD use a song id which is unique for all song in
    playlist and stable over time. This field is automatically
    generated.
    """
    def __init__(self,file,songId,playlistPosition=None,title=" ",time=0,album=" ",artist=" ",track=0):
        self.file=file
        self.title=title
        self.time=time
        self.album=album
        self.artist=artist
        self.track=track
        self.playlistPosition=playlistPosition
        self.songId=songId #self.generatePlaylistSongId(self)

    def generatePlaylistSongId(self,song):
        return id(song)

    def toMpdMsg(self):
        if self.playlistPosition == None :
            logger.warning("MpdPlaylistSong.playlistposition attribute is not set.")
        return ('file: '+self.file+"\n"+
                'Time: '+str(self.time)+"\n"+
                'Album: '+self.album+"\n"+
                'Artist: '+self.artist+"\n"+
                'Title: '+self.title+"\n"+
                'Track: '+str(self.track)+"\n"+
                'Pos: '+str(self.playlistPosition)+"\n"+
                'Id: '+ str(self.songId)+"\n")

class MpdLibrarySong(object):
    """ To create a mpd library song. This is actually not used."""
    def __init__(self,filename):
        self.file=filename
        self.lastModDate="2011-12-17T22:47:58Z"
        self.time="0"
        self.artist= ""
        self.title=filename
        self.album=""
        self.track=""
        self.genre=""

    def toMpdMsg(self):
        return ("file: "+self.filename+"\n"+
                "Last-Modified: "+self.lastModDate+"\n"+
                "Time: "+self.time+"\n"+
                "Artist: "+self.artist+"\n"+
                "Title: "+self.title+"\n"+
                "Album: "+self.album+"\n"+
                "Track: "+self.track+"\n"+
                "Genre :"+self.genre+"\n")


import types
class Opt(object):pass
class OptInt(Opt,types.IntType):
    """ Represent optionnal integer command argument"""
    pass
class OptStr(Opt,types.StringType):
    """ Represent optionnal string command argument"""
    pass


class PlaylistHistory(object):
    """ Contains all playlist version to generate playlist diff (see
    plchanges* commands). This class is a singleton and it is used by
    MpdPlaylist.    
    """ 
    _instance = None
    playlistHistory=[]
        
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(PlaylistHistory, cls).__new__(
                cls, *args, **kwargs)
        return cls._instance
        
    def addPlaylist(self,version,playlist):
        """ Add playlist version if not exist in history """
        for (v,p) in self.playlistHistory:
            if v == version:
                return None
        self.playlistHistory.append((version,playlist))

    def getPlaylist(self,version):
        """ Get playlist from version"""
        for (i,p) in self.playlistHistory:
            if i==version:
                return p
        return None

    def diff(self,version):
        """ Return new songs in current playlist since version """
        plOld=self.getPlaylist(version)
        plCur=self.playlistHistory[len(self.playlistHistory)-1][1]
        if plOld == None:
            return plCur
        diff=[]
        try :
            for i in range(0,len(plOld)):
                if plOld[i] != plCur[i]:
                    diff.append(plCur[i])
            for i in range(len(plOld),len(plCur)):
                diff.append(plCur[i])
        except IndexError: pass
        return diff
            
    def show(self):
        print "show playlistHistory"
        print "number of version: " + str(len(self.playlistHistory))
        for i in self.playlistHistory:
            print i
            print "------"
        print "show playlistHistory end"
        

class MpdPlaylist(object):
    """ MpdPlaylist is a list of song.  
    Use it to create a mapping between your player and the fictive mpd
    server.

    Some methods must be implemented, otherwise, NotImplementedError
    is raised.

    To bind a playlist to this class, use overide
    `handlePlaylist` method.
    """
    def __init__(self):
        self.playlistHistory=PlaylistHistory()

    def handlePlaylist(self):
        """ Implement this method to bind your playlist with mpd
        playlist. This method should return a list of :class:`MpdPlaylistSong`."""
        raise NotImplementedError("you should implement MpdPlaylist.handlePlaylist method (or use MpdPlaylistDummy) ")

    def generateMpdPlaylist(self):
        """ This is an internal method to automatically add playlistPosition to songs in playlist. """
        p=self.handlePlaylist()
        for i in range(len(p)):
            p[i].playlistPosition=i
        self.playlistHistory.addPlaylist(self.version(),p)
        return p

    def generateMpdPlaylistDiff(self,oldVersion):
        self.generateMpdPlaylist()
        return self.playlistHistory.diff(oldVersion)

    def songIdToPosition(self,id):
        """ This method MUST be implemented. It permits to generate the position from a mpd song id."""
        raise NotImplementedError("you should implement MpdPlaylist.songIdToPosition method")
    def version(self):
        return 0
    def length(self):
        return len(self.generateMpdPlaylist())
    def move(self,fromPostion,toPosition):
        """ Implement it to support move* commands """
        raise NotImplementedError("you should implement MpdPlaylist.move method")
    def moveId(self,fromId,toPosition):
        self.move(self.songIdToPosition(fromId),toPosition)
    def delete(self,position):
        """ Implement it to support delete* commands """
        raise NotImplementedError("you should implement MpdPlaylist.delete method")
    def deleteId(self,songId):
        self.delete(self.songIdToPosition(songId))


class MpdPlaylistDummy(MpdPlaylist):
    def handlePlaylist(self):
        logger.warning("Dummy implementation of handlePlaylist method")
        return []
        
