"""
Coverage analysis endpoints - Grid-based coverage analysis with Okumura-Hata RF model
POST /api/v1/analysis/coverage-heatmap - Calculates heatmap for visualization
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user_optional
from app.models.user import User
from app.schemas.signal import CoverageAnalysisRequest, CoverageAnalysisResponse
from app.services.coverage_analysis import CoverageAnalyzer

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.post("/coverage-heatmap", response_model=CoverageAnalysisResponse)
async def analyze_coverage_heatmap(
    request: CoverageAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    """
    Analyze coverage within a polygon using grid-based approach.
    
    Grid generation: 100m spacing (0.1km default)
    RF Model: Okumura-Hata (urban) for path loss calculation
    Distance: Haversine formula
    
    Request:
        - polygon: [[lat, lng], ...] - Closed polygon vertices in order
        - operator: (optional) Filter by operator (e.g., "Vivo", "Claro")
        - threshold_dbm: (optional) Signal threshold for coverage (-85 dBm default)
    
    Response:
        - grid: Array of grid points with signal strength and quality
        - stats: Coverage statistics (%, gap area, total area, avg signal)
    """
    
    # Validate polygon
    if not request.polygon or len(request.polygon) < 3:
        raise HTTPException(
            status_code=400,
            detail="Polygon must have at least 3 vertices"
        )
    
    # Validate polygon is closed (first point should equal last)
    if (request.polygon[0][0] != request.polygon[-1][0] or 
        request.polygon[0][1] != request.polygon[-1][1]):
        # Auto-close polygon for convenience
        request.polygon.append(request.polygon[0])
    
    # Run analysis
    result = CoverageAnalyzer.analyze_coverage(
        db=db,
        polygon=request.polygon,
        operator=request.operator,
        threshold_dbm=request.threshold_dbm or -85,
        grid_step_km=0.1  # 100m grid
    )
    
    return CoverageAnalysisResponse(**result)
