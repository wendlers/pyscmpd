.. python-mpd-server documentation master file, created by
   sphinx-quickstart on Wed Mar 28 00:03:28 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. toctree::
   :maxdepth: 2



Welcome to python-mpd-server's documentation!
============================================= 
.. include:: readme.rst

How to use it
-------------
An example of a basic use is available in :ref:`example`.

python-mpd-server library defines a default server in :mod:`mpdserver` module
and some defaults commands in :mod:`command_skel` module.

To launch the server, you just have to create a Mpd object ::

   mpd=mpdserver.Mpd(listening_port)

This simulates a dummy mpd server which works with sonata, mpc and gmpc. 
To bind an existing player with mpd commmand, you then have to redefine commands.
For example, to bind play command with your player ::

    class Play(mpdserver.Command):
        def handle_args(self):yourplayer.play()
    mpdserver.MpdRequestHandler.commands['play']=Play

Launching python mpd server
----------------------------------
.. automodule:: mpdserver
   :members:


Defining Commands
----------------------------------
.. automodule:: command_base
   :members:

Command Squeletons
-------------------
.. automodule:: command_skel
   :members:



.. _example:

Basic Example
-------------
This is a simple example of how to use python-mpd-server.

.. literalinclude:: ../examples/mpd_server_example.py


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

