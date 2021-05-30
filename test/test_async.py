# encoding: utf-8

import pytest

from opencage.geocoder import OpenCageGeocode, AioHttpError

# async def test_success():
#     async with OpenCageGeocode('abc123') as geocoder:
#         results = await geocoder.geocode_async("EC1M 5RF")
#         assert any((abs(result['geometry']['lat'] - 51.5201666) < 0.05 and abs(result['geometry']['lng'] - -0.0985142) < 0.05) for result in results)

async def test_without_session():
    geocoder = OpenCageGeocode('abc123')

    with pytest.raises(AioHttpError) as excinfo:
        await geocoder.geocode_async("whatever")

    assert str(excinfo.value) == 'Async methods must be used inside an async context.'
