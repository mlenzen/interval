"""interval - a library for handling periods of time.

Intervals are periods of time - a timedelta with a start date.

ProperIntervals are Intervals that correspond to named periods of time like
dates on a calendar instead of an arbitrary 24 hour period. ProperIntervals
can also vary in length like Months or Years.

Intervals are immutable.

Intervals are inclusive of the beginning and exclusive of the end.
"""
from abc import ABCMeta, abstractmethod
import calendar
from datetime import datetime, date, timedelta, tzinfo

__version__ = '0.1.0'


class Interval():
	"""An Interval is a specific timespan, with fixed beginning and end datetimes.

	At least 2 of beg, end and delta must be passed to determine the interval.
	If all 3 are passed, then `end - beg == delta`.

	Args:
		beg: The start of the interval, inclusive.
		end: The end of the interval, exclusive.
		delta: The length of the interval.
	Raises:
		TypeError: If beg has tzinfo and end does not or vice versa.
		ValueError: If at least 2 args are not passed or all 3 are but don't
			match
	"""

	def __init__(
			self,
			beg: datetime = None,
			end: datetime = None,
			delta: timedelta = None,
			) -> None:
		"""Create an Interval with arbitrary beg and end datetimes."""
		if beg:
			self._beg = beg
			if delta:
				self._delta = delta
				if end and self.end != end:
					raise ValueError('delta != end - beg')
			else:
				if not end:
					raise ValueError('Must pass at least 2 of beg, end & delta')
				# Implicitly check that end and beg eith both have or don't
				# have tzinfo
				self._delta = end - beg
		else:
			if not (end and delta):
				raise ValueError('Must pass at least 2 of beg, end & delta')
			self._beg = end - delta
			self._delta = delta

	def __repr__(self):
		return '{cls}(beg={self.beg!r}, end={self.end!r})'.format(
			cls=self.__class__.__name__,
			self=self,
			)

	def __str__(self):
		return '{self.beg}-{self.end}'.format(self=self)

	def __bool__(self):
		return self.end > self.beg

	@property
	def beg(self) -> datetime:
		"""The beginning of this Interval, inclusive."""
		return self._beg

	@property
	def end(self) -> datetime:
		"""The end of this Interval, exclusive."""
		return self.beg + self.delta

	@property
	def delta(self) -> timedelta:
		"""The length of this interval."""
		return self._delta

	@property
	def tzinfo(self) -> tzinfo:
		"""The tzinfo for this Interval."""
		return self.beg.tzinfo

	def __contains__(self, d: datetime):
		return self.beg <= d < self.end

	def __eq__(self, other):
		if not isinstance(other, Interval):
			return False
		return (self.beg, self.end) == (other.beg, other.end)

	def pace(self, dt=None) -> float:
		"""Return how far through this interval dt is.

		If dt isn't passed use datetime.now()
		"""
		if dt is None:
			dt = datetime.now(self.tzinfo)
		if dt < self.beg:
			return 0.0
		elif dt > self.end:
			return 1.0
		else:
			return (dt - self.beg) / self.delta

	def run_rate(self, dt: datetime = None, value=1):
		"""Return the run rate for value at dt.

		If dt is x% through the Interval, calulate the basic run rate for value.
		"""
		return value / self.pace(dt)

	def __add__(self, other):
		if other.end == self.beg:
			return Interval(other.beg, self.end)
		elif self.end == other.beg:
			return Interval(self.beg, other.end)
		else:
			raise ValueError('Interval is not consecutive with this Interval')


