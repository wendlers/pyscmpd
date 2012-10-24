pyscmpd
========

(c) 2012 Stefan Wendler
sw@kaltpost.de
http://gpio.kaltpost.de/


Introduction
------------

*pyscmpd* stands for "Python SoundCloud Music Player Daemon". It is, as the name suggests, 
a Python based daemon, talking a subset of the [MPD] (http://www.musicpd.org/doc/protocol/) 
protocol. Instead of serving local MP3 files, it connects to [SoundCloud] (http://www.soundcloud.com)
and serves the streams found there. The user could configure, which parts of SoundCloud are
made available for browsing (e.g. by defining favorite groups or user). *pyscmpd* is intended to
run as a per user daemon, meaning it is designed to run multiple instances. 

Since *pyscmpd* uses the well known MPD protocol, a variety of 
[clients] (http://mpd.wikia.com/wiki/Clients) could be used as
a front end to the daemon. The once I am testing *pyscmpd* currently on are the 
curses based [ncmpcpp] (http://ncmpcpp.rybczak.net/) and the GTK based  
[sonata] (http://sonata.berlios.de/).

More information could be found at the following places:

* For more details on the architecture of *pyscmpd* see this [document] (https://github.com/wendlers/pyscmpd/blob/master/doc/PyScMPDArchitecture.txt). 
* For more details on the current implementation (including a list of MPD commands currently supported) see this [document] (https://github.com/wendlers/pyscmpd/blob/master/doc/PyScMPDImplementation.txt). 
* As a foundation for the core MPD protocol implementation, the [pympdserver] (http://pympdserver.tuxfamily.org/index.html) library is used. 


Main Features
-------------

The main features currently supported are:

* Browse a predefined set of favorite users  (in "~/.pyscmpd/pyscmpd.conf")
* Browse a predefined set of favorite groups (in "~/.pyscmpd/pyscmpd.conf")
* Browse the favorite tracks of a predefined set of users (in "~/.pyscmpd/pyscmpd.conf")
* Browse random users/groups
* Current play-list is persisted on SIGTERM and restored on next restart
* Save play-lists to a defined name 
* Load stored play-lists 
* Browse stored play-lists 
* Delete stored play-lists
* Clear stored play-lists
* Add tracks to current play-list
* Add tracks to stored play-list
* Change song order in current play-list
* Change song order in stored play-list
* Remove songs from current play-list
* Remove songs from stored play-list
* Clear current play-list
* Start/stop/pause/resume songs
* Control volume
* Elapsed song time and current song-time are transmitted to clients


Project Directory Layout
------------------------

 * `test-src`	 Some test/example sources
 * `src`		 Main sources four pyscmpd
 * `doc`		 Documentation
 * `extlib`		 External libraries (like python-mpd-server)
 * `README.md`	 This README
 * `pyscmpdctrl` Test-script to run "pyscmpd" from within the project directory
 * `setup.py`    Python setup script for installing "pyscmpd"
 * `MANIFEST.in` Meta-data for "setup.py"


Prerequisites
-------------

* [git] (http://git-scm.com/) for cloning the sources
* [Python] (http://python.org/) (2.6 or 2.7, not tested with 3)
* [python-setuptools] (http://pypi.python.org/pypi/setuptools) for installing soundcloud-python
* [python soundcloud API] (https://github.com/soundcloud/soundcloud-python) 
* [python-gst] (http://pygstdocs.berlios.de/)

For more detailed install instructions see next chapter.


Quick Install Instructions
--------------------------

The following instructions describe in short, how to install "pyscmpd" on a Raspberry Pi
with freshly installed Raspian. For more detailed setup instructions see the next chapter.

__Note:__ perform the following steps as user "pi".

*1) Install missing Debian packages*

	sudo apt-get install git python-setuptools python-gst0.10 gstreamer0.10-plugins-base gstreamer0.10-plugins-good gstreamer0.10-plugins-bad gstreamer0.10-plugins-ugly gstreamer0.10-alsa jackd ncmpcpp

*2) Install soundcloud python API*

	sudo easy_install soundcloud

*3) Install pysmpd*

	mkdir $HOME/src
	cd $HOME/src
	git clone https://github.com/wendlers/pyscmpd.git
	cd pyscmpd
	sudo python setup.py install

*4) Autostart pyscmpd with the desktop*

	mkdir $HOME/.config/autostart
	cp ./etc/pyscmpd.desktop $HOME/.config/autostart/.

*5) Run daemon, connect to it*

	pyscmpdctrl start
	ncmpcpp -p 9900

Detailed Install Instructions
-----------------------------

__On Debian Based Linux Systems (e.g. Ubuntu, Raspian, ...)__

For the following steps, it is assumed, that `$HOME/src`is your working directory:

	mkdir $HOME/src

*1) Install soundcloud-python*

apt-get python setuptools:

	sudo apt-get install python-setuptools

clone the sources:

	cd $HOME/src
	git clone https://github.com/soundcloud/soundcloud-python.git
	
run the setup script

	cd soundcloud-python
	sudo python setup.py install
	
__Note:__ Internet connection is needed for this step, since the installer will go and fetch some dependencies from the net. 	

*2) Install python-gst and dependencies*

apt-get the library:

	sudo apt-get install python-gst0.10 

on a fresh Raspian, I needed additionally the following:

	sudo apt-get install gstreamer0.10-plugins-base gstreamer0.10-plugins-good gstreamer0.10-plugins-bad gstreamer0.10-plugins-ugly gstreamer0.10-alsa jackd 
	
*3) Install pyscmpd*

clone pyscmpd sources:

	cd $HOME/src
	git clone https://github.com/wendlers/pyscmpd.git 
	
install pyscmpd:

	cd pyscmpd
	sudo python setup.py install

*3.1) Optional: autostart daemon with LXDE*

If you like to start "pyscmpd" with your LXDE desktop on a raspberry pi, you could create the file "pyscmpd.desktop" 
under "$HOME/.config/autostart" with the following:

	[Desktop Entry]
	Name=pyscmpd
	Comment=Python based soundcloud player using the MPD protocol
	Exec=pyscmpdctrl restart 
	Icon=sound_section
	Terminal=false
	Type=Application
	Categories=Audio

Next time your desktop is started, "pyscmpd" will also be started.

*4) Get a decent MPD client*

I prefer [ncmpcpp] (http://ncmpcpp.rybczak.net/):

	sudo apt-get install ncmpcpp
	
Or for a GUI based client [sonata] (http://sonata.berlios.de/):

	sudo apt-get install sonata
	
__On Other Linux Systems__

To be done ...


Usage
-----

In the main directory start "pyscmpd" daemon with:

	pyscmpdctrl start

A default configuration is created under "~/.pyscmpd/pyscmp.conf". To change the port 
(default 9900), logging, or favorite users to browse change this file. 

By default, the log output of the daemon could be viewed by:

	tail -f ~/.pyscmpd/pyscmpd.log

Now you should be able to connect to the daemons default port 9900, e. g. with ncmpcpp:

	ncmpcpp -p 9900

To stop the daemon use:

	pyscmpdctrl stop

In case "pyscmpdctrl" complains about the PID file already existing, and you are sure the 
daemon is not running yet, you could use the following command to cleanup the PID file:
	
	pyscmpdctrl rmpid 

For debugging, it may be useful to start the daemon in foreground. This could be done by:

	pyscmpdctrl --foreground start

By doing so, log messages are printed to "stdout", while the log-file specified will be ignored.


Customize
---------

__Favorite Users__

To modify the list of your favorite users to browse, edit the *[favorite-users]* section 
in "~/.pyscmpd/pyscmp.conf". The format used for favorite users is:
	 
	category1: user1, user2, ...
	category2: user1, user2, ...
	...

*categoryN* is then shown in the browser as sub-folder folder of *users* folder, containing all 
the users specified. *userN* is the user name of a soundcloud user as shown in the URL. E.g. 
"griz" for [GRiZ] (http://soundcloud.com/griz).

__Favorite Groups__

To define the favorite groups shown in the browser, add them under the *[favorite-groups]* section
in "~/.pyscmpd/pyscmp.conf". The format used for favorite users is:

	categroy1: group1, group2, ...
	categroy2: group1, group2, ...
	...
	
*categoryN* is shown in the browser as sub-folder of the *groups* folder. *groupN* is the group name as shown 
in the URL when browsing a group. E.g. "deep-house-4".

__Favorite Favorites__

To define a set of users who's favorite tracks are listed under the *favorites* folder, add them to the 
*[favorite-favorites]* section in  "~/.pyscmpd/pyscmp.conf". The format used for favorite favorites is:

	category1: user1, user2, ...
	category2: user1, user2, ...
	...
	
For each *categoryN*, a sub-folder of *favorites* is shown in the browser. When *userN* is opened, all the favorite tracks of that user are listed.
	
__Complete Example__

The following shows a complete sample for the two mentioned section as seen in *pysmpc.conf*:

	[favorite-users]
	ghettoswing : maddecent, barelylegit
	electrosoul: griz
	deep-minimal-house: grumoh
	tech-house: beatkind, atmosphererecords

	[favorite-groups]
	house: deep-house-4, minimal-tech-house, 
	swing: swing-fever-electroswing-group, ghettoswing-and-swingstep

	[favorite-favorites]
	me: kaltpost 
	friends: somefrinduser 

__Note:__ Each time "~/.pyscmpd/pyscmp.conf" is modified, the daemon needs to be restarted by:

	pyscmpdctrl restart

__Note:__ an example configuration could be found in the project directory under [./etc/pyscmpd.conf] (https://github.com/wendlers/pyscmpd/blob/master/etc/pyscmpd.conf).

