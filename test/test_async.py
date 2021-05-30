# encoding: utf-8

# from pathlib import Path

# import httpretty

# from httpretty import httprettified
from opencage.geocoder import OpenCageGeocode


# @httprettified
async def test_success():
    async with OpenCageGeocode('ba12d829b226403f9635c4d64cbca4c1') as geocoder:
        # httpretty.register_uri(
        #     httpretty.GET,
        #     geocoder.url,
        #     body=Path('test/fixtures/uk_postcode.json').read_text()
        # )

        results = await geocoder.geocode_async("EC1M 5RF")
        assert any((abs(result['geometry']['lat'] - 51.5201666) < 0.05 and abs(result['geometry']['lng'] - -0.0985142) < 0.05) for result in results)

# test AioHttpError