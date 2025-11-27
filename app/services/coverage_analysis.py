"""Coverage analysis and heatmap service"""

import math
from typing import List, Dict, Tuple, Optional
from sqlalchemy.orm import Session
from app.models.tower import Tower
from app.services.rf_calculations import rf_calc


class CoverageAnalyzer:
    """Service for analyzing coverage with grid-based heatmaps"""
    
    EARTH_RADIUS_KM = 6371.0
    
    @staticmethod
    def point_in_polygon(point: Tuple[float, float], polygon: List[List[float]]) -> bool:
        """
        Ray casting algorithm to check if a point is inside a polygon.
        
        Args:
            point: (lat, lng) tuple
            polygon: List of [lat, lng] coordinates
            
        Returns:
            True if point is inside polygon
        """
        lat, lng = point
        n = len(polygon)
        inside = False
        
        p1_lat, p1_lng = polygon[0]
        for i in range(1, n + 1):
            p2_lat, p2_lng = polygon[i % n]
            if lng > min(p1_lng, p2_lng):
                if lng <= max(p1_lng, p2_lng):
                    if lat <= max(p1_lat, p2_lat):
                        if p1_lng != p2_lng:
                            x_inters = (lng - p1_lng) * (p2_lat - p1_lat) / (p2_lng - p1_lng) + p1_lat
                        if p1_lat == p2_lat or lat <= x_inters:
                            inside = not inside
            p1_lat, p1_lng = p2_lat, p2_lng
        
        return inside
    
    @staticmethod
    def get_polygon_bounds(polygon: List[List[float]]) -> Dict[str, float]:
        """
        Get bounding box of polygon.
        
        Args:
            polygon: List of [lat, lng] coordinates
            
        Returns:
            Dict with min_lat, max_lat, min_lng, max_lng
        """
        lats = [p[0] for p in polygon]
        lngs = [p[1] for p in polygon]
        
        return {
            "min_lat": min(lats),
            "max_lat": max(lats),
            "min_lng": min(lngs),
            "max_lng": max(lngs),
        }
    
    @staticmethod
    def calc_polygon_area_km2(polygon: List[List[float]]) -> float:
        """
        Calculate polygon area using Shoelace formula (in km²).
        Assumes small areas where lat/lng can be treated as Cartesian.
        
        Args:
            polygon: List of [lat, lng] coordinates
            
        Returns:
            Area in km²
        """
        # Get center latitude for conversion factor
        lats = [p[0] for p in polygon]
        center_lat = sum(lats) / len(lats)
        
        # Conversion factors
        lat_km = 111.0  # 1 degree latitude = ~111 km
        lng_km = 111.0 * math.cos(math.radians(center_lat))  # varies by latitude
        
        # Shoelace formula
        area = 0.0
        n = len(polygon)
        for i in range(n):
            p1 = polygon[i]
            p2 = polygon[(i + 1) % n]
            area += p1[1] * p2[0] - p2[1] * p1[0]
        
        area = abs(area) / 2.0
        
        # Convert from degrees² to km²
        area_km2 = area * (lat_km / 360) * (lng_km / 360) * 129600  # 360² conversion
        
        return area_km2
    
    @staticmethod
    def generate_grid(
        bounds: Dict[str, float],
        grid_step_km: float = 0.1
    ) -> List[Tuple[float, float]]:
        """
        Generate grid points within bounding box.
        
        Args:
            bounds: Dict with min_lat, max_lat, min_lng, max_lng
            grid_step_km: Grid spacing in km (default 0.1 km = 100m)
            
        Returns:
            List of (lat, lng) tuples
        """
        # Conversion factors
        center_lat = (bounds["min_lat"] + bounds["max_lat"]) / 2
        lat_km_per_degree = 111.0
        lng_km_per_degree = 111.0 * math.cos(math.radians(center_lat))
        
        # Convert km to degrees
        lat_step_deg = grid_step_km / lat_km_per_degree
        lng_step_deg = grid_step_km / lng_km_per_degree
        
        # Generate grid
        grid = []
        lat = bounds["min_lat"]
        while lat <= bounds["max_lat"]:
            lng = bounds["min_lng"]
            while lng <= bounds["max_lng"]:
                grid.append((lat, lng))
                lng += lng_step_deg
            lat += lat_step_deg
        
        return grid
    
    @staticmethod
    def analyze_coverage(
        db: Session,
        polygon: List[List[float]],
        operator: Optional[str] = None,
        threshold_dbm: float = -85,
        grid_step_km: float = 0.1
    ) -> Dict:
        """
        Analyze coverage within polygon using grid-based approach.
        
        Args:
            db: Database session
            polygon: Polygon coordinates [[lat, lng], ...]
            operator: Optional operator filter
            threshold_dbm: Signal threshold for "coverage" (-85 dBm default)
            grid_step_km: Grid spacing in km (100m = 0.1km)
            
        Returns:
            Dict with grid points and statistics
        """
        # Get towers
        query = db.query(Tower)
        if operator:
            query = query.filter(Tower.operator == operator)
        towers = query.all()
        
        if not towers:
            return {
                "grid": [],
                "stats": {
                    "coverage_pct": 0.0,
                    "gap_area_km2": 0.0,
                    "total_area_km2": 0.0,
                    "avg_signal_dbm": None,
                }
            }
        
        # Get bounds and area
        bounds = CoverageAnalyzer.get_polygon_bounds(polygon)
        total_area_km2 = CoverageAnalyzer.calc_polygon_area_km2(polygon)
        
        # Generate grid
        grid_points = CoverageAnalyzer.generate_grid(bounds, grid_step_km)
        
        # Analyze each grid point
        grid_results = []
        covered_count = 0
        signal_sum = 0.0
        signal_count = 0
        
        for lat, lng in grid_points:
            # Check if point is inside polygon
            if not CoverageAnalyzer.point_in_polygon((lat, lng), polygon):
                continue
            
            # Find closest tower
            min_distance = float('inf')
            closest_tower = None
            
            for tower in towers:
                # Cast SQLAlchemy Column values to float
                distance = rf_calc.calculate_distance(
                    lat, 
                    lng, 
                    float(tower.latitude),  # type: ignore
                    float(tower.longitude)  # type: ignore
                )
                if distance < min_distance:
                    min_distance = distance
                    closest_tower = tower
            
            if closest_tower:
                # Estimate signal strength
                signal_dbm = rf_calc.estimate_signal_from_tower(
                    distance_km=min_distance,
                    frequency_mhz=2100,  # LTE default
                    tx_power_dbm=43,
                    tx_gain_dbi=15,
                    rx_gain_dbi=0
                )
                
                # Classify quality
                if signal_dbm >= -70:
                    quality = "excellent"
                elif signal_dbm >= -85:
                    quality = "good"
                elif signal_dbm >= -95:
                    quality = "fair"
                else:
                    quality = "poor"
                
                # Check coverage
                if signal_dbm >= threshold_dbm:
                    covered_count += 1
                
                signal_sum += signal_dbm
                signal_count += 1
                
                grid_results.append({
                    "lat": lat,
                    "lng": lng,
                    "signal_dbm": round(signal_dbm, 1),
                    "quality": quality,
                })
        
        # Calculate statistics
        if signal_count == 0:
            coverage_pct = 0.0
            avg_signal = None
        else:
            coverage_pct = (covered_count / signal_count) * 100
            avg_signal = round(signal_sum / signal_count, 1)
        
        gap_area_km2 = total_area_km2 * (1 - coverage_pct / 100)
        
        return {
            "grid": grid_results,
            "stats": {
                "coverage_pct": round(coverage_pct, 1),
                "gap_area_km2": round(gap_area_km2, 2),
                "total_area_km2": round(total_area_km2, 2),
                "avg_signal_dbm": avg_signal,
                "grid_points_analyzed": signal_count,
            }
        }


# Global instance
coverage_analyzer = CoverageAnalyzer()
