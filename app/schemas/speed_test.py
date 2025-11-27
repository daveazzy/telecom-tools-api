"""Speed test Pydantic schemas"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class SpeedTestBase(BaseModel):
    """Base speed test schema"""
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    download_mbps: float = Field(..., ge=0, description="Download speed in Mbps")
    upload_mbps: float = Field(..., ge=0, description="Upload speed in Mbps")
    ping_ms: float = Field(..., ge=0, description="Ping in milliseconds")
    jitter_ms: Optional[float] = Field(None, ge=0, description="Jitter in milliseconds")
    packet_loss_percent: Optional[float] = Field(None, ge=0, le=100, description="Packet loss percentage")
    connection_type: Optional[str] = Field(None, description="Connection type: wifi, 4g, 5g")
    isp: Optional[str] = Field(None, description="Internet Service Provider")
    server_location: Optional[str] = Field(None, description="Test server location")


class SpeedTestCreate(SpeedTestBase):
    """Schema for creating a speed test result"""
    tested_at: datetime = Field(..., description="Timestamp of test")
    signal_strength_dbm: Optional[float] = Field(None, ge=-120, le=0)
    operator: Optional[str] = None


class SpeedTestUpdate(BaseModel):
    """Schema for updating a speed test"""
    connection_type: Optional[str] = None
    isp: Optional[str] = None
    operator: Optional[str] = None


class SpeedTestResponse(SpeedTestBase):
    """Schema for speed test response"""
    id: int
    user_id: int
    signal_strength_dbm: Optional[float]
    operator: Optional[str]
    tested_at: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


class SpeedTestStatistics(BaseModel):
    """Speed test statistics schema"""
    total_tests: int
    avg_download_mbps: float
    avg_upload_mbps: float
    avg_ping_ms: float
    max_download_mbps: float
    max_upload_mbps: float
    min_ping_ms: float
    by_connection_type: dict

