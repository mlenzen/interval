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
	>>> from interval import Year, Quarter, Month, Day
	>>> dt = datetime(2017, 2, 8)
	>>> feb_2017 = Month.containing(dt)
	>>> feb_2017.run_rate(dt, 125)
	500.0


:Author: Michael Lenzen
:Copyright: 2017 Michael Lenzen
:License: Apache License, Version 2.0
:Project Homepage: https://github.com/mlenzen/interval
