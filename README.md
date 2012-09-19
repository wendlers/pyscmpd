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

 `test-src`		Some test/example sources
 `src`			Main sources four pyscmpd
 `doc`			Documentation
 `extlib`		External libraries (like python-mpd-server)


Prerequisites
-------------

* [python soundcloud API installed] (https://github.com/soundcloud/soundcloud-python) 
* [python-mpd-server API installed] (http://pympdserver.tuxfamily.org/) *included in ` extlib`*
* python-gst installed (apt-get install python-gst0.10)


Install
-------

A complete installation of the pyscmpd is not supported yet. This section briefly describes what steps 
are needed to make the "pyscmpd" runable from its project directory. 

** On Debian Based Linux Systems (e.g. Ubuntu, Respian, ...)

*1) Install soundcloud-python*

apt-get python setuptools:

	sudo apt-get install python-setuptools

clone the sources:

	git clone https://github.com/soundcloud/soundcloud-python.git
	
run the setup script

	cd soundcloud-python
	sudo python setup.py install
	
Note: internet connection is needed for this step, since the installer will go and fetch some dependencies from the net. 	

*2) Install python-gst*

apt-get the library:

	sudo apt-get install python-gst0.10
	
*3) Install python-mpd-server*

*DONT'T use the version from the python-mpd-server homepage!* 

"pyscmpd" needs a modified version included with "pyscmpd" sources. 

clone pyscmpd sources:

	git clone https://github.com/wendlers/pyscmpd.git
	
install python-mpd-server:

	cd pyscmpd/extlib/python-mpd-server
	sudo python setup.py install

*4) Get a decent MPD client*

I prefere ncmpcpp:

	sudo apt-get install ncmpcpp
	
Or for a GUI based client sonata:

	sudo apt-get install sonata
	
** On Other Linux Systems

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

