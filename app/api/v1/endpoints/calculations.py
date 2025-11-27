"""RF calculation endpoints"""

from fastapi import APIRouter, Depends
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.calculation import (
    LinkBudgetRequest,
    LinkBudgetResponse,
    PathLossRequest,
    PathLossResponse,
    FresnelZoneRequest,
    FresnelZoneResponse,
    PowerConversionRequest,
    PowerConversionResponse
)
from app.services.rf_calculations import rf_calc

router = APIRouter()


@router.post("/link-budget", response_model=LinkBudgetResponse)
async def calculate_link_budget(
    request: LinkBudgetRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Calculate link budget for a radio link.
    
    Args:
        request: Link budget parameters
        current_user: Current authenticated user
        
    Returns:
        Link budget analysis results
    """
    result = rf_calc.link_budget_analysis(
        tx_power_dbm=request.tx_power_dbm,
        tx_gain_dbi=request.tx_gain_dbi,
        rx_gain_dbi=request.rx_gain_dbi,
        frequency_mhz=request.frequency_mhz,
        distance_km=request.distance_km,
        additional_losses_db=request.additional_losses_db,
        rx_sensitivity_dbm=request.rx_sensitivity_dbm
    )
    
    return LinkBudgetResponse(**result)


@router.post("/path-loss", response_model=PathLossResponse)
async def calculate_path_loss(
    request: PathLossRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Calculate path loss using propagation models.
    
    Args:
        request: Path loss parameters
        current_user: Current authenticated user
        
    Returns:
        Path loss calculation results
    """
    # Use Okumura-Hata for typical cellular scenarios
    if request.environment in ["urban", "suburban", "rural"]:
        path_loss = rf_calc.okumura_hata_path_loss(
            frequency_mhz=request.frequency_mhz,
            distance_km=request.distance_km,
            tx_height_m=request.tx_height_m,
            rx_height_m=request.rx_height_m,
            environment=request.environment
        )
        model = "Okumura-Hata"
    else:
        # Fall back to free space
        path_loss = rf_calc.friis_path_loss(
            frequency_mhz=request.frequency_mhz,
            distance_km=request.distance_km
        )
        model = "Free Space (Friis)"
    
    return PathLossResponse(
        path_loss_db=round(path_loss, 2),
        model_used=model,
        parameters={
            "frequency_mhz": request.frequency_mhz,
            "distance_km": request.distance_km,
            "tx_height_m": request.tx_height_m,
            "rx_height_m": request.rx_height_m,
            "environment": request.environment
        }
    )


@router.post("/fresnel-zone", response_model=FresnelZoneResponse)
async def calculate_fresnel_zone(
    request: FresnelZoneRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Calculate Fresnel zone radius.
    
    Args:
        request: Fresnel zone parameters
        current_user: Current authenticated user
        
    Returns:
        Fresnel zone calculation results
    """
    radius = rf_calc.fresnel_zone_radius(
        distance_km=request.distance_km,
        frequency_mhz=request.frequency_mhz,
        zone_number=request.zone_number
    )
    
    wavelength = rf_calc.wavelength(request.frequency_mhz * 1e6)
    
    return FresnelZoneResponse(
        radius_m=round(radius, 2),
        zone_number=request.zone_number,
        frequency_mhz=request.frequency_mhz,
        distance_km=request.distance_km,
        wavelength_m=round(wavelength, 4)
    )


@router.post("/power-conversion", response_model=PowerConversionResponse)
async def convert_power_units(
    request: PowerConversionRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Convert between power units.
    
    Args:
        request: Power conversion parameters
        current_user: Current authenticated user
        
    Returns:
        Converted power value
    """
    value = request.value
    from_unit = request.from_unit.lower()
    to_unit = request.to_unit.lower()
    
    # Convert to watts first
    if from_unit == "dbm":
        watts = rf_calc.dbm_to_watts(value)
    elif from_unit == "mw":
        watts = value / 1000
    elif from_unit == "watts":
        watts = value
    else:
        watts = value
    
    # Convert from watts to target unit
    if to_unit == "dbm":
        result = rf_calc.watts_to_dbm(watts)
    elif to_unit == "mw":
        result = watts * 1000
    elif to_unit == "watts":
        result = watts
    else:
        result = watts
    
    return PowerConversionResponse(
        input_value=value,
        input_unit=from_unit,
        output_value=round(result, 6),
        output_unit=to_unit
    )

