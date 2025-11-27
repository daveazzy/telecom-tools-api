"""Signal measurement database model"""

from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base


class SignalType(str, enum.Enum):
    """Signal type enumeration"""
    CELLULAR_4G = "4g"
    CELLULAR_5G = "5g"
    WIFI = "wifi"


class SignalMeasurement(Base):
    """Signal measurement model for storing RF measurements"""
    
    __tablename__ = "signal_measurements"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Location
    latitude = Column(Float, nullable=False, index=True)
    longitude = Column(Float, nullable=False, index=True)
    altitude = Column(Float, nullable=True)
    
    # Signal data
    signal_type = Column(Enum(SignalType), nullable=False)
    operator = Column(String, nullable=True, index=True)
    signal_strength_dbm = Column(Float, nullable=False)
    signal_quality = Column(Integer, nullable=True)  # 0-100
    frequency_mhz = Column(Float, nullable=True)
    
    # Network info
    technology = Column(String, nullable=True)  # LTE, NR, etc
    cell_id = Column(String, nullable=True, index=True)
    
    # Metadata
    measured_at = Column(DateTime(timezone=True), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", backref="measurements")
    
    def __repr__(self):
        return (f"<SignalMeasurement(id={self.id}, operator='{self.operator}', "
                f"signal={self.signal_strength_dbm}dBm)>")

