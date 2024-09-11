import pathlib
import os
import pytest

from opencage.command_line import main

# NOTE: Testing keys https://opencagedata.com/api#testingkeys
TEST_APIKEY_200 = '6d0e711d72d74daeb2b0bfd2a5cdfdba' # always returns same address
TEST_APIKEY_401 = '11111111111111111111111111111111' # invalid key

@pytest.fixture(autouse=True)
def around():
    yield
    try:
        pathlib.Path("test/fixtures/cli/output.csv").unlink()
    except FileNotFoundError:
        pass

def assert_output(path, length, lines):
    assert pathlib.Path(path).exists()

    with open(path, "r", encoding="utf-8") as f:
        actual = f.readlines()
        # print(actual, file=sys.stderr)
        assert len(actual) == length

        for i, expected in enumerate(lines):
            assert actual[i].strip() == expected

def test_forward():
    main([
        "forward",
        "--api-key", TEST_APIKEY_200,
        "--input", "test/fixtures/cli/forward.csv",
        "--output", "test/fixtures/cli/output.csv",
        "--input-columns", "2,3,4",
        "--add-columns", "country_code,country,postcode,city"
    ])

    assert_output(
        path="test/fixtures/cli/output.csv",
        length=3,
        lines=['Rathausmarkt 1,Hamburg,20095,Germany,de,Germany,48153,Münster']
    )

def test_reverse():
    main([
        "reverse",
        "--api-key", TEST_APIKEY_200,
        "--input", "test/fixtures/cli/reverse.csv",
        "--output", "test/fixtures/cli/output.csv",
        "--add-columns", "country_code,country,postcode"
    ])

    assert_output(
        path="test/fixtures/cli/output.csv",
        length=1,
        lines=['51.9526622,7.6324709,de,Germany,48153']
    )

def test_headers():
    main([
        "forward",
        "--api-key", TEST_APIKEY_200,
        "--input", "test/fixtures/cli/forward_with_headers.csv",
        "--output", "test/fixtures/cli/output.csv",
        "--input-columns", "1,2,3,4",
        "--headers",
        "--add-columns", "lat,lng,postcode"
    ])

    assert_output(
        path="test/fixtures/cli/output.csv",
        length=4,
        lines=[
            'street and number,town,postcode,country,lat,lng,postcode',
            'Rathausmarkt 1,Hamburg,20095,Germany,51.9526622,7.6324709,48153'
        ]
    )

def test_input_errors(capfd):
    main([
        "reverse",
        "--api-key", TEST_APIKEY_200,
        "--input", "test/fixtures/cli/reverse_with_errors.csv",
        "--output", "test/fixtures/cli/output.csv",
        "--add-columns", "country_code,postcode",
        "--no-progress"
    ])

    _, err = capfd.readouterr()
    # assert err == ''
    assert err.count("\n") == 6
    assert "Line 1 - Missing input column 2 in ['50.101010']" in err
    assert "Line 1 - Expected two comma-separated values for reverse geocoding, got ['50.101010']" in err
    assert "Line 3 - Empty line" in err
    assert "Line 3 - Missing input column 2 in ['']" in err
    assert "Line 3 - Expected two comma-separated values for reverse geocoding, got ['']" in err
    assert "Line 4 - Does not look like latitude and longitude: 'a' and 'b'" in err

    assert_output(
        path="test/fixtures/cli/output.csv",
        length=4,
        lines=[
            '50.101010,,',
            '-100,60.1,de,48153',
            ',,',
            'a,b,,'
        ]
    )

def test_empty_result():
    # 'NOWHERE-INTERESTING' is guaranteed to return no result
    # https://opencagedata.com/api#testingkeys
    main([
        "forward",
        "--api-key", TEST_APIKEY_200,
        "--input", "test/fixtures/cli/forward_noresult.csv",
        "--output", "test/fixtures/cli/output.csv",
        "--input-columns", "2",
        "--headers",
        "--verbose",
        "--add-columns", "lat,lng,postcode"
    ])

    assert_output(
        path="test/fixtures/cli/output.csv",
        length=2,
        lines=[
            'id,full_address,lat,lng,postcode',
            '123,NOWHERE-INTERESTING,,,'
        ]
    )


def test_invalid_api_key(capfd):
    main([
        "forward",
        "--api-key", TEST_APIKEY_401,
        "--input", "test/fixtures/cli/forward_with_headers.csv",
        "--output", "test/fixtures/cli/output.csv"
    ])

    _, err = capfd.readouterr()
    assert 'Your API key is not authorized' in err

def test_dryrun(capfd):
    main([
        "forward",
        "--api-key", TEST_APIKEY_200,
        "--input", "test/fixtures/cli/forward_with_headers.csv",
        "--output", "test/fixtures/cli/output.csv",
        "--dry-run"
    ])

    assert not os.path.isfile("test/fixtures/cli/output.csv")

    out, _ = capfd.readouterr()
    assert out.count("\n") == 1
    assert "All good." in out


def test_invalid_domain(capfd):
    main([
        "forward",
        "--api-key", TEST_APIKEY_200,
        "--input", "test/fixtures/cli/forward.csv",
        "--output", "test/fixtures/cli/output.csv",
        "--api-domain", "invalid73585348.opencagedata.com"
    ])

    _, err = capfd.readouterr()
    assert 'Cannot connect to host' in err

    # with dry-run no request will be made
    main([
        "forward",
        "--api-key", TEST_APIKEY_200,
        "--input", "test/fixtures/cli/forward.csv",
        "--output", "test/fixtures/cli/output.csv",
        "--api-domain", "invalid73585348.opencagedata.com",
        "--dry-run"
    ])
    _, err = capfd.readouterr()
    assert err == ''
