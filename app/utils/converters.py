"""Unit conversion utility functions"""

import math
from typing import Tuple


def dbm_to_watts(dbm: float) -> float:
    """Convert dBm to Watts"""
    return 10 ** ((dbm - 30) / 10)


def watts_to_dbm(watts: float) -> float:
    """Convert Watts to dBm"""
    return 10 * math.log10(watts * 1000)


def dbm_to_mw(dbm: float) -> float:
    """Convert dBm to milliwatts"""
    return 10 ** (dbm / 10)


def mw_to_dbm(mw: float) -> float:
    """Convert milliwatts to dBm"""
    return 10 * math.log10(mw)


def db_to_linear(db: float) -> float:
    """Convert dB to linear scale"""
    return 10 ** (db / 10)


def linear_to_db(linear: float) -> float:
    """Convert linear scale to dB"""
    return 10 * math.log10(linear)


def mhz_to_ghz(mhz: float) -> float:
    """Convert MHz to GHz"""
    return mhz / 1000


def ghz_to_mhz(ghz: float) -> float:
    """Convert GHz to MHz"""
    return ghz * 1000


def km_to_meters(km: float) -> float:
    """Convert kilometers to meters"""
    return km * 1000


def meters_to_km(meters: float) -> float:
    """Convert meters to kilometers"""
    return meters / 1000


def degrees_to_radians(degrees: float) -> float:
    """Convert degrees to radians"""
    return degrees * math.pi / 180


def radians_to_degrees(radians: float) -> float:
    """Convert radians to degrees"""
    return radians * 180 / math.pi


def signal_quality_from_dbm(dbm: float) -> int:
    """
    Convert signal strength (dBm) to quality percentage (0-100).
    
    Args:
        dbm: Signal strength in dBm
        
    Returns:
        Quality percentage (0-100)
    """
    if dbm >= -50:
        return 100
    elif dbm <= -100:
        return 0
    else:
        # Linear interpolation between -100 and -50 dBm
        return int((dbm + 100) * 2)


def signal_bars_from_dbm(dbm: float) -> int:
    """
    Convert signal strength to signal bars (1-5).
    
    Args:
        dbm: Signal strength in dBm
        
    Returns:
        Number of bars (1-5)
    """
    if dbm >= -70:
        return 5
    elif dbm >= -85:
        return 4
    elif dbm >= -100:
        return 3
    elif dbm >= -110:
        return 2
    else:
        return 1

