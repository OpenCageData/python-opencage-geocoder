from opencage.geocoder import floatify_latlng

def test_string():
    assert floatify_latlng("123") == "123"

def test_empty_dict():
    assert floatify_latlng({}) == {}

def test_empty_list():
    assert floatify_latlng([]) == []

def test_dict_with_floats():
    assert floatify_latlng({'geom': {'lat': 12.01, 'lng': -0.9}}) == {'geom': {'lat': 12.01, 'lng': -0.9}}

def dict_with_stringified_floats():
    assert floatify_latlng({'geom': {'lat': "12.01", 'lng': "-0.9"}}) == {'geom': {'lat': 12.01, 'lng': -0.9}}

def dict_with_list():
    assert floatify_latlng(
        {'results': [{'geom': {'lat': "12.01", 'lng': "-0.9"}}, {'geometry': {'lat': '0.1', 'lng': '10'}}]}
        ) == {'results': [{'geom': {'lat': 12.01, 'lng': -0.9}}, {'geometry': {'lat': 0.1, 'lng': 10}}]}

def list_with_things():
    assert floatify_latlng([{'foo': 'bar'}]) == [{'foo': 'bar'}]
