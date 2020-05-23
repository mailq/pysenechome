#!/usr/bin/env python
"""Basic usage example and testing of pysenechome."""
import argparse
import asyncio
import logging
import signal
import sys

import aiohttp

import pysenechome

# This module will work with Python 3.5+
# Python 3.4+ "@asyncio.coroutine" decorator
# Python 3.5+ uses "async def f()" syntax

_LOGGER = logging.getLogger(__name__)

VAR = {}

def print_table(sensors):
    print()
    for sen in sensors:
        if sen.value is None:
            print("{:>30}".format(sen.name))
        else:
            print("{:>30}{:>15} {}".format(sen.name, str(sen.value), sen.unit))

async def main_loop(loop, ip):  # pylint: disable=invalid-name
    """Main loop."""
    async with aiohttp.ClientSession(loop=loop) as session:
        VAR["senec"] = pysenechome.SENEC(session, ip)
        VAR["running"] = True
        cnt = 5
        while VAR.get("running"):
            sensors = await VAR["senec"].read()
            print_table(sensors)
            cnt -= 1
            if cnt == 0:
                break
            await asyncio.sleep(1)

def main():
    """Main example."""
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    parser = argparse.ArgumentParser(description="Test the SENEC web API library.")
    parser.add_argument("ip", type=str, help="IP address of the battery system")

    args = parser.parse_args()

    loop = asyncio.get_event_loop()

    def _shutdown(*_):
        VAR["running"] = False
        # asyncio.ensure_future(senec.close_session(), loop=loop)

    signal.signal(signal.SIGINT, _shutdown)
    # loop.add_signal_handler(signal.SIGINT, shutdown)
    # signal.signal(signal.SIGINT, signal.SIG_DFL)
    loop.run_until_complete(
        main_loop(loop, ip=args.ip)
    )


if __name__ == "__main__":
    main()
