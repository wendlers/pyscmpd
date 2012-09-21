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

gobject.threads_init()

mpd = None
mainloop = None

try:

	# logging.basicConfig(level=logging.DEBUG)
	logging.basicConfig(level=logging.INFO)

	# TODO: do not hardcode favorites :-)
	favorites =  [ 
			{ 
				"name" : "test", 
				"users" : [ "griz", "betamaxx", "freudeamtanzen", ]
			},
			{
				"name" : "more",
				"users" : [ "barelylegit", "maddecent", "therealmccheese", "yellowmice", ]
			},
		]

	mpd = scmpd.ScMpdServerDaemon(favorites)

	mainloop = gobject.MainLoop()
	mainloop.run()

except KeyboardInterrupt:

	logging.info("Stopping SoundCloud MPD server")

except Exception as e:

	logging.error("Exception occurred: %s" % `e`)

finally:

	if not mpd == None:
		mpd.quit()

	if not mainloop == None:
		mainloop.quit()
