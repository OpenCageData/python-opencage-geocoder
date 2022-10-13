#/usr/bin/env python

import os
import sys
from setuptools import setup, find_packages

# if you are not using vagrant, just delete os.link directly,
# The hard link only saves a little disk space, so you should not care
if os.environ.get('USER', '') == 'vagrant':
    del os.link


ROOT_DIR = os.path.dirname(__file__)
SOURCE_DIR = os.path.join(ROOT_DIR)

if sys.version_info < (3, 5):
    raise RuntimeError(
        "opencage requires Python 3.6 or newer"
        "Use older opencage 1.x for Python 2.7 or 3.5"
    )

# try for travis
try:
    with open(os.path.join(SOURCE_DIR, 'README.md')) as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = ""

setup(
    name="opencage",
    version="2.1.0",
    description="Wrapper module for the OpenCage Geocoder API",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author="OpenCage GmbH",
    author_email="info@opencagedata.com",
    url="https://github.com/OpenCageData/python-opencage-geocoder/",
    download_url="https://github.com/OpenCageData/python-opencage-geocoder/tarball/2.1.0",
    license="BSD",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    keywords=['geocoding', 'geocoder'],
    classifiers=[
        'Environment :: Web Environment',
        "Development Status :: 5 - Production/Stable",
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        "Programming Language :: Python :: 3 :: Only",
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Scientific/Engineering :: GIS',
        'Topic :: Utilities'
    ],
    install_requires=[
        'Requests>=2.2.0',
        'pyopenssl>=0.15.1',
        'backoff>=1.10.0'
    ],
    test_suite='tests',
    tests_require=[
        'httpretty>=0.9.6',
        'pylint==2.9.1',
        'pytest>=6.0'
    ],
)
