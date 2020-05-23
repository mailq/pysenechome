"""SENEC web API library for Python.

See: http://your-senec.local/lala.cgi
This module was created by reverse engineering the web interface.
The source code is heavily based (copied and adapted) from
https://github.com/kellerza/pysma

Source: http://www.github.com/mailq/pysenechome
"""
import asyncio
import json
import logging

import async_timeout
import attr

from .converter import *
from aiohttp import client_exceptions

_LOGGER = logging.getLogger(__name__)

@attr.s(slots=True)
class Sensor(object):
    """pysenechome sensor definition."""

    key = attr.ib()
    name = attr.ib()
    unit = attr.ib()
    func = attr.ib(default=None)
    value = attr.ib(default=None, init=False)

    def __attrs_post_init__(self):
        """Init path."""
        key = str(self.key)
        self.key = key

    def extract_value(self, result_body):
        """Extract value from json body."""
        try:
            res = result_body[self.key]
        except (KeyError, TypeError):
            _LOGGER.warning("Sensor %s: Not found in %s", self.key, result_body)
            res = self.value
            self.value = None
            return self.value != res

        res = toValue(res)
        # If there is a converter function then transform the value accodingly
        if (self.func != None):
            res = self.func(res)
        self.value = res
        return res != self.value

class SensorGroups(object):
    """SENEC sensor group."""

    def __init__(self, add_default_sensors=True):
        self.__s = {}
        if add_default_sensors:
            group = Sensors()
            group.add(Sensor("GUI_HOUSE_POW", "house_power", "W"))
            group.add(Sensor("GUI_INVERTER_POWER", "pv_power", "W"))
            group.add(Sensor("GUI_BAT_DATA_POWER", "battery_power", "W"))
            group.add(Sensor("GUI_BAT_DATA_VOLTAGE", "battery_voltage", "V"))
            group.add(Sensor("GUI_BAT_DATA_CURRENT", "battery_current", "A"))
            group.add(Sensor("GUI_BAT_DATA_FUEL_CHARGE", "battery_level", "%"))
            group.add(Sensor("GUI_CHARGING_INFO", "charging", "", toBoolean))
            group.add(Sensor("GUI_BAT_DATA_OA_CHARGING", "battery_total_yield", "kWh"))
            group.add(Sensor("STAT_MAINT_REQUIRED", "maintenance", "", toBoolean))
            group.add(Sensor("STAT_HOURS_OF_OPERATION", "hours_of_operation", "h"))
            group.add(Sensor("STAT_STATE", "state", "", toState))
            self.add("ENERGY", group)
            group = Sensors()
            group.add(Sensor("CAR", "can_charge_car", "", toBoolean))
            group.add(Sensor("CLOUDREADY", "can_use_cloud", "", toBoolean))
            group.add(Sensor("ECOGRIDREADY", "can_use_ecogrid", "", toBoolean))
            group.add(Sensor("HEAT", "can_use_heater_rod", "", toBoolean))
            group.add(Sensor("ISLAND", "can_be_off_grid", "", toBoolean))
            group.add(Sensor("ISLAND_PRO", "can_be_off_grid_professional", "", toBoolean))
            self.add("FEATURES", group)
            group = Sensors()
            group.add(Sensor("U_AC", "grid_voltage_p", "V"))
            group.add(Sensor("I_AC", "grid_current_p", "A"))
            group.add(Sensor("P_AC", "grid_power_p", "W"))
            group.add(Sensor("P_TOTAL", "grid_power", "W"))
            group.add(Sensor("FREQ", "frequency", "Hz"))
            self.add("PM1OBJ1", group)
            group = Sensors()
            group.add(Sensor("MPP_INT", "mpp_tracker_", "W"))
            group.add(Sensor("POWER_RATIO", "pv_limit", "%"))
            self.add("PV1", group)
            group = Sensors()
            group.add(Sensor("CYCLES", "battery_cycles_", ""))
            group.add(Sensor("SOC", "battery_state_of_charge_", "%"))
            group.add(Sensor("SOH", "battery_state_of_health_", "%"))
            self.add("BMS", group)

    def __len__(self):
        """Length."""
        return len(self.__s)

    def __contains__(self, key):
        """Get a sensor using either the name or key."""
        try:
            if self[key]:
                return True
        except KeyError:
            return False

    def __getitem__(self, key):
        """Get sensors using the key."""
        return self.__s.get(key)

    def items(self):
        """Iterator."""
        return self.__s.items()

    def values(self):
        """Values."""
        return self.__s.values()

    def add(self, key, sensors):
        """Add a sensor, warning if it exists."""
        if not isinstance(sensors, Sensors):
            raise TypeError("pysenechome.Sensors expected")

        if key in self:
            old = self[key]
            self.__s.remove(old)
            _LOGGER.warning("Replacing sensors %s with %s", old, sensor)

        if key in self:
            _LOGGER.warning("Duplicate SENEC sensors key %s", key)

        self.__s[key] = sensors


