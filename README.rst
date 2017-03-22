interval README
###############

.. image:: https://travis-ci.org/mlenzen/interval.svg?branch=master
	:target: https://travis-ci.org/mlenzen/interval
	:alt: Build Status


.. image:: https://coveralls.io/repos/mlenzen/interval/badge.svg?branch=master
	:target: https://coveralls.io/r/mlenzen/interval?branch=master
	:alt: Coverage

Classes for dealing with date ranges

Why?
====
Dealing with months and years can be cumbersome in python.
Remembering which function to call from ``datetime.datetime`` or
``calendar`` or worse - having to roll your own each time.

Example
=======

.. code-block:: python

	>>> from datetime import datetime
	>>> from interval import Year, Quarter, Month, Day
	>>> dt = datetime(2017, 2, 8)
	>>> feb_2017 = Month.containing(dt)
	>>> feb_2017.run_rate(dt, 125)
	500.0
	>>> Month.divide(Year(2017))
	[Month(beg=datetime.datetime(2017, 1, 1, 0, 0), end=datetime.datetime(2017, 2, 1, 0, 0)),
	 Month(beg=datetime.datetime(2017, 2, 1, 0, 0), end=datetime.datetime(2017, 3, 1, 0, 0)),
	 Month(beg=datetime.datetime(2017, 3, 1, 0, 0), end=datetime.datetime(2017, 4, 1, 0, 0)),
	 Month(beg=datetime.datetime(2017, 4, 1, 0, 0), end=datetime.datetime(2017, 5, 1, 0, 0)),
	 Month(beg=datetime.datetime(2017, 5, 1, 0, 0), end=datetime.datetime(2017, 6, 1, 0, 0)),
	 Month(beg=datetime.datetime(2017, 6, 1, 0, 0), end=datetime.datetime(2017, 7, 1, 0, 0)),
	 Month(beg=datetime.datetime(2017, 7, 1, 0, 0), end=datetime.datetime(2017, 8, 1, 0, 0)),
	 Month(beg=datetime.datetime(2017, 8, 1, 0, 0), end=datetime.datetime(2017, 9, 1, 0, 0)),
	 Month(beg=datetime.datetime(2017, 9, 1, 0, 0), end=datetime.datetime(2017, 10, 1, 0, 0)),
	 Month(beg=datetime.datetime(2017, 10, 1, 0, 0), end=datetime.datetime(2017, 11, 1, 0, 0)),
	 Month(beg=datetime.datetime(2017, 11, 1, 0, 0), end=datetime.datetime(2017, 12, 1, 0, 0)),
	 Month(beg=datetime.datetime(2017, 12, 1, 0, 0), end=datetime.datetime(2018, 1, 1, 0, 0))]


:Author: Michael Lenzen
:Copyright: 2017 Michael Lenzen
:License: Apache License, Version 2.0
:Project Homepage: https://github.com/mlenzen/interval