class _IterableInterval(metaclass=ABCMeta):
	"""Mixin for classes that can be iterated over."""

	@classmethod
	@abstractmethod
	def beginning(cls, dt: datetime):
		"""Return an Interval of this type beginning on dt."""
		raise NotImplementedError

	@classmethod
	def ending(cls, dt: datetime):
		"""Return the instance of this class ending at datetime dt."""
		return cls.beginning(dt).prev()

	def next(self):
		"""Return the next Interval of this type."""
		return self.beginning(self.end)

	@abstractmethod
	def prev(self):
		"""Return the previous Interval of this type."""
		raise NotImplementedError

	@classmethod
	def divide(cls, interval: Interval, extras_action='raise'):
		"""Divide an interval into Intervals of this type.

		extras_action can be 'raise', 'ignore', or 'partial'
		'raise' - raise a ValueError if the passed IntervalType does not evenly
			divide this Interval.
		'ignore' - ignore parts of this Interval to divide self into subintervals
			of interval_type
		'partial' - return partial intervals not matching interval_type where
			necessary
		"""
		possible_values = ('raise', 'ignore', 'partial')
		if extras_action not in possible_values:
			poss_values_str = '","'.join(possible_values)
			raise ValueError('extras_action must be one of "%s"' % poss_values_str)
		out = []
		sub_interval = cls.containing(interval.beg)
		if interval.beg != sub_interval.beg:
			if extras_action == 'raise':
				raise ValueError(
					'The beginning of interval is not the beginning of a ' +
					cls.__name__
					)
			elif extras_action == 'partial':
				out.append(Interval(beg=interval.beg, end=sub_interval.end))
			else:
				out.append(sub_interval)
		else:
			out.append(sub_interval)
		sub_interval = sub_interval.next()
		while sub_interval.end <= interval.end:
			out.append(sub_interval)
			sub_interval = sub_interval.next()
		if sub_interval.beg != interval.end:
			if extras_action == 'raise':
				raise ValueError(
					'The end of interval is does not line up with ' +
					cls.__name__
					)
			elif extras_action == 'partial':
				out.append(Interval(beg=sub_interval.beg, end=interval.end))
		return out

	def divide_into(self, interval_type):
		"""Inverse way of calling `divide`.

		Args:
			interval_type (_IterableInterval): The type of interval to divide self into.
			extras_action: See `divide`
		"""
		return interval_type.divide(self)

	def iter(self, count=None, end=None, reverse=False):
		"""Generate Intervals of this class starting with self.

		Args:
			count: If not None, generate at most count Intervals
			end: If not None, stop before this is yielded
			reverse: If true, generate backwards
		"""
		yielded_count = 0
		next_interval = self
		while True:
			if count is not None and yielded_count >= count:
				break
			if next_interval == end:
				break
			yield next_interval
			yielded_count += 1
			if reverse:
				next_interval = next_interval.prev()
			else:
				next_interval = next_interval.next()


class ProperInterval(Interval, _IterableInterval, metaclass=ABCMeta):
	"""A Interval representing a span on a clock or calendar, eg. a month or hour.

	This is in contrast to a Interval starting at an abitrary point time.
	1:00-2:00 can be a ProperInterval while 1:14-2:14 cannot.

	ProperIntervals can be compared because they cannot overlap.

	To create a new ProperInterval, inherit from ProperInterval and implement
	classmthod `containing` and method `prev`.
	"""

	@classmethod
	@abstractmethod
	def containing(cls, dt: datetime):
		"""Return the instance of this class containing datetime dt."""
		raise NotImplementedError

	@classmethod
	def beginning(cls, dt: datetime):
		"""Return the instance of this class beginning at datetime dt."""
		interval = cls.containing(dt)
		if interval.beg != dt:
			raise ValueError('dt is not the beggining of a {cls}'.format(cls=cls))
		return interval

	@classmethod
	def first_after(cls, dt: datetime):
		"""Return the first ProperInterval following datetime."""
		return cls.containing(dt).next()

	@classmethod
	def last_before(cls, dt: datetime):
		"""Return last ProperInterval before datetime."""
		return cls.containing(dt).prev()

	@classmethod
	def _check_type(cls, other):
		return isinstance(other, cls)

	def __lt__(self, other):
		if not self._check_type(other):
			return NotImplemented
		return self.beg < other.beg

	def __gt__(self, other):
		if not self._check_type(other):
			return NotImplemented
		return self.beg > other.beg

	def __le__(self, other):
		if not self._check_type(other):
			return NotImplemented
		return self.beg <= other.beg

	def __ge__(self, other):
		if not self._check_type(other):
			return NotImplemented
		return self.beg >= other.beg

	def __str__(self):
		return '<{type} starting {self.beg}>'.format(
			type=type(self),
			self=self,
			)


