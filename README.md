pyscmpd
========

(c) 2012 Stefan Wendler
sw@kaltpost.de
http://gpio.kaltpost.de/


Introduction
------------

Python based sound-cloud music server talking MPD protocol.


NOTE: only basic MPD server daemon available yet
------------------------------------------------


Project Directory Layout
------------------------

 * `test-src`		Some test/example sources
 * `src`		Main sources four pyscmpd
 * `doc`		Documentation
 * `extlib`		External libraries (like python-mpd-server)


Prerequisites
-------------

* [Python] (http://python.org/) (2.6 or 2.7, not tested with 3)
* [python-setuptools] (http://pypi.python.org/pypi/setuptools) for installing soundcloud-python
* [git] (http://git-scm.com/) for cloning the sources
* [python soundcloud API installed] (https://github.com/soundcloud/soundcloud-python) 
* [python-mpd-server API installed] (http://pympdserver.tuxfamily.org/) *included in ` extlib`*
* [python-gst installed] (http://pygstdocs.berlios.de/)

For more detailed install instructions see next chapter.

Install
-------

A complete installation of the pyscmpd is not supported yet. This section briefly describes what steps 
are needed to make the "pyscmpd" runable from its project directory. 

_On Debian Based Linux Systems (e.g. Ubuntu, Respian, ...)_

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
	
Note: internet connection is needed for this step, since the installer will go and fetch some dependencies from the net. 	

*2) Install python-gst and dependencies*

apt-get the library:

	sudo apt-get install python-gst0.10 gstreamer0.10-plugins-base
	
*3) Install pyscmpd*

clone pyscmpd sources:

	cd $HOME/src
	git clone https://github.com/wendlers/pyscmpd.git
	
Note: "pyscmpd" has no installer yet, and needs to be run from its project directory 
(see "Usage" chapter for more infromation).

*4) Get a decent MPD client*

I prefere [ncmpcpp] (http://ncmpcpp.rybczak.net/):

	sudo apt-get install ncmpcpp
	
Or for a GUI based client [sonata] (http://sonata.berlios.de/):

	sudo apt-get install sonata
	
_On Other Linux Systems_

To be done ...


Usage
-----

In the main directory start "pyscmpd" with:

	./pyscmpd

Then connect to the daemon on port "9900", e. g. with ncmcpp:

	ncmpcpp -p 9900

To change the list of users to browse, edit "ROOT_USERS" in "./src/pympd.py". 
Whenever ROOT_USERS is changed, delte the meta data cache:

	rm scroot.cache

