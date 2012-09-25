#!/usr/bin/env python

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
This file is part of the pyscmpd project. To install pyscmpd:

  sudo python setup.py install  

'''

import os

from distutils.core import setup
from distutils.sysconfig import get_python_lib

setup(name='pyscmpd',
	version='0.1',
	description='sound-cloud music server daemon',
	long_description='Python based sound-cloud music server talking MPD protocol',
	author='Stefan Wendler',
	author_email='sw@kaltpost.de',
	url='http://www.kaltpost.de/',
	license='GPL 3.0',
	platforms=['Linux'],
	packages = ['pyscmpd', 'mpdserver'],
	package_dir = {'pyscmpd' : 'src/pyscmpd', 'mpdserver' : 'extlib/python-mpd-server/mpdserver' },
	requires = ['soundcloud(>=0.3.1)']
)

# Symlink starter
linkSrc = "%s/pyscmpd/pyscmpdctrl.py" % get_python_lib(False, False, '/usr/local')
linkDst = "/usr/local/bin/pysmpdctrl"

if not os.path.lexists(linkDst):
	os.symlink(linkSrc, linkDst)
