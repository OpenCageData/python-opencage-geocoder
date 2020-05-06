#/usr/bin/env python

import os
from setuptools import setup, find_packages

# if you are not using vagrant, just delete os.link directly,
# The hard link only saves a little disk space, so you should not care
if os.environ.get('USER', '') == 'vagrant':
    del os.link


ROOT_DIR = os.path.dirname(__file__)
SOURCE_DIR = os.path.join(ROOT_DIR)

# try for pypy
try:
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError

# try for travis
try:
    with open(os.path.join(SOURCE_DIR, 'README.md')) as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = ""

setup(
    name="opencage",
    version="1.2.1",
    description="Simple wrapper module for the OpenCage Geocoder API",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author="OpenCage Data Ltd",
    author_email="info@opencagedata.com",
    url="https://github.com/OpenCageData/python-opencage-geocoder/",
    download_url="https://github.com/OpenCageData/python-opencage-geocoder/tarball/1.2.1",
    license="BSD",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    keywords=['geocoding', 'geocoder'],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Utilities'],
    install_requires=[
        'Requests>=2.2.0',
        'six>=1.4.0',
        'pyopenssl>=0.15.1',
        'backoff>=1.10.0'
    ],
    test_suite='tests',
    tests_require=[
        'httpretty>=0.9.6',
        'six>=1.4.0',
    ],
)
