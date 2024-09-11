import argparse
import sys
import os
import io
import re
import csv

from opencage.batch import OpenCageBatchGeocoder
from opencage.version import __version__

def main(args=sys.argv[1:]):
    options = parse_args(args)

    assert sys.version_info >= (3, 8), "Script requires Python 3.8 or newer"

    geocoder = OpenCageBatchGeocoder(options)

    with options.input as input_filename:
        with (io.StringIO() if options.dry_run else open(options.output, 'x', encoding='utf-8')) as output_io:
            reader = csv.reader(input_filename, strict=True, skipinitialspace=True)
            writer = csv.writer(output_io)

            geocoder(csv_input=reader, csv_output=writer)

def parse_args(args):
    if len(args) == 0:
        print("To display help use 'opencage -h', 'opencage forward -h' or 'opencage reverse -h'", file=sys.stderr)
        sys.exit(1)

    parser = argparse.ArgumentParser(description=f'Opencage CLI {__version__}')
    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')

    subparsers = parser.add_subparsers(dest='command')
    subparsers.required = True

    subparser_forward = subparsers.add_parser('forward', help="Forward geocode a file (input is address, add coordinates)")
    subparser_reverse = subparsers.add_parser('reverse', help="Reverse geocode a file (input is coordinates, add full address)")

    for subparser in [subparser_forward, subparser_reverse]:
        subparser.add_argument("--api-key", required=True, type=api_key_type, help="Your OpenCage API key")
        subparser.add_argument("--input", required=True, type=argparse.FileType('r', encoding='utf-8'), help="Input file name", metavar='FILENAME')
        subparser.add_argument("--output", required=True, type=str, help="Output file name", metavar='FILENAME')

        add_optional_arguments(subparser)

    options = parser.parse_args(args)

    if os.path.exists(options.output) and not options.dry_run:
        if options.overwrite:
            os.remove(options.output)
        else:
            print(f"Error: The output file '{options.output}' already exists. You can add --overwrite to your command.", file=sys.stderr)
            sys.exit(1)

    if 0 in options.input_columns:
        print("Error: A column 0 in --input-columns does not exist. The lowest possible number is 1.", file=sys.stderr)
        sys.exit(1)

    return options


def add_optional_arguments(parser):
    parser.add_argument("--headers", action="store_true", help="If the first row should be treated as a header row")
    default_input_cols = '1,2' if re.match(r'.*reverse', parser.prog) else '1'
    parser.add_argument("--input-columns", type=comma_separated_type(int), default=default_input_cols, help=f"Comma-separated list of integers (default '{default_input_cols}')", metavar='')
    default_add_cols = 'lat,lng,_type,_category,country_code,country,state,county,_normalized_city,postcode,road,house_number,confidence,formatted'
    parser.add_argument("--add-columns", type=comma_separated_type(str), default=default_add_cols, help=f"Comma-separated list of output columns (default '{default_add_cols}')", metavar='')
    parser.add_argument("--workers", type=ranged_type(int, 1, 20), default=1, help="Number of parallel geocoding requests (default 1)", metavar='')
    parser.add_argument("--timeout", type=ranged_type(int, 1, 60), default=10, help="Timeout in seconds (default 10)", metavar='')
    parser.add_argument("--retries", type=ranged_type(int, 1, 60), default=10, help="Number of retries (default 5)", metavar='')
    parser.add_argument("--api-domain", type=str, default="api.opencagedata.com", help="API domain (default api.opencagedata.com)", metavar='')
    parser.add_argument("--optional-api-params", type=comma_separated_dict_type, default="", help="Extra parameters for each request (e.g. language=fr,no_dedupe=1)", metavar='')
    parser.add_argument("--limit", type=int, default=0, help="Stop after this number of lines in the input", metavar='')
    parser.add_argument("--unordered", action="store_true", help="Allow the output lines to be in different order (can be faster)")
    parser.add_argument("--dry-run", action="store_true", help="Read the input file but no geocoding")
    parser.add_argument("--no-progress", action="store_true", help="Display no progress bar")
    parser.add_argument("--quiet", action="store_true", help="No progress bar and no messages")
    parser.add_argument("--overwrite", action="store_true", help="Delete the output file first if it exists")
    parser.add_argument("--verbose", action="store_true", help="Display debug information for each request")

    return parser

def api_key_type(apikey):
    pattern = re.compile(r"^(oc_gc_)?[0-9a-f]{32}$")

    if not pattern.match(apikey):
        raise argparse.ArgumentTypeError("invalid API key")

    return apikey


def ranged_type(value_type, min_value, max_value):
    def range_checker(arg: str):
        try:
            f = value_type(arg)
        except ValueError as exc:
            raise argparse.ArgumentTypeError(f'must be a valid {value_type}') from exc
        if f < min_value or f > max_value:
            raise argparse.ArgumentTypeError(f'must be within [{min_value}, {max_value}]')
        return f

    # Return function handle to checking function
    return range_checker


def comma_separated_type(value_type):
    def comma_separated(arg: str):
        if not arg:
            return []

        return [value_type(x) for x in arg.split(',')]

    return comma_separated


def comma_separated_dict_type(arg):
    if not arg:
        return {}

    try:
        return dict([x.split('=') for x in arg.split(',')])
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be a valid comma separated list of key=value pairs") from exc
