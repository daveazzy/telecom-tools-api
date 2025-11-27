"""Tower/cell site database model"""

from sqlalchemy import Column, Integer, Float, String, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class Tower(Base):
    """Tower/cell site model for storing cell tower information"""
    
    __tablename__ = "towers"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Location
    latitude = Column(Float, nullable=False, index=True)
    longitude = Column(Float, nullable=False, index=True)
    altitude = Column(Float, nullable=True)
    
    # Tower info
    operator = Column(String, nullable=False, index=True)
    cell_id = Column(String, unique=True, index=True)
    technology = Column(String)  # 4G, 5G, etc
    frequency_mhz = Column(Float)
    
    # External IDs
    opencellid_id = Column(String, nullable=True, unique=True)
    anatel_code = Column(String, nullable=True)
    
    # Additional info
    address = Column(String, nullable=True)
    coverage_radius_km = Column(Float, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return (f"<Tower(id={self.id}, operator='{self.operator}', "
                f"cell_id='{self.cell_id}')>")

