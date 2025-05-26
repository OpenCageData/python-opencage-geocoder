from opencage.batch import OpenCageBatchGeocoder

batch = OpenCageBatchGeocoder({})


def test_deep_get_result_value():
    result = {
        'annotations': {
            'FIPS': {
                'state': 'CA'
            }
        },
        'components': {
            'street': 'Main Road'
        }
    }

    assert batch.deep_get_result_value(result, ['hello', 'world']) is None

    assert batch.deep_get_result_value(result, ['components', 'street']) == 'Main Road'
    assert batch.deep_get_result_value(result, ['components', 'city']) is None
    assert batch.deep_get_result_value(result, ['components', 'city'], '') == ''

    assert batch.deep_get_result_value([], ['hello', 'world']) is None
    assert batch.deep_get_result_value(None, ['hello', 'world']) is None
