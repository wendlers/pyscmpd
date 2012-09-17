#!/usr/bin/env python

from distutils.core import setup

setup(name='python-mpd-server',
      version='0.1',
      description='Create MPD Server in Python',
      author='kedals',
      author_email='kedals0@gmail.com',
      url='http://pympdserver.tuxfamily.org/',
      packages=["mpdserver"],
      license="GPLv3",
      classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Topic :: Multimedia :: Sound/Audio :: Players',
        'Topic :: Software Development :: Libraries :: Python Modules'],
      long_description="""
python-mpd-server permits to bind a player to a `MPD server <http://mpd.wikia.com>`_. 

You can control your player with a MPD client such as `Sonata
<http://sonata.berlios.de/>`_, `Gmpc <http://gmpc.wikia.com/wiki/>`_ or a command line tool `mpc <http://mpd.wikia.com/wiki/Client:Mpc>`_. This module
defines a server which manages client requests, parses a request and
generates a respond. A MPD command is a class that you can override.

Current supported features are:

- Playback control (play, stop, next, ...)
- Manage a playlist (add, move, delete, ...)
- Store/Load playlists
- User management via password command"""
      )
