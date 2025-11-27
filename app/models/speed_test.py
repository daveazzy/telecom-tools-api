"""Speed test database model"""

from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class SpeedTest(Base):
    """Speed test model for storing network speed test results"""
    
    __tablename__ = "speed_tests"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Location
    latitude = Column(Float, index=True)
    longitude = Column(Float, index=True)
    
    # Results
    download_mbps = Column(Float, nullable=False)
    upload_mbps = Column(Float, nullable=False)
    ping_ms = Column(Float, nullable=False)
    jitter_ms = Column(Float, nullable=True)
    packet_loss_percent = Column(Float, nullable=True)
    
    # Connection info
    connection_type = Column(String, index=True)  # wifi, 4g, 5g
    isp = Column(String, index=True)
    server_location = Column(String)
    
    # Network details
    signal_strength_dbm = Column(Float, nullable=True)
    operator = Column(String, nullable=True, index=True)
    
    # Metadata
    tested_at = Column(DateTime(timezone=True), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", backref="speed_tests")
    
    def __repr__(self):
        return (f"<SpeedTest(id={self.id}, download={self.download_mbps}Mbps, "
                f"upload={self.upload_mbps}Mbps)>")

