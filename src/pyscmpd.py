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
import gobject
import pyscmpd.scmpd as scmpd

from ConfigParser import SafeConfigParser

PYSCMPD_VERSION="0.0.1"

gobject.threads_init()

class PyScMpd():

	mpd 		= None
	mainloop 	= None
	favorites	= None 
	port		= 9900

	def __init__(self):

		self.favorites = []

	def __del__(self):

		if not self.mpd == None:
			self.mpd.quit()

		if not self.mainloop == None:
			self.mainloop.quit()

	def readConfig(self, cfgFile):

		parser = SafeConfigParser()

		try:
			parser.read(cfgFile)

			if parser.has_section("server"):

				if parser.has_option("server", "port"):
					self.port = parser.getint("server", "port")	

			
			if parser.has_section("logging"):

				level 	= "info"
				logFile = None

				if parser.has_option("logging", "level"):
					level = parser.get("logging", "level")	

				if parser.has_option("logging", "file"):
					logFile = parser.get("logging", "file")	

				numeric_level = getattr(logging, level.upper(), None)

				if not isinstance(numeric_level, int):
					raise ValueError('Invalid log level: %s' % loglevel)

				if logFile == None:

					logging.basicConfig(
						level=numeric_level,
						format='%(asctime)s %(levelname)-8s %(message)s',
            	       	datefmt='%m-%d %H:%M',
					)

				else:

					logging.basicConfig(
						level=numeric_level,
						format='%(asctime)s %(name)-3s %(levelname)-8s %(message)s',
            	       	datefmt='%m-%d %H:%M',
						filename=logFile,
						filemode='w'
					)

			if parser.has_section("favorites"):
		
				for category, values in parser.items("favorites"):

					usersRaw = values.split(",")
					users = []

					for user in usersRaw:
						users.append(user.strip())

					self.favorites.append({"name" : category.strip(), "users" : users})

		except Exception as e:

			logging.warn("Unable to parsre config [%s]: %s" % (cfgFile, `e`))

	def run(self):

		logging.info("pyscmpd v%s started" % PYSCMPD_VERSION)

		mpd = scmpd.ScMpdServerDaemon(self.favorites, self.port)

		self.mainloop = gobject.MainLoop()
		self.mainloop.run()

try:

	pyscmpd = PyScMpd()
	pyscmpd.readConfig("./etc/pyscmpd.conf")
	pyscmpd.run()	

except KeyboardInterrupt:

	logging.info("pyscmpd v%s ended" % PYSCMPD_VERSION)

except Exception as e:

	logging.error("Exception occurred: %s" % `e`)

