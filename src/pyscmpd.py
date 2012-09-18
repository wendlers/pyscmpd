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

import pyscmpd.scmpd as scmpd
import pyscmpd.gstplayer as gstplayer 

mpd = None

try:

	# logging.basicConfig(level=logging.DEBUG)
	logging.basicConfig(level=logging.INFO)

	player = gstplayer.GstPlayer() 

	# TODO: do not hardcode root :-)
	ROOT_USERS =  [ 
		"/users/griz", 
		"/users/betamaxx",				# TODO: this one has unicode / encoding errors 
		"/users/freudeamtanzen", 
		"/users/barelylegit", 
		"/users/maddecent" 				# TODO: this one has unicode / encoding errors
		]

	mpd = scmpd.ScMpdServerDaemon(ROOT_USERS, player)

except KeyboardInterrupt:

	logging.info("Stopping SoundCloud MPD server")

except Exception as e:

	logging.error("Exception occurred: %s" % `e`)

finally:

	if not mpd == None:
		mpd.quit()
