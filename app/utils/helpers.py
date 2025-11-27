"""Helper utility functions"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import hashlib
import random
import string


def generate_random_string(length: int = 10) -> str:
    """
    Generate a random string.
    
    Args:
        length: Length of string
        
    Returns:
        Random string
    """
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def generate_hash(data: str) -> str:
    """
    Generate SHA256 hash of data.
    
    Args:
        data: String to hash
        
    Returns:
        Hex digest of hash
    """
    return hashlib.sha256(data.encode()).hexdigest()


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format datetime object.
    
    Args:
        dt: Datetime object
        format_str: Format string
        
    Returns:
        Formatted datetime string
    """
    return dt.strftime(format_str)


def parse_datetime(dt_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> Optional[datetime]:
    """
    Parse datetime string.
    
    Args:
        dt_str: Datetime string
        format_str: Format string
        
    Returns:
        Datetime object or None
    """
    try:
        return datetime.strptime(dt_str, format_str)
    except ValueError:
        return None


def get_date_range(days: int = 30) -> tuple[datetime, datetime]:
    """
    Get date range for the last N days.
    
    Args:
        days: Number of days
        
    Returns:
        Tuple of (start_date, end_date)
    """
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    return start_date, end_date


def paginate_results(items: List[Any], page: int = 1, page_size: int = 50) -> Dict:
    """
    Paginate a list of items.
    
    Args:
        items: List of items
        page: Page number (1-indexed)
        page_size: Items per page
        
    Returns:
        Dictionary with paginated results
    """
    total = len(items)
    total_pages = (total + page_size - 1) // page_size
    
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    
    return {
        "items": items[start_idx:end_idx],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1
    }


def format_signal_strength(dbm: float) -> str:
    """
    Format signal strength with description.
    
    Args:
        dbm: Signal strength in dBm
        
    Returns:
        Formatted string with description
    """
    if dbm >= -70:
        quality = "Excellent"
    elif dbm >= -85:
        quality = "Good"
    elif dbm >= -100:
        quality = "Fair"
    elif dbm >= -110:
        quality = "Poor"
    else:
        quality = "Very Poor"
    
    return f"{dbm} dBm ({quality})"


def calculate_percentage(value: float, total: float) -> float:
    """
    Calculate percentage safely.
    
    Args:
        value: Value
        total: Total
        
    Returns:
        Percentage (0-100)
    """
    if total == 0:
        return 0.0
    return round((value / total) * 100, 2)


def flatten_dict(d: Dict, parent_key: str = '', sep: str = '_') -> Dict:
    """
    Flatten a nested dictionary.
    
    Args:
        d: Dictionary to flatten
        parent_key: Parent key prefix
        sep: Separator
        
    Returns:
        Flattened dictionary
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

