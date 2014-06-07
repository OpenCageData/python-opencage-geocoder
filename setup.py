#/usr/bin/env python

from setuptools import setup, find_packages
import os

ROOT_DIR = os.path.dirname(__file__)
SOURCE_DIR = os.path.join(ROOT_DIR)

setup(
	name="opencage",
	version="1.0.0",
	description="Simple wrapper module for the OpenCage Geocoder API",
	author="OpenCage (a Lokku brand)",
	author_email="info@opencagedata.com",
	url="",
	license="BSD",
	packages=find_packages(),
	include_package_data=True,
	zip_safe=False,
	classifiers=[
		'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities'],
    install_requires=[
        'Requests>=2.2.0'
        'six',
    ],
    test_suite='tests',
    tests_require=[
        'httpretty',
        'six',
    ],
)