class Year(ProperInterval):
	"""A ProperInterval for a Year."""

	def __init__(self, year: int, tzinfo: tzinfo = None) -> None:
		self._year = year
		self._tzinfo = tzinfo

	def __str__(self):
		return str(self.year)

	@property
	def year(self) -> int:
		return self._year

	@property
	def tzinfo(self) -> tzinfo:
		return self._tzinfo

	@property
	def beg(self) -> datetime:
		return datetime(self.year, 1, 1, tzinfo=self.tzinfo)

	@property
	def end(self) -> datetime:
		return datetime(self.year + 1, 1, 1, tzinfo=self.tzinfo)

	@property
	def delta(self) -> timedelta:
		return self.end - self.beg

	@classmethod
	def containing(cls, dt: datetime):
		return cls(dt.year, tzinfo=dt.tzinfo)

	def prev(self):
		return type(self)(self.year - 1, self.tzinfo)

	def isleap(self):
		return calendar.isleap(self.year)

	def date(self, month, day):
		return date(self.year, month, day)

	def datetime(self, *args, **kwargs):
		if 'tzinfo' not in kwargs:
			kwargs['tzinfo'] = self.tzinfo
		return datetime(self.year, *args, **kwargs)


class Quarter(ProperInterval):
	"""ProperInterval for a quarter (of a year)."""

	def __init__(self, year: int, quarter: int, tzinfo: tzinfo = None) -> None:
		if not (1 <= quarter <= 4):
			raise ValueError('quarter must be 1, 2, 3 or 4')
		self._year = year
		self._quarter = quarter
		self._tzinfo = tzinfo

	def __str__(self):
		return '{self.year}-Q{self.quarter}'.format(self=self)

	@property
	def year(self) -> int:
		return self._year

	@property
	def quarter(self) -> int:
		return self._quarter

	@property
	def tzinfo(self) -> tzinfo:
		return self._tzinfo

	@property
	def beg(self) -> datetime:
		month = (self.quarter - 1) * 3 + 1
		return datetime(self.year, month, 1, tzinfo=self.tzinfo)

	@property
	def end(self) -> datetime:
		if self.quarter == 4:
			year = self.year + 1
			month = 1
		else:
			year = self.year
			month = self.quarter * 3 + 1
		return datetime(year, month, 1, tzinfo=self.tzinfo)

	@property
	def delta(self) -> timedelta:
		return self.end - self.beg

	@classmethod
	def containing(cls, dt: datetime):
		quarter = dt.month // 3 + 1
		return cls(dt.year, quarter, tzinfo=dt.tzinfo)

	def prev(self):
		if self.quarter == 1:
			year = self.year - 1
			quarter = 4
		else:
			year = self.year
			quarter = self.quarter - 1
		return type(self)(year, quarter, self.tzinfo)


class Month(ProperInterval):
	"""ProperInterval for a month."""

	def __init__(self, year: int, month: int, tzinfo: tzinfo = None) -> None:
		if not (1 <= month <= 12):
			raise ValueError
		self._year = year
		self._month = month
		self._tzinfo = tzinfo

	def __str__(self):
		return '{self.name} {self.year}'.format(self=self)

	@property
	def year(self) -> int:
		return self._year

	@property
	def month(self) -> int:
		return self._month

	@property
	def tzinfo(self) -> tzinfo:
		return self._tzinfo

	@property
	def beg(self) -> datetime:
		return datetime(self.year, self.month, 1, tzinfo=self.tzinfo)

	@property
	def end(self) -> datetime:
		# return self.beg + self.delta
		if self.month == 12:
			year = self.year + 1
			month = 1
		else:
			year = self.year
			month = self.month + 1
		return datetime(year, month, 1, tzinfo=self.tzinfo)

	@property
	def delta(self):
		return timedelta(days=self.num_days())

	def num_days(self):
		return calendar.monthrange(self.year, self.month)[1]

	@classmethod
	def containing(cls, dt: datetime):
		return cls(dt.year, dt.month, tzinfo=dt.tzinfo)

	@property
	def name(self):
		return calendar.month_name[self.month]

	@property
	def abbr(self):
		return calendar.month_abbr[self.month]

	def prev(self):
		if self.month == 1:
			year = self.year - 1
			month = 12
		else:
			year = self.year
			month = self.month - 1
		return Month(year, month, self.tzinfo)

	def date(self, day):
		return date(self.year, self.month, day)

	def datetime(self, *args, **kwargs):
		if 'tzinfo' not in kwargs:
			kwargs['tzinfo'] = self.tzinfo
		return datetime(self.year, self.month, *args, **kwargs)


