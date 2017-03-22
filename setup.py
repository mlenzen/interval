"""setup.py for interval."""
from os.path import dirname, join

from setuptools import setup


setup(
	name='interval',
	py_modules=['interval'],
	version='0.1.0',
	description='Intervals of time',
	author='Michael Lenzen',
	author_email='m.lenzen@gmail.com',
	license='Apache License, Version 2.0',
	# url='',
	keywords=[
		'interval',
		'date range',
		'timespan',
		],
	classifiers=[
		'Development Status :: 4 - Beta',
		'Intended Audience :: Developers',
		'License :: OSI Approved :: Apache Software License',
		'Operating System :: OS Independent',
		'Programming Language :: Python',
		'Programming Language :: Python :: 2',
		'Programming Language :: Python :: 2.6',
		'Programming Language :: Python :: 2.7',
		'Programming Language :: Python :: 3',
		'Programming Language :: Python :: 3.3',
		'Programming Language :: Python :: 3.4',
		'Programming Language :: Python :: 3.5',
		'Programming Language :: Python :: 3.6',
		'Programming Language :: Python :: Implementation :: PyPy',
		'Topic :: Software Development',
		'Topic :: Software Development :: Libraries',
		'Topic :: Software Development :: Libraries :: Python Modules',
		],
	long_description=open(join(dirname(__file__), 'README.rst')).read(),
	install_requires=['setuptools'],
	tests_require=['pytest', 'pytest-runner'],
	package_data={'': ['README.rst', 'LICENSE']},
	)
