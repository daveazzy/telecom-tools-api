"""RF calculation Pydantic schemas"""

from pydantic import BaseModel, Field
from typing import Optional


class LinkBudgetRequest(BaseModel):
    """Schema for link budget calculation request"""
    tx_power_dbm: float = Field(..., description="Transmit power in dBm")
    tx_gain_dbi: float = Field(..., description="Transmit antenna gain in dBi")
    rx_gain_dbi: float = Field(..., description="Receive antenna gain in dBi")
    frequency_mhz: float = Field(..., gt=0, description="Frequency in MHz")
    distance_km: float = Field(..., gt=0, description="Distance in kilometers")
    additional_losses_db: Optional[float] = Field(0, description="Additional losses in dB")
    rx_sensitivity_dbm: Optional[float] = Field(-100, description="Receiver sensitivity in dBm")


class LinkBudgetResponse(BaseModel):
    """Schema for link budget calculation response"""
    received_power_dbm: float
    path_loss_db: float
    free_space_loss_db: float
    eirp_dbm: float
    total_gain_db: float
    link_margin_db: float
    is_viable: bool
    fade_margin_db: float


class PathLossRequest(BaseModel):
    """Schema for path loss calculation request"""
    frequency_mhz: float = Field(..., gt=0, description="Frequency in MHz")
    distance_km: float = Field(..., gt=0, description="Distance in kilometers")
    tx_height_m: float = Field(30, gt=0, description="Transmitter height in meters")
    rx_height_m: float = Field(1.5, gt=0, description="Receiver height in meters")
    environment: str = Field("urban", description="Environment: urban, suburban, or rural")


class PathLossResponse(BaseModel):
    """Schema for path loss calculation response"""
    path_loss_db: float
    model_used: str
    parameters: dict


class FresnelZoneRequest(BaseModel):
    """Schema for Fresnel zone calculation request"""
    distance_km: float = Field(..., gt=0, description="Distance in kilometers")
    frequency_mhz: float = Field(..., gt=0, description="Frequency in MHz")
    zone_number: int = Field(1, ge=1, le=10, description="Fresnel zone number")


class FresnelZoneResponse(BaseModel):
    """Schema for Fresnel zone calculation response"""
    radius_m: float
    zone_number: int
    frequency_mhz: float
    distance_km: float
    wavelength_m: float


class PowerConversionRequest(BaseModel):
    """Schema for power unit conversion request"""
    value: float
    from_unit: str = Field(..., description="Source unit: dbm, watts, mw")
    to_unit: str = Field(..., description="Target unit: dbm, watts, mw")


class PowerConversionResponse(BaseModel):
    """Schema for power unit conversion response"""
    input_value: float
    input_unit: str
    output_value: float
    output_unit: str


class AntennaGainRequest(BaseModel):
    """Schema for antenna gain calculation"""
    frequency_mhz: float = Field(..., gt=0)
    antenna_diameter_m: Optional[float] = Field(None, gt=0)
    efficiency: float = Field(0.6, ge=0, le=1, description="Antenna efficiency (0-1)")


class AntennaGainResponse(BaseModel):
    """Schema for antenna gain response"""
    gain_dbi: float
    gain_db: float
    beamwidth_degrees: Optional[float]
    wavelength_m: float

