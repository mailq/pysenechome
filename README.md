pysenechome library
===================

SENEC Webconnect library for Python 3. The library was originally created
to integrate a SENEC.Home Hybrid battery with HomeAssistant

See <https://senec.com> for more information about the SENEC home
battery storage solutions.

Currently tested on SENEC.Home V3 hybrid, but should work for the whole product line.
If you can access your SENEC via your browser, this might work for you.

Example usage
=============

See [example.py](./example.py) for a basic usage and tests

HomeAssistant
=============

The HomeAssistant SENEC sensor documentation can be found
[here](https://www.home-assistant.io/components/senec)

Daily or monthly usage is not available from the API.
It is possible to get around this by using an additional
[utility meter](https://www.home-assistant.io/components/utility_meter)
