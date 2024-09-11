import pathlib
import pytest
from opencage.version import __version__

from opencage.command_line import parse_args

@pytest.fixture(autouse=True)
def around():
    yield
    try:
        pathlib.Path("test/fixtures/output.csv").unlink()
    except FileNotFoundError:
        pass

def assert_parse_args_error(args, message, capfd):
    with pytest.raises(SystemExit):
        parse_args(args)

    _, err = capfd.readouterr()
    assert message in err

def test_required_arguments(capfd):
    assert_parse_args_error(
        [],
        'To display help use',
        capfd
    )

def test_invalid_command(capfd):
    assert_parse_args_error(
        [
            "singasong"
        ],
        'argument command: invalid choice',
        capfd
    )

def test_version_number(capfd):
    with pytest.raises(SystemExit):
        parse_args(['--version'])
    out, _ = capfd.readouterr()

    assert __version__ in out

def test_invalid_api_key(capfd):
    assert_parse_args_error(
        [
            "forward",
            "--api-key", "invalid",
            "--input", "test/fixtures/input.txt",
            "--output", "test/fixtures/output.csv"
        ],
        'invalid API key',
        capfd
    )

def test_existing_output_file(capfd):
    assert_parse_args_error(
        [
            "forward",
            "--api-key", "oc_gc_12345678901234567890123456789012",
            "--input", "test/fixtures/input.txt",
            "--output", "test/fixtures/input.txt"
        ],
        'already exists',
        capfd
    )

def test_argument_range(capfd):
    assert_parse_args_error(
        [
            "forward",
            "--api-key", "oc_gc_12345678901234567890123456789012",
            "--input", "test/fixtures/input.txt",
            "--output", "test/fixtures/output.csv",
            "--workers", "200"
        ],
        'must be within [1, 20]',
        capfd
    )

def test_zero_based_list(capfd):
    assert_parse_args_error(
        [
            "forward",
            "--api-key", "oc_gc_12345678901234567890123456789012",
            "--input", "test/fixtures/input.txt",
            "--output", "test/fixtures/output.csv",
            "--input-columns", "0,1,2"
        ],
        'The lowest possible number is 1',
        capfd
    )


def test_full_argument_list():
    args = parse_args([
        "reverse",
        "--api-key", "oc_gc_12345678901234567890123456789012",
        "--input", "test/fixtures/input.txt",
        "--output", "test/fixtures/output.csv",
        "--headers",
        "--input-columns", "1,2",
        "--add-columns", "city,postcode",
        "--limit", "4",
        "--workers", "3",
        "--timeout", "2",
        "--retries", "1",
        "--dry-run",
        "--unordered",
        "--api-domain", "bulk.opencagedata.com",
        "--optional-api-params", "extra=1",
        "--no-progress",
        "--quiet"
    ])

    assert args.command == "reverse"
    assert args.api_key == "oc_gc_12345678901234567890123456789012"
    assert args.input.name == "test/fixtures/input.txt"
    assert args.output == "test/fixtures/output.csv"
    assert args.headers is True
    assert args.input_columns == [1, 2]
    assert args.add_columns == ["city", "postcode"]
    assert args.limit == 4
    assert args.workers == 3
    assert args.timeout == 2
    assert args.retries == 1
    assert args.dry_run is True
    assert args.unordered is True
    assert args.api_domain == "bulk.opencagedata.com"
    assert args.optional_api_params == { "extra": "1" }
    assert args.no_progress is True
    assert args.quiet is True

def test_defaults():
    args = parse_args([
        "forward",
        "--api-key", "12345678901234567890123456789012",
        "--input", "test/fixtures/input.txt",
        "--output", "test/fixtures/output.csv"
    ])

    assert args.command == "forward"
    assert args.limit == 0
    assert args.headers is False
    assert args.input_columns == [1]
    assert args.add_columns == ["lat", "lng", "_type", "_category", "country_code", "country", "state",
        "county", "_normalized_city", "postcode", "road", "house_number", "confidence", "formatted"]
    assert args.workers == 1
    assert args.timeout == 10
    assert args.retries == 10
    assert args.dry_run is False
    assert args.unordered is False
    assert args.api_domain == "api.opencagedata.com"
    assert args.optional_api_params == {}
    assert args.no_progress is False
    assert args.quiet is False
