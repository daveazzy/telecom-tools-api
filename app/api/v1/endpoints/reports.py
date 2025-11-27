"""Report generation endpoints"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.report import Report
from app.schemas.report import (
    ReportCreate,
    ReportUpdate,
    ReportResponse,
    ReportGenerateRequest
)
from app.services.report_generator import report_generator

router = APIRouter()


@router.post("", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def create_report(
    report_data: ReportCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new report.
    
    Args:
        report_data: Report data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Created report
    """
    new_report = Report(
        user_id=current_user.id,
        title=report_data.title,
        description=report_data.description,
        report_type=report_data.report_type,
        data=report_data.data,
        status="completed"
    )
    
    db.add(new_report)
    db.commit()
    db.refresh(new_report)
    
    return new_report


@router.get("", response_model=List[ReportResponse])
async def list_reports(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=1000),
    report_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List reports for current user.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        report_type: Filter by report type
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List of reports
    """
    query = db.query(Report).filter(Report.user_id == current_user.id)
    
    if report_type:
        query = query.filter(Report.report_type == report_type)
    
    reports = query.order_by(
        Report.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    return reports


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get report by ID.
    
    Args:
        report_id: Report ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Report data
    """
    report = db.query(Report).filter(
        Report.id == report_id,
        Report.user_id == current_user.id
    ).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    return report


@router.put("/{report_id}", response_model=ReportResponse)
async def update_report(
    report_id: int,
    report_update: ReportUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update report.
    
    Args:
        report_id: Report ID
        report_update: Report update data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Updated report
    """
    report = db.query(Report).filter(
        Report.id == report_id,
        Report.user_id == current_user.id
    ).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Update fields
    update_data = report_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(report, field, value)
    
    db.commit()
    db.refresh(report)
    
    return report


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete report.
    
    Args:
        report_id: Report ID
        current_user: Current authenticated user
        db: Database session
    """
    report = db.query(Report).filter(
        Report.id == report_id,
        Report.user_id == current_user.id
    ).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    db.delete(report)
    db.commit()


@router.post("/generate", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def generate_report(
    request: ReportGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate a new report with specified parameters.
    
    Args:
        request: Report generation request
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Generated report
    """
    # Generate report data based on type
    report_data = {
        "report_type": request.report_type,
        "parameters": request.parameters,
        "generated_by": current_user.username
    }
    
    # Create report summary
    summary = report_generator.generate_summary(report_data)
    
    new_report = Report(
        user_id=current_user.id,
        title=request.title,
        description=request.description or summary,
        report_type=request.report_type,
        data=report_data,
        status="completed"
    )
    
    db.add(new_report)
    db.commit()
    db.refresh(new_report)
    
    return new_report

