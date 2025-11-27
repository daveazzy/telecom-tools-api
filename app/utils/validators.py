"""Validation utility functions"""

import re
from typing import Optional


def validate_latitude(lat: float) -> bool:
    """
    Validate latitude value.
    
    Args:
        lat: Latitude value
        
    Returns:
        True if valid, False otherwise
    """
    return -90 <= lat <= 90


def validate_longitude(lon: float) -> bool:
    """
    Validate longitude value.
    
    Args:
        lon: Longitude value
        
    Returns:
        True if valid, False otherwise
    """
    return -180 <= lon <= 180


def validate_coordinates(lat: float, lon: float) -> bool:
    """
    Validate coordinate pair.
    
    Args:
        lat: Latitude
        lon: Longitude
        
    Returns:
        True if both valid, False otherwise
    """
    return validate_latitude(lat) and validate_longitude(lon)


def validate_frequency_mhz(freq: float) -> bool:
    """
    Validate frequency value (MHz).
    
    Args:
        freq: Frequency in MHz
        
    Returns:
        True if valid, False otherwise
    """
    # Common cellular frequencies: 450-6000 MHz
    return 0 < freq < 10000


def validate_signal_strength(dbm: float) -> bool:
    """
    Validate signal strength value (dBm).
    
    Args:
        dbm: Signal strength in dBm
        
    Returns:
        True if valid, False otherwise
    """
    # Typical range for cellular signals
    return -120 <= dbm <= 0


def validate_email(email: str) -> bool:
    """
    Validate email format.
    
    Args:
        email: Email address
        
    Returns:
        True if valid format, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_cell_id(cell_id: str) -> bool:
    """
    Validate cell ID format.
    
    Args:
        cell_id: Cell ID string
        
    Returns:
        True if valid format, False otherwise
    """
    # Cell ID should be alphanumeric
    return bool(cell_id and cell_id.replace('-', '').replace('_', '').isalnum())


def sanitize_operator_name(operator: str) -> str:
    """
    Sanitize and normalize operator name.
    
    Args:
        operator: Operator name
        
    Returns:
        Sanitized operator name
    """
    return operator.strip().upper()


def validate_distance(distance_km: float) -> bool:
    """
    Validate distance value.
    
    Args:
        distance_km: Distance in kilometers
        
    Returns:
        True if valid, False otherwise
    """
    return 0 < distance_km < 1000  # Max 1000km

