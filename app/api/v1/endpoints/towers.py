"""Tower/cell site endpoints"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_superuser, get_current_user_optional
from app.models.user import User
from app.models.tower import Tower
from app.schemas.tower import (
    TowerCreate,
    TowerUpdate,
    TowerResponse,
    TowerSearchRequest
)
from app.services.tower_service import tower_service
from app.integrations.opencellid import opencellid_client

router = APIRouter()


@router.get("/nearby", response_model=List[TowerResponse])
async def get_nearby_towers(
    latitude: float = Query(..., description="Latitude"),
    longitude: float = Query(..., description="Longitude"),
    radius_km: float = Query(5.0, gt=0, le=50, description="Radius in kilometers"),
    operator: Optional[str] = Query(None, description="Operator filter (optional)"),
    technology: Optional[str] = Query(None, description="Technology filter (optional)"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Get towers nearby a location from local CSV database.
    
    Busca torres próximas usando o arquivo CSV local do OpenCellID (~41k torres brasileiras).
    Não requer autenticação.
    
    Args:
        latitude: User latitude
        longitude: User longitude
        radius_km: Search radius in kilometers (default 5, max 50)
        operator: Filter by operator (optional)
        technology: Filter by technology (optional)
        current_user: Current authenticated user (optional)
        db: Database session
        
    Returns:
        List of nearby towers with distance
    """
    # Get towers from CSV
    csv_towers = opencellid_client.get_real_towers_fallback(
        latitude=latitude,
        longitude=longitude,
        radius_km=radius_km
    )
    
    if not csv_towers:
        return []
    
    # Filter by operator or technology if requested
    filtered_towers = []
    for tower_data in csv_towers:
        # Apply filters
        if operator and tower_data.get("operator") != operator:
            continue
        if technology and tower_data.get("technology") != technology:
            continue
        
        # Check if tower exists in database, if not create it
        existing_tower = db.query(Tower).filter(
            Tower.cell_id == tower_data.get("cellid")
        ).first()
        
        if existing_tower:
            # Add distance info
            existing_tower.distance_km = tower_data.get("distance", 0)
            filtered_towers.append(existing_tower)
        else:
            # Create temporary tower object for response
            new_tower = Tower(
                latitude=float(tower_data.get("lat")),
                longitude=float(tower_data.get("lon")),
                operator=tower_data.get("operator", "Unknown"),
                cell_id=str(tower_data.get("cellid")),
                technology=tower_data.get("technology", "Unknown"),
                opencellid_id=str(tower_data.get("cellid")),
            )
            new_tower.distance_km = tower_data.get("distance", 0)
            filtered_towers.append(new_tower)
    
    return filtered_towers


@router.post("", response_model=TowerResponse, status_code=status.HTTP_201_CREATED)
async def create_tower(
    tower_data: TowerCreate,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
):
    """
    Create a new tower (superuser only).
    
    Args:
        tower_data: Tower data
        current_user: Current authenticated superuser
        db: Database session
        
    Returns:
        Created tower
    """
    # Check if cell_id already exists
    existing = db.query(Tower).filter(Tower.cell_id == tower_data.cell_id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tower with this cell_id already exists"
        )
    
    new_tower = Tower(**tower_data.model_dump())
    db.add(new_tower)
    db.commit()
    db.refresh(new_tower)
    
    return new_tower


@router.get("", response_model=List[TowerResponse])
async def list_towers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    operator: Optional[str] = None,
    technology: Optional[str] = None,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    List towers. Public endpoint (auth optional).
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return (default 100, max 1000)
        operator: Filter by operator
        technology: Filter by technology
        current_user: Current authenticated user (optional)
        db: Database session
        
    Returns:
        List of towers
    """
    query = db.query(Tower)
    
    if operator:
        query = query.filter(Tower.operator == operator)
    if technology:
        query = query.filter(Tower.technology == technology)
    
    towers = query.offset(skip).limit(limit).all()
    return towers


@router.get("/{tower_id}", response_model=TowerResponse)
async def get_tower(
    tower_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get tower by ID.
    
    Args:
        tower_id: Tower ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Tower data
    """
    tower = db.query(Tower).filter(Tower.id == tower_id).first()
    if not tower:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tower not found"
        )
    return tower


@router.put("/{tower_id}", response_model=TowerResponse)
async def update_tower(
    tower_id: int,
    tower_update: TowerUpdate,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
):
    """
    Update tower (superuser only).
    
    Args:
        tower_id: Tower ID
        tower_update: Tower update data
        current_user: Current authenticated superuser
        db: Database session
        
    Returns:
        Updated tower
    """
    tower = db.query(Tower).filter(Tower.id == tower_id).first()
    if not tower:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tower not found"
        )
    
    # Update fields
    update_data = tower_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(tower, field, value)
    
    db.commit()
    db.refresh(tower)
    
    return tower


@router.delete("/{tower_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tower(
    tower_id: int,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
):
    """
    Delete tower (superuser only).
    
    Args:
        tower_id: Tower ID
        current_user: Current authenticated superuser
        db: Database session
    """
    tower = db.query(Tower).filter(Tower.id == tower_id).first()
    if not tower:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tower not found"
        )
    
    db.delete(tower)
    db.commit()


@router.post("/search", response_model=List[TowerResponse])
async def search_nearby_towers(
    search: TowerSearchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Search for nearby towers.
    
    Args:
        search: Search parameters
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List of nearby towers with distance
    """
    towers = tower_service.find_nearby_towers(
        db=db,
        latitude=search.latitude,
        longitude=search.longitude,
        radius_km=search.radius_km,
        operator=search.operator,
        technology=search.technology
    )
    
    return towers

