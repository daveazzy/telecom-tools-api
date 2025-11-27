"""
Tower Recommendation Engine
Implements clustering of coverage gaps and scoring for tower placement optimization
"""

from typing import List, Dict, Tuple
from dataclasses import dataclass
from enum import Enum
import math


class PriorityLevel(str, Enum):
    """Priority classification for recommendations"""
    HIGH = "high"      # score > 5
    MEDIUM = "medium"  # score 2-5
    LOW = "low"        # score < 2


@dataclass
class GapZone:
    """Represents a coverage gap area to analyze"""
    latitude: float
    longitude: float
    area_km2: float
    

@dataclass
class Recommendation:
    """Represents a recommended tower placement"""
    latitude: float
    longitude: float
    score: float
    priority: PriorityLevel
    population_reached: int
    cluster_id: int
    reason: str
    gap_count: int  # Number of gaps in this cluster
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for API response"""
        return {
            "location": {
                "latitude": round(self.latitude, 6),
                "longitude": round(self.longitude, 6)
            },
            "score": round(self.score, 2),
            "priority": self.priority.value,
            "population_reached": self.population_reached,
            "reason": self.reason,
            "gap_count": self.gap_count
        }


class RecommendationEngine:
    """
    Engine for analyzing coverage gaps and recommending tower placements
    
    Strategy:
    1. Cluster gaps within 2km radius (CLUSTERING_RADIUS_KM)
    2. Calculate cluster centroids
    3. Score each cluster: (population_estimate * area_km2) / 100000
    4. Classify priority: HIGH (>5), MEDIUM (2-5), LOW (<2)
    5. Return top 5 sorted by score descending
    """
    
    CLUSTERING_RADIUS_KM = 2.0  # Gaps within 2km are same cluster
    EARTH_RADIUS_KM = 6371.0    # For Haversine distance
    POPULATION_DENSITY_PER_KM2 = 500  # Estimated population per km² in coverage areas
    
    def __init__(self):
        pass
    
    @staticmethod
    def haversine_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calculate distance between two points in kilometers using Haversine formula"""
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lng = math.radians(lng2 - lng1)
        
        a = (math.sin(delta_lat / 2) ** 2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lng / 2) ** 2)
        c = 2 * math.asin(math.sqrt(a))
        
        return RecommendationEngine.EARTH_RADIUS_KM * c
    
    @staticmethod
    def cluster_gaps(gaps: List[GapZone], radius_km: float = CLUSTERING_RADIUS_KM) -> Dict[int, List[GapZone]]:
        """
        Cluster gaps using distance-based grouping (similar to k-means with radius constraint)
        
        Returns dict: {cluster_id: [gaps in cluster]}
        """
        if not gaps:
            return {}
        
        clusters: Dict[int, List[GapZone]] = {}
        assigned = set()
        cluster_id = 0
        
        for i, gap in enumerate(gaps):
            if i in assigned:
                continue
            
            # Start new cluster
            current_cluster = [gap]
            assigned.add(i)
            
            # Find all gaps within radius
            for j in range(i + 1, len(gaps)):
                if j not in assigned:
                    distance = RecommendationEngine.haversine_distance(
                        gap.latitude, gap.longitude,
                        gaps[j].latitude, gaps[j].longitude
                    )
                    if distance <= radius_km:
                        current_cluster.append(gaps[j])
                        assigned.add(j)
            
            clusters[cluster_id] = current_cluster
            cluster_id += 1
        
        return clusters
    
    @staticmethod
    def calculate_cluster_centroid(gaps: List[GapZone]) -> Tuple[float, float, float]:
        """
        Calculate centroid of a cluster of gaps
        
        Returns: (latitude, longitude, total_area_km2)
        """
        if not gaps:
            return 0.0, 0.0, 0.0
        
        avg_lat = sum(g.latitude for g in gaps) / len(gaps)
        avg_lng = sum(g.longitude for g in gaps) / len(gaps)
        total_area = sum(g.area_km2 for g in gaps)
        
        return avg_lat, avg_lng, total_area
    
    @staticmethod
    def calculate_priority(score: float) -> PriorityLevel:
        """Classify priority based on score"""
        if score > 5.0:
            return PriorityLevel.HIGH
        elif score >= 2.0:
            return PriorityLevel.MEDIUM
        else:
            return PriorityLevel.LOW
    
    @staticmethod
    def estimate_population_reached(area_km2: float) -> int:
        """
        Estimate population that would be reached by a tower
        Assumes standard population density + area of coverage
        
        Formula: area_km2 * population_density_per_km2 * coverage_factor
        Coverage factor accounts for actual population distribution (not all area equally populated)
        """
        # Assume typical mobile coverage of ~3.5km radius (38.5 km²)
        # But gaps are typically in less dense areas, so reduce density estimate
        density = RecommendationEngine.POPULATION_DENSITY_PER_KM2
        coverage_radius_km = 3.5
        typical_coverage_area_km2 = math.pi * (coverage_radius_km ** 2)
        
        # Population is proportional to gap area vs typical coverage area
        if area_km2 > 0:
            ratio = min(area_km2 / typical_coverage_area_km2, 1.0)
            return int(density * typical_coverage_area_km2 * ratio)
        
        return int(density * typical_coverage_area_km2)
    
    def generate_recommendations(
        self,
        gaps: List[GapZone],
        max_recommendations: int = 5
    ) -> List[Recommendation]:
        """
        Main method: Generate tower recommendations from coverage gaps
        
        Process:
        1. Cluster gaps within 2km radius
        2. Calculate centroid for each cluster
        3. Score by area * population density
        4. Classify priority level
        5. Sort by score (descending)
        6. Return top N
        """
        if not gaps:
            return []
        
        # Step 1: Cluster gaps
        clusters = self.cluster_gaps(gaps, self.CLUSTERING_RADIUS_KM)
        
        # Step 2-3: Generate recommendations from clusters
        recommendations: List[Recommendation] = []
        
        for cluster_id, cluster_gaps in clusters.items():
            # Calculate centroid
            lat, lng, total_area = self.calculate_cluster_centroid(cluster_gaps)
            
            # Calculate score: (area_km2 * population_factor) / normalization
            # Score formula gives higher weight to larger gaps with more affected area
            population_factor = self.POPULATION_DENSITY_PER_KM2 / 100  # Normalize
            score = (total_area * population_factor) / 1000  # Adjust scale to 0-10 range
            score = min(score * 10, 10.0)  # Cap at 10
            
            # Estimate population reached
            population_reached = self.estimate_population_reached(total_area)
            
            # Classify priority
            priority = self.calculate_priority(score)
            
            # Generate reason
            reason = f"{len(cluster_gaps)} gap(s) covering {total_area:.2f} km²"
            
            recommendation = Recommendation(
                latitude=lat,
                longitude=lng,
                score=score,
                priority=priority,
                population_reached=population_reached,
                cluster_id=cluster_id,
                reason=reason,
                gap_count=len(cluster_gaps)
            )
            
            recommendations.append(recommendation)
        
        # Step 4: Sort by priority (HIGH > MEDIUM > LOW) then by score descending
        def sort_key(r):
            priority_order = {PriorityLevel.HIGH: 0, PriorityLevel.MEDIUM: 1, PriorityLevel.LOW: 2}
            return (priority_order[r.priority], -r.score)
        
        recommendations.sort(key=sort_key)
        
        # Step 5: Return top N
        return recommendations[:max_recommendations]
    
    def get_top_recommendations(
        self,
        gaps: List[GapZone],
        count: int = 5
    ) -> List[Dict]:
        """
        Generate and return top N recommendations as dictionaries
        """
        recommendations = self.generate_recommendations(gaps, max_recommendations=count)
        return [rec.to_dict() for rec in recommendations]


def create_gap_zones_from_grid(
    grid_points: List[Dict],
    threshold_signal_dbm: float = -95.0
) -> List[GapZone]:
    """
    Helper: Convert coverage grid with poor signal to gap zones
    
    Args:
        grid_points: List of {lat, lng, signal_dbm, quality} from coverage analysis
        threshold_signal_dbm: Signal level below which area is considered a gap
    
    Returns:
        List of GapZone objects representing coverage gaps
    """
    gaps = []
    
    # Group poor-quality points (gaps)
    poor_points = [
        p for p in grid_points 
        if p.get("signal_dbm", 0) < threshold_signal_dbm
    ]
    
    if not poor_points:
        return []
    
    # For simplicity, create gap zones at poor quality points
    # In production, would cluster and calculate polygon area
    grid_step_km = 0.1  # Default from coverage_analysis
    area_per_point_km2 = grid_step_km * grid_step_km
    
    for point in poor_points:
        gap = GapZone(
            latitude=float(point.get("lat", 0)),
            longitude=float(point.get("lng", 0)),
            area_km2=area_per_point_km2
        )
        gaps.append(gap)
    
    return gaps
