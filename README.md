pyscmpd
========

(c) 2012 Stefan Wendler
sw@kaltpost.de
http://gpio.kaltpost.de/


Introduction
------------

Python based sound-cloud music server talking MPD protocol.


NOTE: only some tests available yet ....
----------------------------------------


Project Directory Layout
------------------------

 `test-src`		Some test/example sources


Prerequisites
-------------

* [python soundcloud API installed] (https://github.com/soundcloud/soundcloud-python) 
* [python-mpd-server API installed] (http://pympdserver.tuxfamily.org/)
* python-gst installed (apt-get install python-gst0.10)


Usage
-----

In the main directory start "pyscmpd" with:

	./pyscmpd

Then connect to the daemon on port "9900", e. g. with ncmcpp:

	ncmpcpp -p 9900

To change the list of users to browse, edit "ROOT_USERS" in "./src/pympd.py". 
Whenever ROOT_USERS is changed, delte the meta data cache:

	rm scroot.cache

