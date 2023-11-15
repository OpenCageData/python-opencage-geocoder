# encoding: utf-8

import pytest

from opencage.geocoder import ForbiddenError, OpenCageGeocode, AioHttpError

# NOTE: Testing keys https://opencagedata.com/api#testingkeys

@pytest.mark.asyncio
async def test_success():
    async with OpenCageGeocode('6d0e711d72d74daeb2b0bfd2a5cdfdba') as geocoder:
        results = await geocoder.geocode_async("EC1M 5RF")
        assert any(
            abs(result['geometry']['lat'] - 51.952659 < 0.05 and
            abs(result['geometry']['lng'] - 7.632473) < 0.05)
            for result in results
        )

@pytest.mark.asyncio
async def test_failure():
    async with OpenCageGeocode('6c79ee8e1ca44ad58ad1fc493ba9542f') as geocoder:
        with pytest.raises(ForbiddenError) as excinfo:
            await geocoder.geocode_async("Atlantis")

        assert str(excinfo.value) == 'Your API key has been blocked or suspended.'

@pytest.mark.asyncio
async def test_without_async_session():
    geocoder = OpenCageGeocode('4372eff77b8343cebfc843eb4da4ddc4')

    with pytest.raises(AioHttpError) as excinfo:
        await geocoder.geocode_async("Atlantis")

    assert str(excinfo.value) == 'Async methods must be used inside an async context.'

@pytest.mark.asyncio
async def test_using_non_async_method():
    async with OpenCageGeocode('6d0e711d72d74daeb2b0bfd2a5cdfdba') as geocoder:
        with pytest.raises(AioHttpError) as excinfo:
            await geocoder.geocode("Atlantis")

    assert str(excinfo.value) == 'Cannot use `geocode` in an async context, use `geocode_async`.'
