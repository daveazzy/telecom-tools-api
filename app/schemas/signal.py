"""Signal measurement Pydantic schemas"""

from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, List


class SignalMeasurementBase(BaseModel):
    """Base signal measurement schema"""
    latitude: float = Field(..., ge=-90, le=90, description="Latitude in decimal degrees")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude in decimal degrees")
    altitude: Optional[float] = Field(None, description="Altitude in meters")
    signal_type: str = Field(..., description="Signal type: 4g, 5g, or wifi")
    operator: Optional[str] = Field(None, description="Network operator name")
    signal_strength_dbm: float = Field(..., ge=-120, le=0, description="Signal strength in dBm")
    signal_quality: Optional[int] = Field(None, ge=0, le=100, description="Signal quality percentage")
    frequency_mhz: Optional[float] = Field(None, gt=0, description="Frequency in MHz")
    technology: Optional[str] = Field(None, description="Technology: LTE, NR, etc")
    cell_id: Optional[str] = Field(None, description="Cell ID")


class SignalMeasurementCreate(SignalMeasurementBase):
    """Schema for creating a signal measurement"""
    measured_at: datetime = Field(..., description="Timestamp of measurement")


class SignalMeasurementUpdate(BaseModel):
    """Schema for updating a signal measurement"""
    signal_strength_dbm: Optional[float] = Field(None, ge=-120, le=0)
    signal_quality: Optional[int] = Field(None, ge=0, le=100)
    operator: Optional[str] = None


class SignalMeasurementResponse(SignalMeasurementBase):
    """Schema for signal measurement response"""
    id: int
    user_id: int
    measured_at: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


class SignalHeatmapRequest(BaseModel):
    """Schema for requesting heatmap data"""
    min_lat: float = Field(..., ge=-90, le=90)
    max_lat: float = Field(..., ge=-90, le=90)
    min_lon: float = Field(..., ge=-180, le=180)
    max_lon: float = Field(..., ge=-180, le=180)
    signal_type: Optional[str] = None
    operator: Optional[str] = None
    
    @validator('max_lat')
    def validate_latitude_range(cls, v, values):
        if 'min_lat' in values and v <= values['min_lat']:
            raise ValueError('max_lat must be greater than min_lat')
        return v
    
    @validator('max_lon')
    def validate_longitude_range(cls, v, values):
        if 'min_lon' in values and v <= values['min_lon']:
            raise ValueError('max_lon must be greater than min_lon')
        return v


class HeatmapDataPoint(BaseModel):
    """Single heatmap data point"""
    lat: float
    lon: float
    signal_dbm: float
    quality: Optional[int]
    operator: Optional[str]


class SignalHeatmapResponse(BaseModel):
    """Schema for heatmap response"""
    data_points: List[HeatmapDataPoint]
    total_points: int
    bounds: dict


class CoverageStatistics(BaseModel):
    """Coverage statistics schema"""
    total_measurements: int
    average_signal_dbm: Optional[float]
    median_signal_dbm: Optional[float]
    min_signal_dbm: Optional[float]
    max_signal_dbm: Optional[float]
    std_deviation: Optional[float]
    coverage_percentage: float
    good_signal_count: int
    poor_signal_count: int


class CoverageGridPoint(BaseModel):
    """Single grid point for coverage analysis"""
    lat: float
    lng: float
    signal_dbm: float
    quality: str  # "excellent", "good", "fair", "poor"


class CoverageAnalysisRequest(BaseModel):
    """Request for coverage heatmap analysis"""
    polygon: List[List[float]] = Field(..., description="Polygon coordinates: [[lat, lng], ...]")
    operator: Optional[str] = Field(None, description="Operator filter (e.g., 'TIM', 'VIVO')")
    threshold_dbm: float = Field(-85, ge=-120, le=0, description="Signal threshold for coverage")


class CoverageAnalysisResponse(BaseModel):
    """Response from coverage heatmap analysis"""
    grid: List[CoverageGridPoint] = Field(..., description="Grid points with signal values")
    stats: dict = Field(..., description="Statistics: coverage_pct, gap_area_km2, total_area_km2")
    
    class Config:
        from_attributes = True