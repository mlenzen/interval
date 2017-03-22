"""Tests for interval."""
from datetime import date, datetime, timedelta, timezone

import pytest

from interval import (
	Month,
	Week,
	Day,
	ProperInterval,
	FixedInterval,
	Interval,
	)


def test_interval_init():
	i = Interval(datetime(2017, 3, 22), datetime(2017, 3, 24))
	assert i.delta == timedelta(days=2)
	assert i == Interval(datetime(2017, 3, 22), delta=timedelta(days=2))
	assert i == Interval(end=datetime(2017, 3, 24), delta=timedelta(days=2))


def test_interval_init_tzinfo_mismatch():
	with pytest.raises(TypeError):
		Interval(datetime(2017, 3, 22), datetime.now(tz=timezone.utc))


def test_interval_init_value_mismatch():
	with pytest.raises(ValueError):
		Interval(datetime(2017, 3, 22), datetime(2017, 3, 24), timedelta(days=1))


def test_interval_init_only_beg():
	with pytest.raises(ValueError):
		Interval(datetime(2017, 3, 22))


def test_interval_init_only_end():
	with pytest.raises(ValueError):
		Interval(end=datetime(2017, 3, 22))


def test_interval_init_only_delta():
	with pytest.raises(ValueError):
		Interval(delta=timedelta(days=2))


def test_interval_init_empty():
	with pytest.raises(ValueError):
		Interval()


def test_tzinfo():
	assert Interval(datetime.now(timezone.utc), delta=timedelta(days=1)).tzinfo == timezone.utc


def test_tzinfo_from_end():
	assert Interval(end=datetime.now(timezone.utc), delta=timedelta(days=2)).tzinfo == timezone.utc


def test_str():
	i = Interval(datetime(2017, 3, 22), datetime(2017, 3, 24))
	assert str(i) == '2017-03-22 00:00:00-2017-03-24 00:00:00'


def test_repr():
	i = Interval(datetime(2017, 3, 22), datetime(2017, 3, 24))
	assert repr(i) == 'Interval(beg=datetime.datetime(2017, 3, 22, 0, 0), end=datetime.datetime(2017, 3, 24, 0, 0))'


def test_bool_true():
	i = Interval(datetime(2017, 3, 22), datetime(2017, 3, 24))
	assert i

def test_bool_empty():
	assert not Interval(datetime(2017, 3, 22), datetime(2017, 3, 22))


def test_contains_middle():
	i = Interval(datetime(2017, 3, 22), datetime(2017, 3, 23))
	assert datetime(2017, 3, 22, 12) in i


def test_contains_beg():
	i = Interval(datetime(2017, 3, 22), datetime(2017, 3, 23))
	assert datetime(2017, 3, 22) in i


def test_contains_end():
	i = Interval(datetime(2017, 3, 22), datetime(2017, 3, 23))
	assert datetime(2017, 3, 23) not in i


def test_pace_middle():
	i = Interval(datetime(2017, 3, 22), datetime(2017, 3, 24))
	assert i.pace(datetime(2017, 3, 23)) == 0.5


def test_pace_prior():
	i = Interval(datetime(2017, 3, 22), datetime(2017, 3, 24))
	assert i.pace(datetime(2017, 3, 21)) == 0


def test_pace_post():
	i = Interval(datetime(2017, 3, 22), datetime(2017, 3, 24))
	assert i.pace(datetime(2017, 3, 27)) == 1


def test_pace_today():
	assert 0 < Month.containing(datetime.now()).pace() < 1


def test_run_rate():
	i = Interval(datetime(2017, 3, 22), datetime(2017, 3, 24))
	assert i.run_rate(datetime(2017, 3, 23, 12)) == 4 / 3


def test_add():
	i = Interval(datetime(2017, 3, 22), datetime(2017, 3, 23))
	j = Interval(datetime(2017, 3, 23), datetime(2017, 3, 24))
	assert i + j == Interval(datetime(2017, 3, 22), datetime(2017, 3, 24))


def test_equal_not():
	d1 = datetime(2017, 3, 22)
	d2 = datetime(2017, 3, 23)
	i = Interval(d1, d2)
	assert i != (d1, d2)


def test_add_reverse():
	i = Interval(datetime(2017, 3, 22), datetime(2017, 3, 23))
	j = Interval(datetime(2017, 3, 23), datetime(2017, 3, 24))
	assert j + i == Interval(datetime(2017, 3, 22), datetime(2017, 3, 24))


def test_add_nonconsecutive():
	i = Interval(datetime(2017, 3, 22), datetime(2017, 3, 23))
	j = Interval(datetime(2017, 3, 23, 12), datetime(2017, 3, 24))
	with pytest.raises(ValueError):
		i + j


def test_containing():
	assert Month.containing(datetime(2016, 5, 23)) == Month(year=2016, month=5)
	assert Day.containing(datetime(2016, 5, 23, 12, 0, 0)) == Day(datetime(2016, 5, 23))


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
