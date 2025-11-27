"""Tower data loader - reads from local CSV database (RN towers)"""

import logging
import math
import csv
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class TowerDataLoader:
    """Client for reading tower data from CSV file with Brazilian tower coordinates"""
    
    EARTH_RADIUS_KM = 6371.0
    
    # Cache de torres do CSV
    _csv_towers_cache: Optional[List[Dict[str, Any]]] = None
    
    @staticmethod
    def parse_coordinate(coord_str: str) -> Optional[float]:
        """
        Convert coordinate string from DD+Direction+MMSS format to decimal degrees.
        Example: '05S3009' -> -5.5025 (5°30'09"S)
                 '36W5124' -> -36.8567 (36°51'24"W)
        
        Args:
            coord_str: Coordinate string in format DD[N/S/E/W]MMSS
            
        Returns:
            Decimal degree coordinate or None if parsing fails
        """
        if not coord_str or not isinstance(coord_str, str):
            return None
        
        coord_str = coord_str.strip().upper()
        
        # Pattern: DD + Direction + MMSS
        match = re.search(r'(\d+)([NSEW])(\d+)', coord_str)
        if not match:
            return None
        
        try:
            dd_str, direction_char, mmss_str = match.groups()
            
            # Parse degrees
            degrees = int(dd_str)
            
            # Parse minutes and seconds from MMSS (4 digits)
            if len(mmss_str) >= 4:
                minutes = int(mmss_str[0:2])
                seconds = int(mmss_str[2:4])
            else:
                return None
            
            # Calculate decimal
            decimal = degrees + minutes / 60.0 + seconds / 3600.0
            
            # Apply direction
            if direction_char in 'SW':
                decimal = -decimal
            
            return decimal
        except (ValueError, IndexError):
            pass
        
        return None
    
    @staticmethod
    def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points in km"""
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return TowerDataLoader.EARTH_RADIUS_KM * c
    
    @classmethod
    def _load_csv_towers(cls) -> List[Dict[str, Any]]:
        """
        Load towers from CSV file (erbs - RN.csv format).
        Cache in memory for performance.

        Returns:
            List of towers from CSV
        """
        if cls._csv_towers_cache is not None:
            return cls._csv_towers_cache

        csv_path = Path(__file__).parent.parent.parent / "assets" / "erbs - RN.csv"

        if not csv_path.exists():
            logger.warning(f"CSV file not found: {csv_path}")
            return []

        logger.info(f"Loading towers from CSV: {csv_path}")

        towers = []
        errors = 0
        
        try:
            with open(csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        # Parse coordinates
                        lat_str = row.get("Latitude", "").strip()
                        lon_str = row.get("Longitude", "").strip()
                        
                        lat = cls.parse_coordinate(lat_str)
                        lon = cls.parse_coordinate(lon_str)
                        
                        if lat is None or lon is None:
                            errors += 1
                            if errors <= 5:
                                logger.debug(f"Could not parse coordinates on row {row_num}: lat={lat_str}, lon={lon_str}")
                            continue
                        
                        # Detect technology
                        tech = None
                        tech_map = {
                            '2G': '2G',
                            '3G': '3G',
                            '4G': '4G',
                            '5G': '5G'
                        }
                        
                        # Check which technologies are available
                        technologies = []
                        for tech_code, tech_name in tech_map.items():
                            if row.get(tech_code, "").strip().upper() == "SIM":
                                technologies.append(tech_name)
                        
                        # Use latest technology as primary
                        if technologies:
                            tech = technologies[-1]  # Get latest (4G/5G preferred)
                        else:
                            tech = "Unknown"
                        
                        tower = {
                            "cellid": row.get("NumEstacao", "").strip(),
                            "latitude": lat,
                            "longitude": lon,
                            "lat": lat,  # Alias for compatibility
                            "lon": lon,  # Alias for compatibility
                            "operator": row.get("NomeEntidade", "Unknown").strip(),
                            "city": row.get("NomeMunicipio", "").strip(),
                            "address": row.get("EnderecoEstacao", "").strip(),
                            "technology": tech,
                            "has_2g": row.get("2G", "").strip().upper() == "SIM",
                            "has_3g": row.get("3G", "").strip().upper() == "SIM",
                            "has_4g": row.get("4G", "").strip().upper() == "SIM",
                            "has_5g": row.get("5G", "").strip().upper() == "SIM",
                        }
                        towers.append(tower)
                        
                    except Exception as e:
                        errors += 1
                        if errors <= 5:
                            logger.debug(f"Error parsing row {row_num}: {e}")
                        continue

            logger.info(f"Loaded {len(towers):,} towers from CSV")
            if errors > 0:
                logger.info(f"Warning: {errors:,} rows had parsing errors")
            cls._csv_towers_cache = towers
            return towers

        except Exception as e:
            logger.error(f"Error loading CSV: {e}")
            return []
    
    @staticmethod
    def _get_operator_name(operator: str) -> str:
        """Normalize operator name"""
        operator_map = {
            'TIM': 'TIM',
            'CLARO': 'Claro',
            'VIVO': 'Vivo',
            'OI': 'Oi',
            'NEXTEL': 'Nextel',
        }
        op_upper = operator.upper() if operator else "Unknown"
        return operator_map.get(op_upper, operator)
    
    @staticmethod
    def get_real_towers_fallback(latitude: float, longitude: float, radius_km: float = 5) -> List[Dict]:
        """
        Get towers from local CSV database within specified radius.
        
        Args:
            latitude: Search latitude
            longitude: Search longitude
            radius_km: Search radius in kilometers
            
        Returns:
            List of nearby towers sorted by distance
        """
        csv_towers = TowerDataLoader._load_csv_towers()
        if not csv_towers:
            logger.warning("Tower database not available")
            return []
        
        nearby = []
        for tower in csv_towers:
            try:
                dist = TowerDataLoader.haversine(
                    latitude, longitude, 
                    tower['latitude'], tower['longitude']
                )
                if dist <= radius_km:
                    tower['distance'] = round(dist, 2)
                    nearby.append(tower)
            except (ValueError, KeyError):
                continue
        
        # Sort by distance
        nearby.sort(key=lambda x: x.get('distance', float('inf')))
        
        logger.info(f"Found {len(nearby)} towers nearby (radius: {radius_km}km)")
        return nearby


# Backward compatibility alias
class OpenCellIDClient(TowerDataLoader):
    """Backward compatible alias for TowerDataLoader"""
    pass


# Global instance
opencellid_client = OpenCellIDClient()

