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
    geocoder = OpenCageGeocode('abcde', domain='api2.opencagedata.com')
    assert geocoder.url == 'https://api2.opencagedata.com/geocode/v1/json'


def test_custom_domain_localhost():
    """Test that localhost domain can be set"""
    geocoder = OpenCageGeocode('abcde', domain='localhost:8080')
    assert geocoder.url == 'https://localhost:8080/geocode/v1/json'


def test_custom_domain_invalid():
    """Test that invalid domains are rejected"""
    import pytest
    with pytest.raises(ValueError, match="Invalid API domain"):
        OpenCageGeocode('abcde', domain='www.example.com')
