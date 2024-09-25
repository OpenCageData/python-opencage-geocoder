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

    assert batch.deep_get_result_value(result, ['hello', 'world']) == None

    assert batch.deep_get_result_value(result, ['components', 'street']) == 'Main Road'
    assert batch.deep_get_result_value(result, ['components', 'city']) == None
    assert batch.deep_get_result_value(result, ['components', 'city'], '') == ''

    assert batch.deep_get_result_value([], ['hello', 'world']) == None
    assert batch.deep_get_result_value(None, ['hello', 'world']) == None
