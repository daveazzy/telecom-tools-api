"""Schemas for tower recommendation endpoints"""

from pydantic import BaseModel, Field
from typing import List, Dict, Literal


class GapZoneRequest(BaseModel):
    """Represents a coverage gap area from heatmap analysis"""
    latitude: float = Field(..., description="Latitude of gap center")
    longitude: float = Field(..., description="Longitude of gap center")
    area_km2: float = Field(..., description="Area of gap in km²")


class RecommendationRequest(BaseModel):
    """Request for tower recommendations"""
    gaps: List[GapZoneRequest] = Field(
        ...,
        description="List of coverage gaps to analyze"
    )
    operator: str = Field(
        default="all",
        description="Filter by operator (e.g., 'Claro', 'Vivo', 'TIM', 'all')"
    )
    max_recommendations: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Maximum number of recommendations to return"
    )


class RecommendationLocation(BaseModel):
    """Location of recommended tower"""
    latitude: float = Field(..., description="Latitude")
    longitude: float = Field(..., description="Longitude")


class RecommendationItem(BaseModel):
    """Single tower recommendation"""
    location: RecommendationLocation
    score: float = Field(..., description="Recommendation score (0-10)")
    priority: Literal["high", "medium", "low"] = Field(
        ...,
        description="Priority level: high (>5), medium (2-5), low (<2)"
    )
    population_reached: int = Field(
        ...,
        description="Estimated population that would be served"
    )
    reason: str = Field(..., description="Reason for recommendation")
    gap_count: int = Field(..., description="Number of gaps in this cluster")


class RecommendationResponse(BaseModel):
    """Response with tower recommendations"""
    recommendations: List[RecommendationItem]
    total_gaps_analyzed: int = Field(..., description="Total number of gaps analyzed")
    clusters_found: int = Field(..., description="Number of clusters found")
    analysis_metadata: Dict = Field(
        default_factory=dict,
        description="Additional analysis metadata"
    )
