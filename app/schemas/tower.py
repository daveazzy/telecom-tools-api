"""Tower Pydantic schemas"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class TowerBase(BaseModel):
    """Base tower schema"""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    altitude: Optional[float] = None
    operator: str = Field(..., min_length=1)
    cell_id: str = Field(..., min_length=1)
    technology: Optional[str] = None
    frequency_mhz: Optional[float] = Field(None, gt=0)
    address: Optional[str] = None
    coverage_radius_km: Optional[float] = Field(None, gt=0)


class TowerCreate(TowerBase):
    """Schema for creating a tower"""
    opencellid_id: Optional[str] = None
    anatel_code: Optional[str] = None


class TowerUpdate(BaseModel):
    """Schema for updating a tower"""
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    altitude: Optional[float] = None
    operator: Optional[str] = None
    technology: Optional[str] = None
    frequency_mhz: Optional[float] = Field(None, gt=0)
    address: Optional[str] = None
    coverage_radius_km: Optional[float] = Field(None, gt=0)


class TowerResponse(TowerBase):
    """Schema for tower response"""
    id: int
    opencellid_id: Optional[str]
    anatel_code: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    distance_km: Optional[float] = None
    
    class Config:
        from_attributes = True


class TowerSearchRequest(BaseModel):
    """Schema for searching towers"""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    radius_km: float = Field(5.0, gt=0, le=50, description="Search radius in kilometers")
    operator: Optional[str] = None
    technology: Optional[str] = None

