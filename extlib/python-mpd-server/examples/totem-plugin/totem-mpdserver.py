from gi.repository import Peas
from gi.repository import Gtk
from gi.repository import Totem
from gi.repository import Gio
from gi.repository import GObject

import mpdserver

class Pause(mpdserver.Pause):
	def handle_pause(self):
		print "Pause catched"
		self.player.action_play_pause()

class MpdServerPlugin(GObject.Object, Peas.Activatable):
	__gtype_name__ = 'PythonConsolePlugin2'
	object = GObject.property(type = GObject.Object)



	def __init__(self):
                GObject.Object.__init__ (self)
		self.totem = None
		self.window = None

	
	def do_activate(self):
		self.totem = self.object
		self.mpd=mpdserver.MpdServerDaemon(9999)
		self.mpd.requestHandler.SetPlayer(self.totem)
		self.mpd.requestHandler.RegisterCommand(Pause)

	def do_deactivate(self):
		self.mpd.quit()
