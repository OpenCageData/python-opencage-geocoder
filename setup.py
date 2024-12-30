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

if sys.version_info < (3, 8):
    raise RuntimeError(
        "opencage requires Python 3.8 or newer"
        "Use older opencage 1.x for Python 2.7 or 3.7"
    )

# try for testing
try:
    with open(os.path.join(SOURCE_DIR, 'README.md'), encoding="utf-8") as f:
        LONG_DESCRIPTION = f.read()
except FileNotFoundError:
    LONG_DESCRIPTION = ""

setup(
    name="opencage",
    version="3.0.4",
    description="Wrapper module for the OpenCage Geocoder API",
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author="OpenCage GmbH",
    author_email="info@opencagedata.com",
    url="https://github.com/OpenCageData/python-opencage-geocoder/",
    download_url="https://github.com/OpenCageData/python-opencage-geocoder/tarball/3.0.4",
    license="BSD",
    entry_points={
        'console_scripts': [
            'opencage=opencage.command_line:main'
        ]
    },
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
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Topic :: Scientific/Engineering :: GIS',
        'Topic :: Utilities'
    ],
    install_requires=[
        'Requests>=2.31.0',
        'backoff>=2.2.1',
        'tqdm>=4.66.4',
        'certifi>=2024.07.04',
        'aiohttp>=3.10.5'
    ],
    test_suite='pytest',
    tests_require=[
        'httpretty>=1.1.4',
        'pylint==2.17.4',
        'pytest>=7.4.0'
    ],
)
