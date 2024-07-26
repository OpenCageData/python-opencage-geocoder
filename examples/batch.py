#!/usr/bin/env python3

# Background tutorial on async programming with Python
# https://realpython.com/async-io-python/

# Requires Python 3.8 or newer. Tested with 3.8/3.9/3.10/3.11.

# Installation:
# pip3 install --upgrade opencage asyncio aiohttp backoff tqdm

# Example (forward) input file:
# 1,"Via Allende 8, Cascina, Toscana, Italia"
# 2,"Via Coppi, 17, Formigine, Emilia-Romagna, Italia"
# 3,"Via Dei Salici 20, Gallarate, Lombardia, Italia"
# 4,"Via Vittorio Veneto N7, San Giuliano Terme, Toscana, Italia"
# 5,"Via Tiro A Segno 8, Gallarate, Lombardia, Italia"

# Example (reverse) input file:
# 1,"43.6783472,10.5533173"
# 2,"44.5655041,10.8412106"
# 3,"45.6823942,8.7919808"
# 4,"43.7804922,10.402925"
# 5,"45.6506236,8.8037173"
# or
# 1,43.6783472,10.5533173
# 2,44.5655041,10.8412106
# 3,45.6823942,8.7919808
# 4,43.7804922,10.402925
# 5,45.6506236,8.8037173

import os
import sys
import csv
import re
import ssl
import asyncio
import traceback
import aiohttp
import backoff
import certifi
import pkg_resources
from tqdm import tqdm
import opencage
from opencage.geocoder import OpenCageGeocode, OpenCageGeocodeError

# Use certificates from the certifi package instead of those of the operating system
# https://pypi.org/project/certifi/
# https://docs.aiohttp.org/en/stable/client_advanced.html#ssl-control-for-tcp-sockets
sslcontext = ssl.create_default_context(cafile=certifi.where())
# Alternatively set sslcontext=False to ignore certificate validation (not advised)
# or sslcontext=None to use those of the operating system



API_KEY = ''
FILENAME_INPUT_CSV = 'file_to_geocode.csv'
FILENAME_OUTPUT_CSV = 'file_geocoded.csv'
FORWARD_OR_REVERSE = 'guess' # 'forward' (address -> coordinates) or 'reverse' (coordinates -> address)
                             # With 'guess' the script checks if the address is two numbers and then
                             # assumes reverse
API_DOMAIN = 'api.opencagedata.com'
MAX_ITEMS = 100              # How many lines to read from the input file. Set to 0 for unlimited
NUM_WORKERS = 3              # For 10 requests per second try 2-5
REQUEST_TIMEOUT_SECONDS = 5  # For individual HTTP requests. Default is 1
RETRY_MAX_TRIES = 10          # How often to retry if a HTTP request times out
RETRY_MAX_TIME = 60          # Limit in seconds for retries
SHOW_PROGRESS = True         # Show progress bar





# Check OpenCage geocoder is the latest version
#
minimum_required_version = '2.3.1'
package_version = pkg_resources.get_distribution('opencage').version
if pkg_resources.parse_version(package_version) < pkg_resources.parse_version(minimum_required_version):
    sys.stderr.write(f"At least version {minimum_required_version} of opencage geocoder package required. ")
    sys.stderr.write(f"Try upgrading by running 'pip install --upgrade opencage'.\n")
    sys.exit(1)


# Check API key present
#
if len(API_KEY) < 32:
    sys.stderr.write(f"API_KEY '{API_KEY}' does not look valid.\n")
    sys.exit(1)


# Don't overwrite output file
#
if os.path.exists(FILENAME_OUTPUT_CSV):
    sys.stderr.write(f"The output file '{FILENAME_OUTPUT_CSV}' already exists.\n")
    sys.exit(1)

csv_writer = csv.writer(open(FILENAME_OUTPUT_CSV, 'w', encoding='utf8', newline=''))

PROGRESS_BAR = SHOW_PROGRESS and tqdm(total=0, position=0, desc="Addresses geocoded", dynamic_ncols=True)

# '40.78,-73.97' => true
# '3rd Ave, New York' => false
def guess_text_is_coordinate_pair(text):
    coordinate_pattern = r'^(-?\d+(\.\d+)?),(-?\d+(\.\d+)?)$'
    # x = 'yes' if bool(re.search(coordinate_pattern, text)) else 'no'
    # sys.stderr.write(f"{text} is coordinate_pair: {x}\n")
    return bool(re.search(coordinate_pattern, text))

async def write_one_geocoding_result(geocoding_result, address, address_id):
    # print(geocoding_result, file=sys.stderr)
    if geocoding_result is not None:
        row = [
            address_id,
            geocoding_result['geometry']['lat'],
            geocoding_result['geometry']['lng'],
            # Any of the components might be empty:
            geocoding_result['components'].get('_type', ''),
            geocoding_result['components'].get('country', ''),
            geocoding_result['components'].get('county', ''),
            geocoding_result['components'].get('city', ''),
            geocoding_result['components'].get('postcode', ''),
            geocoding_result['components'].get('road', ''),
            geocoding_result['components'].get('house_number', ''),
            geocoding_result['confidence'],
            geocoding_result['formatted']
        ]

    else:
        sys.stderr.write(f"not found, writing empty result: {address}\n")
        row = [
            address_id,
            0, # not to be confused with https://en.wikipedia.org/wiki/Null_Island
            0,
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            -1, # confidence values are 1-10 (lowest to highest), use -1 for unknown
            ''
        ]
    csv_writer.writerow(row)


