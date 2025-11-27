"""Tower/cell site service"""

from sqlalchemy.orm import Session
from app.models.tower import Tower
from app.services.rf_calculations import rf_calc
from typing import List, Optional, Dict


class TowerService:
    """Service for tower/cell site operations"""
    
    @staticmethod
    def find_nearby_towers(
        db: Session,
        latitude: float,
        longitude: float,
        radius_km: float = 5.0,
        operator: Optional[str] = None,
        technology: Optional[str] = None
    ) -> List[Tower]:
        """
        Find towers within a radius of a location.
        
        Args:
            db: Database session
            latitude: Center latitude
            longitude: Center longitude
            radius_km: Search radius in kilometers
            operator: Optional operator filter
            technology: Optional technology filter
            
        Returns:
            List of towers with distance information
        """
        query = db.query(Tower)
        
        if operator:
            query = query.filter(Tower.operator == operator)
        if technology:
            query = query.filter(Tower.technology == technology)
        
        all_towers = query.all()
        
        # Filter by distance and add distance field
        nearby_towers = []
        for tower in all_towers:
            distance = rf_calc.calculate_distance(
                latitude, longitude,
                tower.latitude, tower.longitude
            )
            
            if distance <= radius_km:
                # Add distance attribute for sorting
                tower.distance_km = round(distance, 2)
                nearby_towers.append(tower)
        
        # Sort by distance
        nearby_towers.sort(key=lambda t: t.distance_km)
        
        return nearby_towers
    
    @staticmethod
    def get_tower_by_cell_id(db: Session, cell_id: str) -> Optional[Tower]:
        """
        Get tower by cell ID.
        
        Args:
            db: Database session
            cell_id: Cell ID to search for
            
        Returns:
            Tower object or None
        """
        return db.query(Tower).filter(Tower.cell_id == cell_id).first()
    
    @staticmethod
    def calculate_coverage_area(tower: Tower) -> Dict:
        """
        Calculate theoretical coverage area for a tower.
        
        Args:
            tower: Tower object
            
        Returns:
            Dictionary with coverage information
        """
        # Default values if not specified
        coverage_radius = tower.coverage_radius_km if tower.coverage_radius_km else 5.0
        frequency = tower.frequency_mhz if tower.frequency_mhz else 2100  # Default LTE frequency
        
        # Calculate coverage area
        area_km2 = 3.14159 * (coverage_radius ** 2)
        
        # Estimate based on technology
        if tower.technology in ["5G", "NR"]:
            typical_radius = 0.5  # 5G typically has shorter range
        elif tower.technology in ["4G", "LTE"]:
            typical_radius = 5.0
        else:
            typical_radius = 10.0  # 3G/2G
        
        return {
            "coverage_radius_km": coverage_radius,
            "coverage_area_km2": round(area_km2, 2),
            "typical_radius_km": typical_radius,
            "frequency_mhz": frequency,
            "technology": tower.technology
        }
    
    @staticmethod
    def get_operator_statistics(db: Session) -> Dict:
        """
        Get statistics about towers by operator.
        
        Args:
            db: Database session
            
        Returns:
            Dictionary with operator statistics
        """
        from sqlalchemy import func
        
        stats = db.query(
            Tower.operator,
            func.count(Tower.id).label('tower_count'),
            func.avg(Tower.frequency_mhz).label('avg_frequency')
        ).group_by(Tower.operator).all()
        
        result = {}
        for operator, count, avg_freq in stats:
            result[operator] = {
                "tower_count": count,
                "avg_frequency_mhz": round(float(avg_freq), 2) if avg_freq else None
            }
        
        return result
    
    @staticmethod
    def calculate_best_server(
        db: Session,
        latitude: float,
        longitude: float,
        signal_measurements: Dict[str, float]
    ) -> Optional[Tower]:
        """
        Determine the best serving tower based on location and signal strength.
        
        Args:
            db: Database session
            latitude: User latitude
            longitude: User longitude
            signal_measurements: Dictionary of cell_id to signal_strength
            
        Returns:
            Best tower or None
        """
        if not signal_measurements:
            # If no signal data, find closest tower
            nearby = TowerService.find_nearby_towers(db, latitude, longitude, 10.0)
            return nearby[0] if nearby else None
        
        # Find towers matching measured cell IDs
        best_signal = float('-inf')
        best_tower = None
        
        for cell_id, signal_dbm in signal_measurements.items():
            tower = TowerService.get_tower_by_cell_id(db, cell_id)
            if tower and signal_dbm > best_signal:
                best_signal = signal_dbm
                best_tower = tower
        
        return best_tower


# Global instance
tower_service = TowerService()

