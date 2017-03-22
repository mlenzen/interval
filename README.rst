interval README
###############

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
	>>> from interval import Year, Quarer, Month, Day
	>>> q1_2016 = Quarer(2016, 1)
	>>> for month in q1_2016.divide(Month):
	...:    print(month)
	'January 2016'
	'Febuary 2016'
	'March 2016'
	>>> dt = datetime(2017, 2, 8)
	>>> feb_2017 = Month.containing(dt)
	>>> feb_2017.run_rate(dt, 125)
	500


:Author: Michael Lenzen
:Copyright: 2017 Michael Lenzen
:License: Apache License, Version 2.0
:Project Homepage: https://github.com/mlenzen/interval
