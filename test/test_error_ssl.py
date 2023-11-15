# encoding: utf-8

import ssl
import pytest
from opencage.geocoder import OpenCageGeocode, SSLError

# NOTE: Testing keys https://opencagedata.com/api#testingkeys

# Connect to a host that has an invalid certificate
@pytest.mark.asyncio
async def test_sslerror():
    bad_domain = 'wrong.host.badssl.com'
    async with OpenCageGeocode('6d0e711d72d74daeb2b0bfd2a5cdfdba', domain=bad_domain) as geocoder:
        with pytest.raises(SSLError) as excinfo:
            await geocoder.geocode_async("something")
        assert str(excinfo.value).startswith('SSL Certificate error')

# Connect to OpenCage API domain but use certificate of another domain
# This tests that sslcontext can be set.
@pytest.mark.asyncio
async def test_sslerror_wrong_certificate():
    sslcontext = ssl.create_default_context(cafile='test/fixtures/badssl-com-chain.pem')

    async with OpenCageGeocode('6d0e711d72d74daeb2b0bfd2a5cdfdba', sslcontext=sslcontext) as geocoder:
        with pytest.raises(SSLError) as excinfo:
            await geocoder.geocode_async("something")
        assert str(excinfo.value).startswith('SSL Certificate error')