class FixedIntervalType(ABCMeta):
	"""Type for FixedIntervals.

	FixedIntervalTypes have an attribute delta that is the length of all
	Intervals of that type.

	FixedIntervalTypes can be multiplied by a number to get a new
	FixedIntervalType.
	"""

	def __mul__(self, value):
		return self.create(value * self.delta)


class FixedInterval(Interval, _IterableInterval, metaclass=FixedIntervalType):
	"""A Interval of a fixed length."""

	def __init__(self, beg: datetime) -> None:
		self._beg = beg

	@property
	@classmethod
	@abstractmethod
	def delta(self) -> timedelta:
		raise NotImplementedError

	@property
	def end(self) -> datetime:
		return self.beg + self.delta

	def prev(self):
		return self.ending(self.beg)

	@classmethod
	def beginning(cls, d: datetime):
		"""Return the instance of this class beginning at datetime d."""
		return cls(d)

	@classmethod
	def ending(cls, d: datetime):
		"""Return the instance of this class beginning at datetime d."""
		return cls(d - cls.delta)

	@classmethod
	def create(cls, delta: timedelta, name='FixedInterval'):
		"""Create a FixedIntervalType with delta delta."""
		return type(name, (cls, ), {'delta': delta})


class Week(FixedInterval, ProperInterval):
	"""ProperInterval for a week."""

	delta = timedelta(days=7)

	@classmethod
	def containing(cls, dt: datetime, starts_on: int = None):
		"""Create the week that starts on d.

		Use calendar.setfirstweekday or pass starts_on to set the first
		day of the week, must be 0(MONDAY) through 6 (SUNDAY).
		"""
		if not starts_on:
			starts_on = calendar.firstweekday()
		days_prior = (dt.weekday() + 7 - starts_on) % 7
		day_start = dt.replace(hour=0, minute=0, second=0, microsecond=0)
		week_start = day_start - timedelta(days=days_prior)
		return cls(week_start)


class _SubDay():
	"""A mixin for ProperIntervals shorter than a day."""

	@property
	def year(self):
		return self.beg.year

	@property
	def month(self):
		return self.beg.month

	@property
	def day(self):
		return self.beg.day

	def weekday(self):
		return self.beg.weekday()

	def isoweekday(self):
		return self.beg.isoweekday()

	@property
	def date(self):
		return self.beg.date()


class Day(FixedInterval, ProperInterval, _SubDay):
	"""ProperInterval for a day."""

	delta = timedelta(days=1)

	@classmethod
	def containing(cls, dt: datetime):
		d = datetime(dt.year, dt.month, dt.day)
		return cls(d)

	@property
	def name(self):
		return calendar.day_name[self.weekday()]

	@property
	def abbr(self):
		return calendar.day_abbr[self.weekday()]


class Hour(FixedInterval, ProperInterval, _SubDay):
	"""ProperInterval for an hour."""

	delta = timedelta(hours=1)

	@classmethod
	def containing(cls, dt: datetime):
		dt = dt.replace(minute=0, second=0, microsecond=0)
		return cls(dt)


class Minute(FixedInterval, ProperInterval, _SubDay):
	"""ProperInterval for a minute."""

	delta = timedelta(minutes=1)

	@classmethod
	def containing(cls, dt: datetime):
		dt = dt.replace(second=0, microsecond=0)
		return cls(dt)


class Second(FixedInterval, ProperInterval, _SubDay):
	"""ProperInterval for a second."""

	delta = timedelta(seconds=1)

	@classmethod
	def containing(cls, dt: datetime):
		dt = dt.replace(microsecond=0)
		return cls(dt)


class MilliSecond(FixedInterval, ProperInterval, _SubDay):
	"""ProperInterval for a millisecond."""

	delta = timedelta(microseconds=1000)

	@classmethod
	def containing(cls, dt: datetime):
		microsecond = int(round(dt.microsecond, -3))
		dt = dt.replace(microsecond=microsecond)
		return cls(dt)


class MicroSecond(FixedInterval, ProperInterval, _SubDay):
	"""ProperInterval for a microsecond."""

	delta = timedelta(microseconds=1)

	@classmethod
	def containing(cls, dt: datetime):
		return cls(dt)
