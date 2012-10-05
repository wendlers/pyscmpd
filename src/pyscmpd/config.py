#!/usr/bin/python

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

import os

USER_WORK_DIR	= ("%s/.pyscmpd" 		% os.getenv("HOME"))
DEF_PID_FILE	= ("%s/pyscmpd.pid" 	% USER_WORK_DIR)
DEF_CONF_FILE	= ("%s/pyscmpd.conf" 	% USER_WORK_DIR)
DEF_LOG_FILE	= ("%s/pyscmpd.log" 	% USER_WORK_DIR)
PLAYLIST_DIR	= ("%s/playlists"		% USER_WORK_DIR) 

CURR_PLAYLIST_KEY = "current"
