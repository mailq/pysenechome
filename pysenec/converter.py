import struct

def toValue(input):
    if isinstance(input, list):
        return [toValue(i) for i in input]
    switcher = {
        'fl': _hexstringToFloat,
        'u8': _hexstringToInteger,
        'u3': _hexstringToInteger,
        'u1': _hexstringToInteger,
        'i3': _hexstringToInteger,
        'st': _identity,
    }
    prefix = input[:2]
    func = switcher.get(prefix, lambda: "Invalid type")
    return func(input[3:])

def _hexstringToFloat(input):
    return round(struct.unpack('!f', bytes.fromhex(input))[0],2)

def _hexstringToInteger(input):
    return int(input,16)

def _identity(input):
    return input

def toBoolean(input):
    return input == 1

def toState(input):
    switcher = {
        0: "Initial",
        1: "Communication failed with charger",
        2: "Meter error",
        3: "Shutdown by utility",
        4: "First charge",
        5: "Maintenance charge",
        6: "Maintenance charge finished",
        7: "Maintenance required",
        8: "Manual security charge",
        9: "Manual security charge finished",
        10: "Complete charge",
        11: "Balancing: charging",
        12: "Sulfate: charging",
        13: "Battery full",
        14: "Charging",
        15: "Battery empty",
        16: "Discharging",
        17: "PV and discharging",
        18: "Grid and discharging",
        19: "Passive",
        20: "Off",
        21: "Own consumption",
        22: "Restart",
        23: "Manual balancing: charging",
        24: "Manual sulfate: charging",
        25: "Security charge",
        26: "Battery protection mode",
        27: "EG error",
        28: "EG charging",
        29: "EG discharging",
        30: "EG passive",
        31: "EG charging denied",
        32: "EG discharging denied",
        33: "Emergency charge",
        34: "Software update",
        35: "Error home power",
        36: "Error grid connection",
        37: "Error hardware",
        38: "No connection to Senec",
        39: "Error BMS",
        40: "Maintenance: filter",
        41: "Sleep mode",
        42: "Waiting for surplus",
        43: "Capacity test: charging",
        44: "Capacity test: discharging",
        45: "Manual sulfate: waiting",
        46: "Manual sulfate: finished",
        47: "Manual sulfate: error",
        48: "Balancing: waiting",
        49: "Emergency charge: error",
        50: "Manual balancing: waiting",
        51: "Manual balancing: error",
        52: "Manual balancing: finished",
        53: "Automatic balancing: waiting",
        54: "Finalizing charging",
        55: "Battery disconnector off",
        56: "Peak shaving: waiting",
        57: "Error charger",
        58: "Error network processing unit",
        59: "BMS offline",
        60: "Maintenance: error",
        61: "Manual security charge: error",
        62: "Security charge: error",
        63: "No master connection",
        64: "Lithium security mode on",
        65: "Lithium security mode off",
        66: "Error battery current",
        67: "BMS DC off",
        68: "Initializing grid",
        69: "Stabilizing grid",
        70: "Remote shutdown",
        71: "Off peak charging",
        72: "Error half bridge",
        73: "Error BMS temperature",
        74: "Factory settings not found",
        75: "Off grid mode",
        76: "Off grid mode: battery empty",
        77: "Error off grid",
        78: "Initializing",
        79: "Setup mode",
        80: "Grid down",
        81: "BMS update required",
        82: "BMS configuration required",
        83: "Isolation test",
        84: "Self test",
        85: "Remote control",
    }
    return switcher.get(input, "<Unknown>")