# Backing off 0.4 seconds afters 1 tries calling function <function geocode_one_address
# at 0x10dbf5e50> with args ('14464 3RD ST # 4, 91423, CA, USA', '1780245') and kwargs {}
def backoff_hdlr(details):
    sys.stderr.write("Backing off {wait:0.1f} seconds afters {tries} tries "
                                     "calling function {target} with args {args} and kwargs "
                                     "{kwargs}\n".format(**details))

# https://pypi.org/project/backoff/
@backoff.on_exception(backoff.expo,
                                            (asyncio.TimeoutError),
                                            max_time=RETRY_MAX_TIME, # seconds
                                            max_tries=RETRY_MAX_TRIES,
                                            on_backoff=backoff_hdlr)
async def geocode_one_address(address, address_id):
    async with OpenCageGeocode(API_KEY, domain=API_DOMAIN, sslcontext=sslcontext) as geocoder:
        global FORWARD_OR_REVERSE

        geocoding_results = None
        try:
            if FORWARD_OR_REVERSE == 'reverse' or \
                (FORWARD_OR_REVERSE == 'guess' and guess_text_is_coordinate_pair(address)):
                # Reverse:
                # coordinates -> address, e.g. '40.78,-73.97' => '101, West 91st Street, New York'
                lon_lat = address.split(',')
                geocoding_results = await geocoder.reverse_geocode_async(
                                            lon_lat[0], lon_lat[1], no_annotations=1)
            else:
                # Forward:
                # address -> coordinates
                # note: you may also want to set other optional parameters like
                # countrycode, language, etc
                # see the full list: https://opencagedata.com/api#forward-opt
                geocoding_results = await geocoder.geocode_async(address, no_annotations=1)
        except OpenCageGeocodeError as exc:
            sys.stderr.write(str(exc) + "\n")
        except Exception as exc:
            traceback.print_exception(exc, file=sys.stderr)

        try:
            if geocoding_results is not None and len(geocoding_results):
                geocoding_result = geocoding_results[0]
            else:
                geocoding_result = None

            await write_one_geocoding_result(geocoding_result, address, address_id)
        except Exception as exc:
            traceback.print_exception(exc, file=sys.stderr)



async def run_worker(worker_name, queue):
    global PROGRESS_BAR
    sys.stderr.write(f"Worker {worker_name} starts...\n")

    while True:
        work_item = await queue.get()
        address_id = work_item['id']
        address = work_item['address']
        await geocode_one_address(address, address_id)

        if SHOW_PROGRESS:
            PROGRESS_BAR.update(1)

        queue.task_done()




async def main():
    global PROGRESS_BAR
    assert sys.version_info >= (3, 8), "Script requires Python 3.8 or newer"

    ## 1. Read CSV into a Queue
    ##    Each work_item is an address and id. The id will be part of the output,
    ##    easy to add more settings. Named 'work_item' to avoid the words
    ##    'address' or 'task' which are used elsewhere
    ##
    ## https://docs.python.org/3/library/asyncio-queue.html
    ##
    queue = asyncio.Queue(maxsize=MAX_ITEMS)

    with open(FILENAME_INPUT_CSV, 'r', encoding='utf-8') as infile:
        csv_reader = csv.reader(infile, strict=True, skipinitialspace=True)

        for row in csv_reader:
            if len(row) == 0:
                raise Exception(f"Empty line in input file at line number {csv_reader.line_num}, aborting")

            if FORWARD_OR_REVERSE == 'reverse' or \
                (FORWARD_OR_REVERSE == 'guess' and len(row) > 2 and \
                    guess_text_is_coordinate_pair(f"{row[1]},{row[2]}")):
                work_item = {'id': row[0], 'address': f"{row[1]},{row[2]}"}
            else:
                work_item = {'id': row[0], 'address': row[1]}

            await queue.put(work_item)
            if queue.full():
                break

    sys.stderr.write(f"{queue.qsize()} work_items in queue\n")

    if SHOW_PROGRESS:
        PROGRESS_BAR.total = queue.qsize()
        PROGRESS_BAR.refresh()

    ## 2. Create tasks workers. That is coroutines, each taks take work_items
    ##    from the queue until it's empty. Tasks run in parallel
    ##
    ## https://docs.python.org/3/library/asyncio-task.html#creating-tasks
    ## https://docs.python.org/3/library/asyncio-task.html#coroutine
    ##
    sys.stderr.write(f"Creating {NUM_WORKERS} task workers...\n")
    tasks = []
    for i in range(NUM_WORKERS):
        task = asyncio.create_task(run_worker(f'worker {i}', queue))
        tasks.append(task)


    ## 3. Now workers do the geocoding
    ##
    sys.stderr.write("Now waiting for workers to finish processing queue...\n")
    await queue.join()


    ## 4. Cleanup
    ##
    for task in tasks:
        task.cancel()

    if SHOW_PROGRESS:
        PROGRESS_BAR.close()

    sys.stderr.write("All done.\n")


asyncio.run(main())
