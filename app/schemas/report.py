"""Report Pydantic schemas"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Any


class ReportBase(BaseModel):
    """Base report schema"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    report_type: str = Field(..., description="Type: signal_map, coverage, link_budget, etc")


class ReportCreate(ReportBase):
    """Schema for creating a report"""
    data: dict = Field(..., description="Report data as JSON")


class ReportUpdate(BaseModel):
    """Schema for updating a report"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[str] = None


class ReportResponse(ReportBase):
    """Schema for report response"""
    id: int
    user_id: int
    data: dict
    pdf_path: Optional[str]
    csv_path: Optional[str]
    status: str
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class ReportGenerateRequest(BaseModel):
    """Schema for generating a new report"""
    title: str
    report_type: str
    description: Optional[str] = None
    parameters: dict = Field(..., description="Report-specific parameters")
    generate_pdf: bool = Field(True, description="Generate PDF file")
    generate_csv: bool = Field(False, description="Generate CSV file")

