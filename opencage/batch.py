import sys
import ssl
import asyncio
import traceback
import threading
import random

from contextlib import suppress
from urllib.parse import urlencode
from tqdm import tqdm
import certifi
import backoff
from opencage.geocoder import OpenCageGeocode, OpenCageGeocodeError, _query_for_reverse_geocoding

class OpenCageBatchGeocoder():

    """ Called from command_line.py
        init() receives the parsed command line parameters
        geocode() receive an input and output CSV reader/writer and loops over the data
    """

    def __init__(self, options):
        self.options = options
        self.sslcontext = ssl.create_default_context(cafile=certifi.where())
        self.user_agent_comment = 'OpenCage CLI'
        self.write_counter = 1

    def __call__(self, *args, **kwargs):
        asyncio.run(self.geocode(*args, **kwargs))

    async def geocode(self, csv_input, csv_output):
        if not self.options.dry_run:
            test = await self.test_request()
            if test['error']:
                self.log(test['error'])
                return
            if test['free'] is True and self.options.workers > 1:
                sys.stderr.write(f"Free trial account detected. Resetting number of workers to 1.\n")
                self.options.workers = 1

        if self.options.headers:
            header_columns = next(csv_input, None)
            if header_columns is None:
                return

        queue = asyncio.Queue(maxsize=self.options.limit)

        read_warnings = await self.read_input(csv_input, queue)

        if self.options.dry_run:
            if not read_warnings:
                print('All good.')
            return

        if self.options.headers:
            csv_output.writerow(header_columns + self.options.add_columns)

        progress_bar = not (self.options.no_progress or self.options.quiet) and \
            tqdm(total=queue.qsize(), position=0, desc="Addresses geocoded", dynamic_ncols=True)

        tasks = []
        for _ in range(self.options.workers):
            task = asyncio.create_task(self.worker(csv_output, queue, progress_bar))
            tasks.append(task)

        # This starts the workers and waits until all are finished
        await queue.join()

        # All tasks done
        for task in tasks:
            task.cancel()

        if progress_bar:
            progress_bar.close()

    async def test_request(self):
        try:
            async with OpenCageGeocode(self.options.api_key, domain=self.options.api_domain, sslcontext=self.sslcontext, user_agent_comment=self.user_agent_comment) as geocoder:
                result = await geocoder.geocode_async('Kendall Sq, Cambridge, MA', raw_response=True)

                free = False
                with suppress(KeyError):
                    free = result['rate']['limit'] == 2500

                return { 'error': None, 'free': free }
        except Exception as exc:
            return { 'error': exc }

    async def read_input(self, csv_input, queue):
        any_warnings = False
        for index, row in enumerate(csv_input):
            line_number = index + 1

            if len(row) == 0:
                self.log(f"Line {line_number} - Empty line")
                any_warnings = True
                row = ['']

            item = await self.read_one_line(row, line_number)
            if item['warnings'] is True:
                any_warnings = True
            await queue.put(item)

            if queue.full():
                break

        return any_warnings

    async def read_one_line(self, row, row_id):
        warnings = False

        if self.options.command == 'reverse':
            input_columns = [1, 2]
        elif self.options.input_columns:
            input_columns = self.options.input_columns
        else:
            input_columns = None

        if input_columns:
            address = []
            try:
                for column in input_columns:
                    # input_columns option uses 1-based indexing
                    address.append(row[column - 1])
            except IndexError:
                self.log(f"Line {row_id} - Missing input column {column} in {row}")
                warnings = True
        else:
            address = row

        if self.options.command == 'reverse':

            if len(address) != 2:
                self.log(f"Line {row_id} - Expected two comma-separated values for reverse geocoding, got {address}")
            else:
                # _query_for_reverse_geocoding attempts to convert into numbers. We rather have it fail
                # now than during the actual geocoding
                try:
                    _query_for_reverse_geocoding(address[0], address[1])
                except:
                    self.log(f"Line {row_id} - Does not look like latitude and longitude: '{address[0]}' and '{address[1]}'")
                    warnings = True
                    address = []

        return { 'row_id': row_id, 'address': ','.join(address), 'original_columns': row, 'warnings': warnings }

    async def worker(self, csv_output, queue, progress):
        while True:
            item = await queue.get()

            try:
                await self.geocode_one_address(csv_output, item['row_id'], item['address'], item['original_columns'])

                if progress:
                    progress.update(1)
            except Exception as exc:
                traceback.print_exception(exc, file=sys.stderr)
            finally:
                queue.task_done()

    async def geocode_one_address(self, csv_output, row_id, address, original_columns):
        def on_backoff(details):
            if not self.options.quiet:
                sys.stderr.write("Backing off {wait:0.1f} seconds afters {tries} tries "
                    "calling function {target} with args {args} and kwargs "
                    "{kwargs}\n".format(**details))

        @backoff.on_exception(backoff.expo,
                              asyncio.TimeoutError,
                              max_time=self.options.timeout,
                              max_tries=self.options.retries,
                              on_backoff=on_backoff)
        async def _geocode_one_address():
            async with OpenCageGeocode(self.options.api_key, domain=self.options.api_domain, sslcontext=self.sslcontext, user_agent_comment=self.user_agent_comment) as geocoder:
                geocoding_results = None
                params = { 'no_annotations': 1, **self.options.optional_api_params }

                try:
                    if self.options.command == 'reverse':
                        if ',' in address:
                            lon, lat = address.split(',')
                            geocoding_results = await geocoder.reverse_geocode_async(lon, lat, **params)
                    else:
                        geocoding_results = await geocoder.geocode_async(address, **params)
                except OpenCageGeocodeError as exc:
                    self.log(str(exc))
                except Exception as exc:
                    traceback.print_exception(exc, file=sys.stderr)

                try:
                    if geocoding_results is not None and len(geocoding_results):
                        geocoding_result = geocoding_results[0]
                    else:
                        geocoding_result = None

                    if self.options.verbose:
                        self.log({
                            'row_id': row_id,
                            'thread_id': threading.get_native_id(),
                            'request': geocoder.url + '?' + urlencode(geocoder._parse_request(address, params)),
                            'response': geocoding_result
                        })

                    await self.write_one_geocoding_result(csv_output, row_id, geocoding_result, original_columns)
                except Exception as exc:
                    traceback.print_exception(exc, file=sys.stderr)

        await _geocode_one_address()

    async def write_one_geocoding_result(self, csv_output, row_id, geocoding_result, original_columns):
        row = original_columns

        for column in self.options.add_columns:
            if geocoding_result is None:
                row.append('')
            elif column in geocoding_result:
                row.append(self.deep_get_result_value(geocoding_result, [column], ''))
            elif column in geocoding_result['components']:
                row.append(self.deep_get_result_value(geocoding_result, ['components', column], ''))
            elif column in geocoding_result['geometry']:
                row.append(self.deep_get_result_value(geocoding_result, ['geometry', column], ''))
            elif column == 'FIPS':
                row.append(self.deep_get_result_value(geocoding_result, ['annotations', 'FIPS', 'county'], ''))
            else:
                row.append('')

        # Enforce that row are written ordered. That means we might wait for other threads
        # to finish a task and make the overall process slower. Alternative would be to
        # use a second queue, or keep some results in memory.
        if not self.options.unordered:
            while row_id > self.write_counter:
                if self.options.verbose:
                    self.log(f"Want to write row {row_id}, but write_counter is at {self.write_counter}")
                await asyncio.sleep(random.uniform(0.01, 0.1))

            if self.options.verbose:
                self.log(f"Writing row {row_id}")
        csv_output.writerow(row)
        self.write_counter = self.write_counter + 1

    def log(self, message):
        if not self.options.quiet:
            sys.stderr.write(f"{message}\n")

    def deep_get_result_value(self, data, keys, default=None):
        for key in keys:
            if isinstance(data, dict):
                data = data.get(key, default)
            else:
                return default
        return data
