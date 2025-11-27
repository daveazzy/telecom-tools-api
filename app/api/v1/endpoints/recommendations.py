"""
Tower Recommendations API Endpoint
Provides strategic tower placement recommendations based on coverage gaps
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional

from app.schemas.recommendation import (
    RecommendationRequest,
    RecommendationResponse,
    RecommendationItem,
    RecommendationLocation,
    GapZoneRequest
)
from app.services.recommendation_engine import (
    RecommendationEngine,
    GapZone,
)


router = APIRouter(
    prefix="/recommendations",
    tags=["recommendations"]
)


@router.post(
    "/towers",
    response_model=RecommendationResponse,
    summary="Generate tower placement recommendations",
    description="Analyze coverage gaps and generate strategic tower placement recommendations"
)
async def get_tower_recommendations(
    request: RecommendationRequest
):
    """
    Generate tower placement recommendations based on coverage gaps
    
    **Request:**
    - `gaps`: List of coverage gaps (latitude, longitude, area_km²)
    - `operator`: Filter by operator (optional, default: 'all')
    - `max_recommendations`: Maximum recommendations to return (1-20, default: 5)
    
    **Response:**
    - `recommendations`: List of recommended tower placements with scores and priority
    - `total_gaps_analyzed`: Total number of gaps analyzed
    - `clusters_found`: Number of clusters created from gaps
    
    **Priority Levels:**
    - `high`: Score > 5 (covers large gaps with more affected area)
    - `medium`: Score 2-5 (moderate coverage impact)
    - `low`: Score < 2 (small gaps with limited impact)
    
    **Example Request:**
    ```json
    {
      "gaps": [
        {"latitude": -23.551, "longitude": -46.634, "area_km2": 0.5},
        {"latitude": -23.553, "longitude": -46.633, "area_km2": 0.3}
      ],
      "max_recommendations": 5
    }
    ```
    """
    
    # Validate request
    if not request.gaps:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one gap zone is required"
        )
    
    if len(request.gaps) > 1000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 1000 gap zones allowed"
        )
    
    # Convert request to engine objects
    gaps: List[GapZone] = [
        GapZone(
            latitude=gap.latitude,
            longitude=gap.longitude,
            area_km2=gap.area_km2
        )
        for gap in request.gaps
    ]
    
    # Generate recommendations
    engine = RecommendationEngine()
    recommendations_data = engine.get_top_recommendations(
        gaps=gaps,
        count=request.max_recommendations
    )
    
    # Convert to response format
    recommendations = []
    for rec_data in recommendations_data:
        location = RecommendationLocation(
            latitude=rec_data["location"]["latitude"],
            longitude=rec_data["location"]["longitude"]
        )
        
        recommendation = RecommendationItem(
            location=location,
            score=rec_data["score"],
            priority=rec_data["priority"],
            population_reached=rec_data["population_reached"],
            reason=rec_data["reason"],
            gap_count=rec_data["gap_count"]
        )
        recommendations.append(recommendation)
    
    # Prepare metadata
    num_clusters = len(set(rec_data.get("cluster_id", i) for i, rec_data in enumerate(recommendations_data)))
    
    return RecommendationResponse(
        recommendations=recommendations,
        total_gaps_analyzed=len(request.gaps),
        clusters_found=num_clusters,
        analysis_metadata={
            "clustering_radius_km": RecommendationEngine.CLUSTERING_RADIUS_KM,
            "population_density_estimate": RecommendationEngine.POPULATION_DENSITY_PER_KM2,
            "operator_filter": request.operator,
            "algorithm": "gap_clustering_with_score_ranking"
        }
    )


@router.get(
    "/health",
    summary="Health check",
    tags=["health"]
)
async def recommendations_health():
    """Health check endpoint for recommendations service"""
    return {
        "status": "healthy",
        "service": "recommendations",
        "version": "1.0.0"
    }
