"""Report database model"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Report(Base):
    """Report model for storing generated analysis reports"""
    
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    title = Column(String, nullable=False)
    description = Column(Text)
    report_type = Column(String, nullable=False, index=True)  # signal_map, coverage, link_budget, etc
    
    # Data
    data = Column(JSON, nullable=False)  # Store report data as JSON
    
    # Files
    pdf_path = Column(String, nullable=True)
    csv_path = Column(String, nullable=True)
    
    # Status
    status = Column(String, default="completed")  # pending, processing, completed, failed
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", backref="reports")
    
    def __repr__(self):
        return f"<Report(id={self.id}, title='{self.title}', type='{self.report_type}')>"

