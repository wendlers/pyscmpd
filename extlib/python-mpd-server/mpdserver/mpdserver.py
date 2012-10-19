# Pimp is a highly interactive music player.
# Copyright (C) 2011 kedals0@gmail.com

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""To launch a mpd server, use :class:`MpdServer` or
:class:`MpdServerDaemon` classes.

:class:`MpdRequestHandler` manages a client connection. It parses
client requests and executes corresponding commands. Supported MPD
commands are specified with method
:func:`MpdRequestHandler.RegisterCommand`. Skeletons commands are
provided by module :mod:`command_skel`. They can easily be override.

A client connection can begin by a password command. In this case, a
:class:`Frontend` is created by client password command. This object
is provided to commands treated during this session.
"""
import SocketServer
SocketServer.TCPServer.allow_reuse_address = True
import time
import re 
import threading
import sys
#from pimp.core.playlist import * 
#from pimp.core.player import * 
#import pimp.core.db
import logging

from command_base import *
from command_skel import *

logger=logging
#logger.basicConfig(level=logging.INFO)
#logger.basicConfig(level=logging.DEBUG)


##################################
### Mpd supported return types ###
##################################
class MpdErrorMsgFormat(Exception):pass
class MpdCommandError(Exception):
    def __init__(self,msg="Unknown error",command="command is not specified"):
        self.command=command
        self.msg=msg
    def toMpdMsg(self):
        return "ACK [error@command_listNum] {%s} %s\n" % (self.command,self.msg)
class CommandNotSupported(MpdCommandError):
    def __init__(self,commandName):
        self.commandName=commandName
    def toMpdMsg(self):
        return "ACK [error@command_listNum] {%s} Command '%s' not supported\n" % (self.commandName,self.commandName)
class CommandNotMPDCommand(MpdCommandError):
    def __init__(self,commandName):
        self.commandName=commandName
    def toMpdMsg(self):
        return "ACK [error@command_listNum] {%s} Command '%s' is not a MPD command\n" % (self.commandName,self.commandName)
class CommandNotImplemented(MpdCommandError):
    def __init__(self,commandName,message=""):
        self.commandName=commandName
        self.message=message
    def toMpdMsg(self):
        return "ACK [error@command_listNum] {%s} Command '%s' is not implemented (%s)\n" % (self.commandName,self.commandName,self.message)
class UserNotAllowed(MpdCommandError):
    def __init__(self,commandName,userName):
        self.commandName=commandName
        self.userName=userName
    def toMpdMsg(self):
        return "ACK [error@command_listNum] {%s} User '%s' is not allowed to execute command %s\n" % (self.commandName,self.userName,self.commandName)
class PasswordError(MpdCommandError):
    def __init__(self,pwd,format):
        self.pwd=pwd
        self.format=format
    def toMpdMsg(self):
        return "ACK [error@command_listNum] {password} Password '%s' is not allowed a valid password. You should use a password such as '%s'\n" % (self.pwd,self.format)

class Frontend(object):
    """ To define a frontend. To specify a frontend and user , use MPD
    password command with format 'frontend:user'. If password command
    is not used, frontend is set to 'unknown' and user to 'default'."""
    _DefaultUsername='default'
    username=_DefaultUsername
    _DefaultFrontend='unknown'
    frontend=_DefaultFrontend

    def set(self,frontendPassword):
        """ Password from frontend contains the name of frontend (mpc,
        sonata, ...) and a user name. The format is 'frontend:user'"""
        (self.frontend,t,self.username)=frontendPassword.partition(':')
        if self.frontend == '' or self.username == '':
            logger.warning("Wrong password request '%s'" % frontendPassword)

            raise PasswordError(frontendPassword,"frontend:user")
        return True
    def get(self):
        """ Get frontend information. Return a dict."""
        return {'username':self.username,'frontend':self.frontend}
    def getUsername(self):
        return self.username
    @classmethod
    def GetDefaultUsername(cls):
        return cls._DefaultUsername
        

class MpdRequestHandler(SocketServer.StreamRequestHandler):
    """ Manage the connection from a mpd client. Each client
    connection instances this object."""
    Playlist=MpdPlaylist
    __player=None
    __SupportedCommands={'currentsong'      :{'class':CurrentSong,'users':['default'],'group':'read','mpdVersion':"0.12",'neededBy':["sonata"]},
                         'outputs'          :{'class':Outputs,'users':['default'],'group':'read','mpdVersion':"0.12",'neededBy':["gmpc"]},
                         'status'           :{'class':Status,'users':['default'],'group':'read','mpdVersion':"0.12",'neededBy':["sonata"]},
                         'stats'            :{'class':Stats,'users':['default'],'group':'read','mpdVersion':"0.12",'neededBy':None},
                         'notcommands'      :{'class':NotCommands,'users':['default'],'group':'read','mpdVersion':"0.12",'neededBy':["gmpc"]},
                         'commands'         :{'class':None,'users':[],'group':'read','mpdVersion':"0.12",'neededBy':None},
                         'lsinfo'           :{'class':None,'users':[],'group':'read','mpdVersion':"0.12",'neededBy':None},
                         'tagtypes'         :{'class':None,'users':[],'group':'read','mpdVersion':"0.12",'neededBy':None},
                         'playlistinfo'     :{'class':PlaylistInfo,'users':['default'],'group':'read','mpdVersion':"0.12",'neededBy':None},
                         'playlistid'       :{'class':PlaylistId,'users':['default'],'group':'read','mpdVersion':"0.12",'neededBy':None},
                         'listplaylistinfo' :{'class':None,'users':[],'group':'read','mpdVersion':"0.12",'neededBy':None},
                         'plchanges'        :{'class':PlChanges,'users':['default'],'group':'read','mpdVersion':"0.12",'neededBy':["sonata"]},
                         'plchangesposid'   :{'class':PlChangesPosId,'users':['default'],'group':'read','mpdVersion':"0.12",'neededBy':None},
                         'moveid'           :{'class':None,'users':[],'group':'read','mpdVersion':"0.12",'neededBy':None},
                         'move'             :{'class':None,'users':[],'group':'read','mpdVersion':"0.12",'neededBy':None},
                         'delete'           :{'class':Delete,'users':[],'group':'read','mpdVersion':"0.12",'neededBy':None},
                         'deleteid'         :{'class':DeleteId,'users':['default'],'group':'read','mpdVersion':"0.12",'neededBy':None},
                         'add'              :{'class':None,'users':[],'group':'read','mpdVersion':"0.12",'neededBy':None},
                         'addid'            :{'class':None,'users':[],'group':'read','mpdVersion':"0.12",'neededBy':None},
                         'playid'           :{'class':None,'users':[],'group':'read','mpdVersion':"0.12",'neededBy':None},
                         'play'             :{'class':None,'users':[],'group':'read','mpdVersion':"0.12",'neededBy':None},
                         'password'         :{'class':Password,'users':['default'],'group':'read','mpdVersion':"0.12",'neededBy':["all"]},
                         'clear'            :{'class':None,'users':[],'group':'read','mpdVersion':"0.12",'neededBy':None},
                         'stop'             :{'class':None,'users':[],'group':'read','mpdVersion':"0.12",'neededBy':None},
                         'seek'             :{'class':None,'users':[],'group':'read','mpdVersion':"0.12",'neededBy':None},
                         'pause'            :{'class':None,'users':[],'group':'read','mpdVersion':"0.12",'neededBy':None},
                         'next'             :{'class':None,'users':[],'group':'read','mpdVersion':"0.12",'neededBy':None},
                         'previous'         :{'class':None,'users':[],'group':'read','mpdVersion':"0.12",'neededBy':None},
                         'random'           :{'class':None,'users':[],'group':'read','mpdVersion':"0.12",'neededBy':None},
                         'listplaylists'    :{'class':None,'users':[],'group':'read','mpdVersion':"0.12",'neededBy':None},
                         'playlistclear'    :{'class':None,'users':[],'group':'read','mpdVersion':"0.12",'neededBy':None},
                         'playlistmove'    :{'class':None,'users':[],'group':'read','mpdVersion':"0.12",'neededBy':None},
                         'playlistdelete'   :{'class':None,'users':[],'group':'read','mpdVersion':"0.12",'neededBy':None},
                         'playlistadd'   	:{'class':None,'users':[],'group':'read','mpdVersion':"0.12",'neededBy':None},
                         'load'             :{'class':None,'users':[],'group':'write','mpdVersion':"0.12",'neededBy':None},
                         'save'             :{'class':None,'users':[],'group':'write','mpdVersion':"0.12",'neededBy':None},
                         'search'           :{'class':None,'users':[],'group':'read','mpdVersion':"0.12",'neededBy':None},
                         'rm'               :{'class':None,'users':[],'group':'write','mpdVersion':"0.12",'neededBy':None},
                         'rename'           :{'class':None,'users':[],'group':'write','mpdVersion':"0.12",'neededBy':None},
                         'setvol'           :{'class':None,'users':[],'group':'control','mpdVersion':"0.12",'neededBy':None},
                         'decoders'         :{'class':Decoders,'users':['default'],'group':'reflection','mpdVersion':"0.12",'neededBy':None}
                         }
    
    def __init__(self, request, client_address, server):
        self.playlist=self.Playlist()
        self.frontend=Frontend()
        logger.debug( "Client connected (%s)" % threading.currentThread().getName())
        SocketServer.StreamRequestHandler.__init__(self,request,client_address,server)


    """ Handle connection with mpd client. It gets client command,
    execute it and send a respond."""
    def handle(self):
        welcome=u"OK MPD 0.13.0\n"
        self.request.send(welcome.encode("utf-8"))
        while True:
            msg=""
            try:
                cmdlist=None
                cmds=[]
                while True:
                    self.data = self.rfile.readline().strip()
                    if len(self.data)==0 : raise IOError #To detect last EOF
                    if self.data == "command_list_ok_begin":
                        cmdlist="list_ok"
                    elif self.data == "command_list_begin":
                        cmdlist="list"
                    elif self.data == "command_list_end":
                        break
                    else:
                        cmds.append(self.data)
                        if not cmdlist:break
                logger.debug("Commands received from %s" % self.client_address[0])
                try:
                    for c in cmds:
                        logger.debug("Command '" + c + "'...")
                        msg=msg+self.__cmdExec(c)
                        if cmdlist=="list_ok" :  msg=msg+"list_OK\n"
                except MpdCommandError as e:
                    logger.info("Command Error: %s"%e.toMpdMsg())
                    msg=e.toMpdMsg()
                except : raise
                else:
                    msg=msg+"OK\n"
                logger.debug("Message sent:\n\t\t"+msg.replace("\n","\n\t\t"))
                # umsg=unicode(msg,"utf-8",errors='replace')
                self.request.send(msg.encode("utf-8"))
            except IOError,e:
                logger.debug("Client disconnected (%s)"% threading.currentThread().getName())
                break

    def __cmdExec(self,c):
        """ Execute mpd client command. Take a string, parse it and
        execute the corresponding server.Command function."""
        try:
            pcmd=[m.group() for m in re.compile('(\w+)|("([^"])+")').finditer(c)] # WARNING An argument cannot contains a '"'
            cmd=pcmd[0]
            args=[a[1:len(a)-1] for a in pcmd[1:]]
            logger.debug("Command executed : %s %s for frontend '%s'" % (cmd,args,self.frontend.get()))
            commandCls=self.__getCommandClass(cmd,self.frontend)
            msg=commandCls(args,playlist=self.playlist,frontend=self.frontend,player=self.__class__.__player).run()
        except MpdCommandError : raise
        except CommandNotSupported : raise
        except :
            logger.critical("Unexpected error on command %s (%s): %s" % (c,self.frontend.get(),sys.exc_info()[0]))
            raise
        logger.debug("Respond:\n\t\t"+msg.replace("\n","\n\t\t"))
        return msg

    # Manage user rights
    @classmethod
    def RegisterCommand(cls,cls_cmd,users=['default']):
        """ Register a command. Make this command supported by a mpd
        server which use this request handler class. cls_cmd is a
        class which inherits from :class:`command_base.Command`."""
        cls.__SupportedCommands[cls_cmd.GetCommandName()]['class']=cls_cmd
        for a in users : cls.__SupportedCommands[cls_cmd.GetCommandName()]['users'].append(a)

    @classmethod
    def UnregisterCommand(cls,commandName):
        """ Unregister a command"""
        cls.__SupportedCommands[commandName]=None

    @classmethod
    def UserPermissionsCommand(cls,user,commandName=None,group=None):
        """ Add permissions for user 'user'. If commandName is not specified, group should be specified. """
        if commandName != None:
             cls.__SupportedCommands[commandNames]['users'].append(user)
        elif group != None:
            for c in cls.__SupportedCommands.itervalues():
                if c['group']==group:
                    c['users'].append(user)
        else:
            raise TypeError


    @classmethod
    def SupportedCommand(cls):
        """Return a list of command and allowed users."""
        return ["%s\t\t%s"%(k,v['users']) for (k,v) in cls.__SupportedCommands.iteritems() if v['class']!=None ]
    

    def __getCommandClass(self,commandName,frontend):
        """ To get a command class to execute on received command
        string. This method raise supported command errors."""
        if not self.__SupportedCommands.has_key(commandName):
            logger.warning("Command '%s' is not a MPD command!" % commandName)
            raise CommandNotMPDCommand(commandName)
        elif self.__SupportedCommands[commandName]['class'] == None:
            if self.__SupportedCommands[commandName]['neededBy'] != None:
                logger.critical("Command '%s' is needed for client(s) %s" % (commandName," ".join(self.__SupportedCommands[commandName]['neededBy'])))
            logger.warning("Command '%s' is not supported!" % commandName)
            raise CommandNotSupported(commandName)
        elif not (Frontend.GetDefaultUsername() in self.__SupportedCommands[commandName]['users']
                  or frontend.getUsername() in self.__SupportedCommands[commandName]['users']):
            raise UserNotAllowed(commandName,frontend.getUsername())
        else :
            return self.__SupportedCommands[commandName]['class']


    @classmethod
    def SetPlayer(cls,player):
        """To set player object. It is passed to executed commands."""
        cls.__player=player
    @classmethod
    def GetPlayer(cls):
        """To get player object associated to pympdserver."""
        return cls.__player
        
            

class MpdServer(SocketServer.ThreadingMixIn,SocketServer.TCPServer):
    """ Create a MPD server. By default, a request is treated via
    :class:`MpdRequestHandler` class but you can specify an alternative
    request class with RequestHandlerClass argument."""
    requestHandler=MpdRequestHandler
    """ The class which treats client requests. Use this attribute to
    specify supported commands (see :class:`MpdRequestHandler`)."""
    def __init__(self,port=6600,RequestHandlerClass=MpdRequestHandler):
        self.host, self.port = "", port
        self.requestHandler=RequestHandlerClass
        SocketServer.TCPServer.__init__(self,(self.host,self.port),RequestHandlerClass)
        
    def run(self):
        """Run MPD server in a blocking way."""
        logger.info("Mpd Server is listening on port " + str(self.port))
        self.serve_forever()
        
class MpdServerDaemon(MpdServer):
    """ Create a deamonized MPD server. See :class:`MpdServer` for
    more informations. When a MpdServerDaemon object is created, a
    thread is started to treat clients request."""
    def __init__(self,port=6600,mpdRequestHandler=MpdRequestHandler):
        MpdServer.__init__(self,port,mpdRequestHandler)
        self.thread = threading.Thread(target=self.run)
        self.thread.setDaemon(True)
        self.thread.start()
        
    def quit(self):
        """Stop MPD server deamon."""
        logger.info("Stopping Mpd Server")
        self.shutdown()

    def wait(self,timeout=None):
        """ Return True if mpd is alive, False otherwise. This method
        is useful to catch Keyboard interrupt for instance."""
        if timeout==None:
            self.thread.join()
        else:
            self.thread.join(timeout)
        return self.thread.isAlive()
        