class Sensors(object):
    """SENEC Sensors."""

    def __init__(self):
        self.__s = []

    def __len__(self):
        """Length."""
        return len(self.__s)

    def __contains__(self, key):
        """Get a sensor using either the name or key."""
        try:
            if self[key]:
                return True
        except KeyError:
            return False

    def __getitem__(self, key):
        """Get a sensor using either the name or key."""
        for sen in self.__s:
            if sen.name == key or sen.key == key:
                return sen
        raise KeyError(key)

    def __iter__(self):
        """Iterator."""
        return self.__s.__iter__()

    def add(self, sensor):
        """Add a sensor, warning if it exists."""
        if isinstance(sensor, (list, tuple)):
            for sss in sensor:
                self.add(sss)
            return

        if not isinstance(sensor, Sensor):
            raise TypeError("pysenechome.Sensor expected")

        if sensor.name in self:
            old = self[sensor.name]
            self.__s.remove(old)
            _LOGGER.warning("Replacing sensor %s with %s", old, sensor)

        if sensor.key in self:
            _LOGGER.warning("Duplicate SENEC sensor key %s", sensor.key)

        self.__s.append(sensor)


URL_VALUES = "/lala.cgi"

class SENEC:
    """Class to connect to the SENEC web API and read parameters."""

    def __init__(self, session, url):
        """Init SENEC connection."""
        self._url = url.rstrip("/")
        if not url.startswith("http"):
            self._url = "http://" + self._url
        self._aio_session = session
        self._sensor_groups = SensorGroups()

    async def _fetch_json(self, url, payload):
        """Fetch json data for requests."""
        params = {
            "data": json.dumps(payload),
            "headers": {"content-type": "application/json"}
        }
        for _ in range(3):
            try:
                with async_timeout.timeout(3):
                    async with self._aio_session.post(self._url + url, **params) as res:
                        body = await res.text()
                        return (await res.json()) or {}
            except (asyncio.TimeoutError, client_exceptions.ClientError):
                continue
        return {"err": "Could not connect to SENEC.home at {} (timeout)".format(self._url)}

    def _asRequest(self, sensors):
        """Convert a sensor group to a JSON request"""
        result = {}
        for value in sensors:
            result[value.key] = ''
        return result

    async def read(self):
        """Read a set of keys."""
        payload = {key: self._asRequest(value) for key, value in self._sensor_groups.items()}
        body = await self._fetch_json(URL_VALUES, payload=payload)

        # connection refused?
        err = body.get("err")
        if err is not None:
            _LOGGER.warning(
                "%s: error detected, connection failed? Got: %s",
                self._url,
                body,
            )
            return False

        for key, sen in self._sensor_groups.items():
            result_body = body[key]
            if key in body:
                for sensor in sen:
                    sensor.extract_value(result_body)
                    continue

        result = []
        for group in self._sensor_groups.values():
            for sen in group:
                if isinstance(sen.value, list):
                    for i, value in enumerate(sen.value):
                        sensor_dummy = Sensor(sen.key, sen.name + str(i+1), sen.unit)
                        sensor_dummy.value = value
                        result.append(sensor_dummy)
                else:
                    result.append(sen)
        return result
