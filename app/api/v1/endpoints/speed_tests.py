"""Speed test endpoints"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.speed_test import SpeedTest
from app.schemas.speed_test import (
    SpeedTestCreate,
    SpeedTestUpdate,
    SpeedTestResponse,
    SpeedTestStatistics
)

router = APIRouter()


@router.post("", response_model=SpeedTestResponse, status_code=status.HTTP_201_CREATED)
async def create_speed_test(
    speed_test: SpeedTestCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new speed test result.
    
    Args:
        speed_test: Speed test data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Created speed test
    """
    new_test = SpeedTest(
        user_id=current_user.id,
        **speed_test.model_dump()
    )
    
    db.add(new_test)
    db.commit()
    db.refresh(new_test)
    
    return new_test


@router.get("", response_model=List[SpeedTestResponse])
async def list_speed_tests(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=1000),
    connection_type: Optional[str] = None,
    operator: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List speed tests for current user.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        connection_type: Filter by connection type
        operator: Filter by operator
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List of speed tests
    """
    query = db.query(SpeedTest).filter(SpeedTest.user_id == current_user.id)
    
    if connection_type:
        query = query.filter(SpeedTest.connection_type == connection_type)
    if operator:
        query = query.filter(SpeedTest.operator == operator)
    
    tests = query.order_by(
        SpeedTest.tested_at.desc()
    ).offset(skip).limit(limit).all()
    
    return tests


@router.get("/{test_id}", response_model=SpeedTestResponse)
async def get_speed_test(
    test_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get speed test by ID.
    
    Args:
        test_id: Speed test ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Speed test data
    """
    test = db.query(SpeedTest).filter(
        SpeedTest.id == test_id,
        SpeedTest.user_id == current_user.id
    ).first()
    
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Speed test not found"
        )
    
    return test


@router.put("/{test_id}", response_model=SpeedTestResponse)
async def update_speed_test(
    test_id: int,
    test_update: SpeedTestUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update speed test.
    
    Args:
        test_id: Speed test ID
        test_update: Speed test update data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Updated speed test
    """
    test = db.query(SpeedTest).filter(
        SpeedTest.id == test_id,
        SpeedTest.user_id == current_user.id
    ).first()
    
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Speed test not found"
        )
    
    # Update fields
    update_data = test_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(test, field, value)
    
    db.commit()
    db.refresh(test)
    
    return test


@router.delete("/{test_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_speed_test(
    test_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete speed test.
    
    Args:
        test_id: Speed test ID
        current_user: Current authenticated user
        db: Database session
    """
    test = db.query(SpeedTest).filter(
        SpeedTest.id == test_id,
        SpeedTest.user_id == current_user.id
    ).first()
    
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Speed test not found"
        )
    
    db.delete(test)
    db.commit()


@router.get("/statistics/summary", response_model=SpeedTestStatistics)
async def get_speed_test_statistics(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get speed test statistics for user.
    
    Args:
        days: Number of days to analyze
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Speed test statistics
    """
    from sqlalchemy import func
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    tests = db.query(SpeedTest).filter(
        SpeedTest.user_id == current_user.id,
        SpeedTest.tested_at >= start_date
    ).all()
    
    if not tests:
        return SpeedTestStatistics(
            total_tests=0,
            avg_download_mbps=0,
            avg_upload_mbps=0,
            avg_ping_ms=0,
            max_download_mbps=0,
            max_upload_mbps=0,
            min_ping_ms=0,
            by_connection_type={}
        )
    
    # Calculate statistics
    downloads = [t.download_mbps for t in tests]
    uploads = [t.upload_mbps for t in tests]
    pings = [t.ping_ms for t in tests]
    
    # Group by connection type
    by_type = {}
    for test in tests:
        conn_type = test.connection_type or "unknown"
        if conn_type not in by_type:
            by_type[conn_type] = {
                "count": 0,
                "avg_download": 0,
                "avg_upload": 0,
                "avg_ping": 0
            }
        by_type[conn_type]["count"] += 1
    
    # Calculate averages by type
    for conn_type in by_type:
        type_tests = [t for t in tests if (t.connection_type or "unknown") == conn_type]
        by_type[conn_type]["avg_download"] = round(
            sum(t.download_mbps for t in type_tests) / len(type_tests), 2
        )
        by_type[conn_type]["avg_upload"] = round(
            sum(t.upload_mbps for t in type_tests) / len(type_tests), 2
        )
        by_type[conn_type]["avg_ping"] = round(
            sum(t.ping_ms for t in type_tests) / len(type_tests), 2
        )
    
    return SpeedTestStatistics(
        total_tests=len(tests),
        avg_download_mbps=round(sum(downloads) / len(downloads), 2),
        avg_upload_mbps=round(sum(uploads) / len(uploads), 2),
        avg_ping_ms=round(sum(pings) / len(pings), 2),
        max_download_mbps=round(max(downloads), 2),
        max_upload_mbps=round(max(uploads), 2),
        min_ping_ms=round(min(pings), 2),
        by_connection_type=by_type
    )

