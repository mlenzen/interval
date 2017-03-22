from datetime import date, datetime, timedelta

import pytest

from interval import (
	Month,
	Week,
	Day,
	ProperInterval,
	FixedInterval,
	)


def test_containing():
	assert Month.containing(date(2016, 5, 23)) == Month(year=2016, month=5)
	assert Day.containing(datetime(2016, 5, 23, 12, 0, 0)) == Day(datetime(2016, 5, 23))


def test_beginning():
	assert Day
	pass


def test_divide():
	pass


def test_custom_proper_interval():
	class FiscalYear(ProperInterval):

		@classmethod
		def containing(cls, dt):
			if dt < datetime(dt.year, 2, 1):
				year = dt.year - 1
			else:
				year = dt.year
			beg = datetime(year, 2, 1)
			end = datetime(year + 1, 2, 1)
			return cls(beg, end)

		def prev(self):
			beg = datetime(self.beg.year - 1, 2, 1)
			end = datetime(self.end.year - 1, 2, 1)
			return FiscalYear(beg, end)

		def __str__(self):
			return 'FY' + self.beg.year

	fy2016 = FiscalYear(datetime(2016, 2, 1), datetime(2017, 2, 1))
	assert fy2016.beg == datetime(2016, 2, 1)
	assert fy2016.end == datetime(2017, 2, 1)
	assert fy2016.delta == timedelta(days=366)
	assert FiscalYear.containing(datetime(2016, 3, 1)) == fy2016
	assert FiscalYear.containing(datetime(2017, 1, 23)) == fy2016
	assert FiscalYear.beginning(datetime(2016, 2, 1)) == fy2016
	with pytest.raises(ValueError):
		FiscalYear.beginning(datetime(2016, 1, 1))


def test_day_name():
	d = Day(datetime(2017, 3, 21))
	assert d.name == 'Tuesday'
	assert d.abbr == 'Tue'


def test_month_name():
	m = Month(2017, 3)
	assert m.name == 'March'
	assert m.abbr == 'Mar'


def test_inherit_fixed_interval_bad():
	"""Classes inheriting from FixedInterval must have a property delta."""
	class Bad(FixedInterval):
		pass

	with pytest.raises(TypeError):
		Bad(datetime.now())


def test_inherit_fixed_interval_good():
	class Good(FixedInterval):
		delta = timedelta(days=2)

	o = Good(datetime(2017, 3, 21))
	assert o.beg == datetime(2017, 3, 21)
	assert o.end == datetime(2017, 3, 23)
	assert o.delta == timedelta(days=2)


def test_fixed_interval_factory():
	cls = FixedInterval.create(timedelta(days=3))
	obj = cls(datetime(2017, 3, 21))
	assert obj.end == datetime(2017, 3, 24)
