#!/usr/bin/env python3

# Example script we used between 2021 and 2023. It's now being replaced by
# the much more powerful CLI tool (see README.md file).
#
# Git version history will show how we kept adding features. Below is a
# version with less features, on purpose, for better readability.
#
# Background tutorial on async programming with Python
# https://realpython.com/async-io-python/
#
# Requires Python 3.7 or newer. Tested with 3.8 and 3.9.
#
# Installation:
# pip3 install opencage
#

import sys
import csv
import asyncio
from opencage.geocoder import OpenCageGeocode

API_KEY = ''
INFILE = 'file_to_geocode.csv'
OUTFILE = 'file_geocoded.csv'
MAX_ITEMS = 100        # Set to 0 for unlimited
NUM_WORKERS = 3        # For 10 requests per second try 2-5

csv_writer = csv.writer(open(OUTFILE, 'w', encoding='utf8', newline=''))

async def write_one_geocoding_result(geocoding_result, address, address_id):
    if geocoding_result is not None:
        geocoding_result = geocoding_result[0]
        row = [
            address_id,
            geocoding_result['geometry']['lat'],
            geocoding_result['geometry']['lng'],
            # Any of these components might be empty :
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
            -1, # confidence values are 1-10 (lowest to highest), use -1 for unknown
            ''
        ]
        sys.stderr.write(f"not found, writing empty result: ${address}\n")
    csv_writer.writerow(row)


async def geocode_one_address(address, address_id):
    async with OpenCageGeocode(API_KEY) as geocoder:
        geocoding_result = await geocoder.geocode_async(address)
        try:
            await write_one_geocoding_result(geocoding_result, address, address_id)
        except Exception as e:
            sys.stderr.write(e)



async def run_worker(worker_name, queue):
    sys.stderr.write(f"Worker ${worker_name} starts...\n")
    while True:
        work_item = await queue.get()
        address_id = work_item['id']
        address = work_item['address']
        await geocode_one_address(address, address_id)
        queue.task_done()




async def main():
    assert sys.version_info >= (3, 7), "Script requires Python 3.7+."

    ## 1. Read CSV into a Queue
    ##    Each work_item is an address and id. The id will be part of the output,
    ##    easy to add more settings. Named 'work_item' to avoid the words
    ##    'address' or 'task' which are used elsewhere
    ##
    ## https://docs.python.org/3/library/asyncio-queue.html
    ##
    queue = asyncio.Queue(maxsize=MAX_ITEMS)

    csv_reader = csv.reader(open(INFILE, 'r', encoding='utf8'))

    for row in csv_reader:
        work_item = {'id': row[0], 'address': row[1]}
        await queue.put(work_item)
        if queue.full():
            break

    sys.stderr.write(f"${queue.qsize()} work_items in queue\n")


    ## 2. Create tasks workers. That is coroutines, each taks take work_items
    ##    from the queue until it's empty. Tasks run in parallel
    ##
    ## https://docs.python.org/3/library/asyncio-task.html#creating-tasks
    ## https://docs.python.org/3/library/asyncio-task.html#coroutine
    ##
    sys.stderr.write(f"Creating ${NUM_WORKERS} task workers...\n")
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

    sys.stderr.write("All done.\n")


asyncio.run(main())
