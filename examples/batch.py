#!/usr/bin/env python3

# Background tutorial on async programming with Python
# https://realpython.com/async-io-python/

# Requires Python 3.7 or newer. Tested with 3.8 and 3.9.

# Installation:
# pip3 install --upgrade opencage asyncio aiohttp backoff tqdm

import sys
import csv
import asyncio
import traceback
import backoff
from tqdm import tqdm
from opencage.geocoder import OpenCageGeocode, AioHttpError

API_KEY = ''
FILENAME_INPUT_CSV = 'file_to_geocode.csv'
FILENAME_OUTPUT_CSV = 'file_geocoded.csv'

MAX_ITEMS = 100              # Howy man lines to read from the input file. Set to 0 for unlimited
NUM_WORKERS = 3              # For 10 requests per second try 2-5
REQUEST_TIMEOUT_SECONDS = 5  # For individual HTTP requests. Fefault is 1
RETRY_MAX_TRIES = 10         # How often to retry if a HTTP request times out
RETRY_MAX_TIME = 60          # Limit in seconds for retries
SHOW_PROGRESS = True         # Show progress bar

csv_writer = csv.writer(open(FILENAME_OUTPUT_CSV, 'w', encoding='utf8', newline=''))

PROGRESS_BAR = SHOW_PROGRESS and tqdm(total=0, position=0, desc="Addresses geocoded", dynamic_ncols=True)

async def write_one_geocoding_result(geocoding_results, address, address_id):
    if geocoding_results is not None and len(geocoding_results):
        first_result = geocoding_results[0]
        row = [
            address_id,
            first_result['geometry']['lat'],
            first_result['geometry']['lng'],
            # Any of the components might be empty:
            first_result['components'].get('_type', ''),
            first_result['components'].get('country', ''),
            first_result['components'].get('county', ''),
            first_result['components'].get('city', ''),
            first_result['components'].get('postcode', ''),
            first_result['components'].get('road', ''),
            first_result['components'].get('house_number', ''),
            first_result['confidence'],
            first_result['formatted']
        ]

    else:
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
        sys.stderr.write(f"not found, writing empty result: {address}\n")
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
    async with OpenCageGeocode(API_KEY) as geocoder:
        # address -> coordinates
        # note: you may also want to set other optional parameters like
        # countrycode, language, etc
        # see the full list: https://opencagedata.com/api#forward-opt
        try:
            geocoding_results = await geocoder.geocode_async(address, no_annotations=1)
        except Exception as exc:
            geocoding_results = None
            traceback.print_exception(exc, file=sys.stderr)

        # coordinates -> address, e.g. '40.78,-73.97' => 101, West 91st Street, New York
        # lon_lat = address.split(',')
        # geocoding_result = await geocoder.reverse_geocode_async(lon_lat[0], lon_lat[1], no_annotations=1)
        # returns a single result so we convert it to a list
        # geocoding_results = [geocoding_result]

        try:
            await write_one_geocoding_result(geocoding_results, address, address_id)
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
    assert sys.version_info >= (3, 7), "Script requires Python 3.7+."

    ## 1. Read CSV into a Queue
    ##    Each work_item is an address and id. The id will be part of the output,
    ##    easy to add more settings. Named 'work_item' to avoid the words
    ##    'address' or 'task' which are used elsewhere
    ##
    ## https://docs.python.org/3/library/asyncio-queue.html
    ##
    queue = asyncio.Queue(maxsize=MAX_ITEMS)

    csv_reader = csv.reader(open(FILENAME_INPUT_CSV, 'r'), strict=True, skipinitialspace=True)

    for row in csv_reader:
        if len(row) == 0:
            raise Exception(f"Empty line in input file at line number {csv_reader.line_num}, aborting")

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
