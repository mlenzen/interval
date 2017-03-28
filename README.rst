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
Dealing with months and years can be cumbersome and verbose in python.
Remembering which function to call from ``datetime.datetime`` or
``calendar`` or worse - having to roll your own each time.

Example
=======

.. code-block:: python

	>>> from datetime import datetime, timedelta
	>>> from interval import Year, Quarter, Month, Day, FixedInterval
	>>> dt = datetime(2017, 2, 8)
	>>> # Return the Month containing a datetime
	>>> feb_2017 = Month.containing(dt)
	>>> # Calculate the percent complete
	>>> feb_2017.pace(dt)
	0.25
	>>> # Get related Intervals
	>>> feb_2017.next()
	Month(beg=datetime.datetime(2017, 3, 1, 0, 0), end=datetime.datetime(2017, 4, 1, 0, 0))
	>>> # Divide Intervals into Intervals of other types
	>>> Month.divide(Quarter(2017, 1))
	[Month(beg=datetime.datetime(2017, 1, 1, 0, 0), end=datetime.datetime(2017, 2, 1, 0, 0)), Month(beg=datetime.datetime(2017, 2, 1, 0, 0), end=datetime.datetime(2017, 3, 1, 0, 0)), Month(beg=datetime.datetime(2017, 3, 1, 0, 0), end=datetime.datetime(2017, 4, 1, 0, 0))]
	>>> # Alternatively written
	>>> Quarter(2017, 1).divide_into(Month)
	[Month(beg=datetime.datetime(2017, 1, 1, 0, 0), end=datetime.datetime(2017, 2, 1, 0, 0)), Month(beg=datetime.datetime(2017, 2, 1, 0, 0), end=datetime.datetime(2017, 3, 1, 0, 0)), Month(beg=datetime.datetime(2017, 3, 1, 0, 0), end=datetime.datetime(2017, 4, 1, 0, 0))]
	>>> # A FixedInterval is an Interval that alwas has the same delta (unlike a Month or Year)
	>>> Fortnight = FixedInterval.create(timedelta(weeks=2), name='Fortnight')
	>>> Fortnight.ending(datetime(2017, 2, 8))
	Fortnight(beg=datetime.datetime(2017, 1, 25, 0, 0), end=datetime.datetime(2017, 2, 8, 0, 0))


:Author: Michael Lenzen
:Copyright: 2017 Michael Lenzen
:License: Apache License, Version 2.0
:Project Homepage: https://github.com/mlenzen/interval
