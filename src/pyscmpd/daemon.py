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

import sys
import os
import time
import atexit
import logging
import gobject
import pyscmpd.scmpd as scmpd

from signal import SIGTERM 
from ConfigParser import SafeConfigParser

PYSCMPD_VERSION="0.0.1"

gobject.threads_init()

class PyScMpd:

	stdin			= None
	stdout 			= None
	stderr			= None
	pidfile			= None
	mpd 			= None
	mainloop 		= None
	port			= 9900

	favoriteUsers	= None 
	favoriteGroups	= None 

	def __init__(self, pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):

		self.stdin 			= stdin
		self.stdout 		= stdout
		self.stderr 		= stderr
		self.pidfile 		= pidfile

		self.favoriteUsers 	= []
		self.favoriteGroups	= []

	def daemonize(self):

		try: 

			pid = os.fork() 
			if pid > 0:
				# exit first parent
				sys.exit(0) 

		except OSError, e: 

			sys.stderr.write("Fork failed: %d (%s)\n" % (e.errno, e.strerror))
			sys.exit(1)
	
		# decouple from parent environment
		os.chdir("/") 
		os.setsid() 
		os.umask(0) 
	
		# do second fork
		try: 

			pid = os.fork() 
			if pid > 0:
				# exit from second parent
				sys.exit(0) 

		except OSError, e: 

			sys.stderr.write("Fork failed: %d (%s)\n" % (e.errno, e.strerror))
			sys.exit(1) 
	
		# redirect standard file descriptors
		sys.stdout.flush()
		sys.stderr.flush()

		si = file(self.stdin, 'r')
		so = file(self.stdout, 'a+')
		se = file(self.stderr, 'a+', 0)

		os.dup2(si.fileno(), sys.stdin.fileno())
		os.dup2(so.fileno(), sys.stdout.fileno())
		os.dup2(se.fileno(), sys.stderr.fileno())
	
		# write pidfile
		atexit.register(self.delpid)
		pid = str(os.getpid())
		file(self.pidfile,'w+').write("%s\n" % pid)

	def delpid(self):

		os.remove(self.pidfile)

	def start(self):

		# Check for a pidfile to see if the daemon already runs
		try:

			pf = file(self.pidfile,'r')
			pid = int(pf.read().strip())
			pf.close()

		except IOError:

			pid = None
	
		if pid:

			sys.stderr.write("Pidfile %s already exist. Daemon already running?\n" % self.pidfile)
			sys.exit(1)
		
		# Start the daemon
		self.daemonize()
		self.run()

	def stop(self):

		# Get the pid from the pidfile
		try:

			pf = file(self.pidfile,'r')
			pid = int(pf.read().strip())
			pf.close()

		except IOError:

			pid = None
	
		if not pid:

			sys.stderr.write("Pidfile %s does not exist. Daemon not running?\n" % self.pidfile)
			return 

		# Try killing the daemon process	
		try:

			while 1:
				os.kill(pid, SIGTERM)
				time.sleep(0.1)

		except OSError:

			if os.path.exists(self.pidfile):
				os.remove(self.pidfile)

	def restart(self):

		self.stop()
		self.start()

	def readConfig(self, cfgFile, foreground=False):

		try:
			with open(cfgFile): pass
		except:
			sys.stderr.write("Unable to open config-file: %s\n" % cfgFile)
			sys.exit(1)
		
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

				if foreground or logFile == None:

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
						filemode='a'
					)
					
					sys.stdout.write("Logging to file: %s\n" % logFile)

			if parser.has_section("favorite-users"):
		
				for category, values in parser.items("favorite-users"):

					usersRaw = values.split(",")
					users = []

					for user in usersRaw:
						users.append(user.strip())

					self.favoriteUsers.append({"name" : category.strip(), "users" : users})

			if parser.has_option("favorite-groups", "groups"):
		
				groupsRaw = parser.get("favorite-groups", "groups").split(",") 
				groups = []

				for group in groupsRaw:
					self.favoriteGroups.append(group.strip())

		except Exception as e:

			logging.warn("Unable to parsre config [%s]: %s" % (cfgFile, `e`))


	def run(self):

		logging.info("pyscmpd v%s started" % PYSCMPD_VERSION)
		mpd = scmpd.ScMpdServerDaemon(self.favoriteUsers, self.favoriteGroups, self.port)

		self.mainloop = gobject.MainLoop()
		self.mainloop.run()

