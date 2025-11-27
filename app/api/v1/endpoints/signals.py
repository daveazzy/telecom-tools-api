"""Signal measurement endpoints"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_user_optional
from app.models.user import User
from app.models.signal_measurement import SignalMeasurement
from app.schemas.signal import (
    SignalMeasurementCreate,
    SignalMeasurementResponse,
    SignalHeatmapRequest,
    HeatmapDataPoint,
    CoverageStatistics
)
from app.services.signal_analysis import signal_analyzer

router = APIRouter()


@router.post("", response_model=SignalMeasurementResponse, status_code=status.HTTP_201_CREATED)
async def create_measurement(
    measurement: SignalMeasurementCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new signal measurement.
    
    Args:
        measurement: Signal measurement data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Created measurement
    """
    new_measurement = SignalMeasurement(
        user_id=current_user.id,
        **measurement.model_dump()
    )
    
    db.add(new_measurement)
    db.commit()
    db.refresh(new_measurement)
    
    return new_measurement


@router.get("", response_model=List[SignalMeasurementResponse])
async def list_measurements(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=1000),
    operator: Optional[str] = None,
    signal_type: Optional[str] = None,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    List signal measurements for current user.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        operator: Filter by operator
        signal_type: Filter by signal type
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List of measurements
    """
    query = db.query(SignalMeasurement)
    # If authenticated, return measurements for that user only
    if current_user:
        query = query.filter(SignalMeasurement.user_id == current_user.id)
    
    if operator:
        query = query.filter(SignalMeasurement.operator == operator)
    if signal_type:
        query = query.filter(SignalMeasurement.signal_type == signal_type)
    
    measurements = query.order_by(
        SignalMeasurement.measured_at.desc()
    ).offset(skip).limit(limit).all()
    
    return measurements


@router.get("/{measurement_id}", response_model=SignalMeasurementResponse)
async def get_measurement(
    measurement_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get signal measurement by ID.
    
    Args:
        measurement_id: Measurement ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Measurement data
    """
    measurement = db.query(SignalMeasurement).filter(
        SignalMeasurement.id == measurement_id,
        SignalMeasurement.user_id == current_user.id
    ).first()
    
    if not measurement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Measurement not found"
        )
    
    return measurement


@router.delete("/{measurement_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_measurement(
    measurement_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete signal measurement.
    
    Args:
        measurement_id: Measurement ID
        current_user: Current authenticated user
        db: Database session
    """
    measurement = db.query(SignalMeasurement).filter(
        SignalMeasurement.id == measurement_id,
        SignalMeasurement.user_id == current_user.id
    ).first()
    
    if not measurement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Measurement not found"
        )
    
    db.delete(measurement)
    db.commit()


@router.post("/heatmap", response_model=List[HeatmapDataPoint])
async def get_heatmap_data(
    request: SignalHeatmapRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get heatmap data for signal visualization.
    
    Args:
        request: Heatmap request parameters
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Heatmap data points
    """
    data = signal_analyzer.get_heatmap_data(
        db=db,
        min_lat=request.min_lat,
        max_lat=request.max_lat,
        min_lon=request.min_lon,
        max_lon=request.max_lon,
        signal_type=request.signal_type,
        operator=request.operator
    )
    
    return [HeatmapDataPoint(**point) for point in data]


@router.post("/coverage-stats", response_model=CoverageStatistics)
async def get_coverage_statistics(
    min_lat: float = Query(..., ge=-90, le=90),
    max_lat: float = Query(..., ge=-90, le=90),
    min_lon: float = Query(..., ge=-180, le=180),
    max_lon: float = Query(..., ge=-180, le=180),
    operator: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get coverage statistics for an area.
    
    Args:
        min_lat, max_lat: Latitude bounds
        min_lon, max_lon: Longitude bounds
        operator: Optional operator filter
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Coverage statistics
    """
    area_bounds = {
        "min_lat": min_lat,
        "max_lat": max_lat,
        "min_lon": min_lon,
        "max_lon": max_lon
    }
    
    stats = signal_analyzer.calculate_coverage_statistics(
        db=db,
        area_bounds=area_bounds,
        operator=operator
    )
    
    return CoverageStatistics(**stats)

