"""Signal analysis services"""

from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.models.signal_measurement import SignalMeasurement
from typing import List, Dict, Optional
import statistics


class SignalAnalyzer:
    """Class for analyzing signal measurement data"""
    
    @staticmethod
    def get_heatmap_data(
        db: Session,
        min_lat: float,
        max_lat: float,
        min_lon: float,
        max_lon: float,
        signal_type: Optional[str] = None,
        operator: Optional[str] = None
    ) -> List[Dict]:
        """
        Get signal data for heatmap visualization.
        
        Args:
            db: Database session
            min_lat, max_lat: Latitude bounds
            min_lon, max_lon: Longitude bounds
            signal_type: Optional signal type filter
            operator: Optional operator filter
            
        Returns:
            List of data points with coordinates and signal strength
        """
        query = db.query(SignalMeasurement).filter(
            and_(
                SignalMeasurement.latitude >= min_lat,
                SignalMeasurement.latitude <= max_lat,
                SignalMeasurement.longitude >= min_lon,
                SignalMeasurement.longitude <= max_lon
            )
        )
        
        if signal_type:
            query = query.filter(SignalMeasurement.signal_type == signal_type)
        if operator:
            query = query.filter(SignalMeasurement.operator == operator)
        
        measurements = query.all()
        
        return [
            {
                "lat": m.latitude,
                "lon": m.longitude,
                "signal_dbm": m.signal_strength_dbm,
                "quality": m.signal_quality,
                "operator": m.operator
            }
            for m in measurements
        ]
    
    @staticmethod
    def calculate_coverage_statistics(
        db: Session,
        area_bounds: Dict[str, float],
        operator: Optional[str] = None
    ) -> Dict:
        """
        Calculate coverage statistics for an area.
        
        Args:
            db: Database session
            area_bounds: Dictionary with min_lat, max_lat, min_lon, max_lon
            operator: Optional operator filter
            
        Returns:
            Dictionary with coverage statistics
        """
        query = db.query(SignalMeasurement).filter(
            and_(
                SignalMeasurement.latitude >= area_bounds["min_lat"],
                SignalMeasurement.latitude <= area_bounds["max_lat"],
                SignalMeasurement.longitude >= area_bounds["min_lon"],
                SignalMeasurement.longitude <= area_bounds["max_lon"]
            )
        )
        
        if operator:
            query = query.filter(SignalMeasurement.operator == operator)
        
        measurements = query.all()
        
        if not measurements:
            return {
                "total_measurements": 0,
                "average_signal_dbm": None,
                "median_signal_dbm": None,
                "min_signal_dbm": None,
                "max_signal_dbm": None,
                "std_deviation": None,
                "coverage_percentage": 0,
                "good_signal_count": 0,
                "poor_signal_count": 0
            }
        
        signals = [m.signal_strength_dbm for m in measurements]
        
        # Good signal threshold: -85 dBm or better
        good_signal_threshold = -85
        good_signals = [s for s in signals if s >= good_signal_threshold]
        
        return {
            "total_measurements": len(measurements),
            "average_signal_dbm": round(statistics.mean(signals), 2),
            "median_signal_dbm": round(statistics.median(signals), 2),
            "min_signal_dbm": round(min(signals), 2),
            "max_signal_dbm": round(max(signals), 2),
            "std_deviation": round(statistics.stdev(signals) if len(signals) > 1 else 0, 2),
            "coverage_percentage": round((len(good_signals) / len(signals)) * 100, 2),
            "good_signal_count": len(good_signals),
            "poor_signal_count": len(signals) - len(good_signals)
        }
    
    @staticmethod
    def identify_dead_zones(
        db: Session,
        area_bounds: Dict[str, float],
        threshold_dbm: float = -100
    ) -> List[Dict]:
        """
        Identify areas with weak signal (dead zones).
        
        Args:
            db: Database session
            area_bounds: Dictionary with area boundaries
            threshold_dbm: Signal strength threshold for dead zones
            
        Returns:
            List of measurements below threshold
        """
        measurements = db.query(SignalMeasurement).filter(
            and_(
                SignalMeasurement.latitude >= area_bounds["min_lat"],
                SignalMeasurement.latitude <= area_bounds["max_lat"],
                SignalMeasurement.longitude >= area_bounds["min_lon"],
                SignalMeasurement.longitude <= area_bounds["max_lon"],
                SignalMeasurement.signal_strength_dbm < threshold_dbm
            )
        ).all()
        
        return [
            {
                "lat": m.latitude,
                "lon": m.longitude,
                "signal_dbm": m.signal_strength_dbm,
                "operator": m.operator,
                "measured_at": m.measured_at.isoformat()
            }
            for m in measurements
        ]
    
    @staticmethod
    def compare_operators(
        db: Session,
        area_bounds: Dict[str, float]
    ) -> Dict[str, Dict]:
        """
        Compare signal performance between operators.
        
        Args:
            db: Database session
            area_bounds: Dictionary with area boundaries
            
        Returns:
            Dictionary with statistics for each operator
        """
        operators = db.query(SignalMeasurement.operator).filter(
            SignalMeasurement.operator.isnot(None)
        ).distinct().all()
        
        results = {}
        for (operator,) in operators:
            stats = SignalAnalyzer.calculate_coverage_statistics(
                db, area_bounds, operator
            )
            results[operator] = stats
        
        return results
    
    @staticmethod
    def get_signal_trends(
        db: Session,
        operator: Optional[str] = None,
        days: int = 30
    ) -> Dict:
        """
        Analyze signal strength trends over time.
        
        Args:
            db: Database session
            operator: Optional operator filter
            days: Number of days to analyze
            
        Returns:
            Trend analysis data
        """
        from datetime import datetime, timedelta
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        query = db.query(SignalMeasurement).filter(
            SignalMeasurement.measured_at >= start_date
        )
        
        if operator:
            query = query.filter(SignalMeasurement.operator == operator)
        
        measurements = query.all()
        
        if not measurements:
            return {"trend": "no_data", "measurements": 0}
        
        # Group by date
        daily_averages = {}
        for m in measurements:
            date_key = m.measured_at.date().isoformat()
            if date_key not in daily_averages:
                daily_averages[date_key] = []
            daily_averages[date_key].append(m.signal_strength_dbm)
        
        # Calculate daily means
        trend_data = []
        for date, signals in sorted(daily_averages.items()):
            trend_data.append({
                "date": date,
                "avg_signal": round(statistics.mean(signals), 2),
                "count": len(signals)
            })
        
        return {
            "trend": "improving" if len(trend_data) > 1 and trend_data[-1]["avg_signal"] > trend_data[0]["avg_signal"] else "stable",
            "measurements": len(measurements),
            "daily_data": trend_data
        }


# Global instance
signal_analyzer = SignalAnalyzer()

