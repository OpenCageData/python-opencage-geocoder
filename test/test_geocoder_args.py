# encoding: utf-8

from opencage.geocoder import OpenCageGeocode

import os


def test_protocol_http():
    """Test that HTTP protocol can be set correctly"""
    geocoder = OpenCageGeocode('abcde', protocol='http')
    assert geocoder.url == 'http://api.opencagedata.com/geocode/v1/json'


def test_api_key_env_var():
    """Test that API key can be set by an environment variable"""

    os.environ['OPENCAGE_API_KEY'] = 'from-env-var'
    geocoder = OpenCageGeocode()
    assert geocoder.key == 'from-env-var'


def test_custom_domain():
    """Test that custom domain can be set"""
    geocoder = OpenCageGeocode('abcde', domain='example.com')
    assert geocoder.url == 'https://example.com/geocode/v1/json'
