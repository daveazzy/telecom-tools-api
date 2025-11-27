"""OpenCellID CSV integration endpoints"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List, Dict
from sqlalchemy.orm import Session
import logging

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.integrations.opencellid import opencellid_client
from app.models.tower import Tower

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/import")
async def import_opencellid(
    lat: float = Query(..., description="Latitude"),
    lng: float = Query(..., description="Longitude"),
    radius_km: float = Query(5.0, gt=0, le=50, description="Radius in kilometers"),
    operator: Optional[str] = Query(None, description="Operator filter (optional)"),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Import towers from local CSV database around a point and save to database.
    
    Uses the local 724.csv (OpenCellID open data) with ~41k Brazilian towers.
    
    Returns: 
        { imported_count, towers: [{lat,lng,operator,signal_type}], source: 'csv' }
    """
    logger.info(f"📍 Importing nearby towers: lat={lat}, lng={lng}, radius={radius_km}km")
    
    # Get towers from CSV
    cells = opencellid_client.get_real_towers_fallback(
        latitude=lat,
        longitude=lng,
        radius_km=radius_km
    )
    
    if not cells:
        logger.warning(f"❌ No towers found in CSV for location")
        raise HTTPException(status_code=404, detail="No towers found in the specified area")

    logger.info(f"✅ CSV found {len(cells)} nearby towers")
    
    imported = []
    errors = 0

    # Batch check existing cell ids to avoid duplicates
    incoming_ids = set()
    for c in cells:
        cid = str(c.get("cellid") or c.get("cell_id") or "")
        if cid:
            incoming_ids.add(cid)

    existing_towers = []
    if incoming_ids:
        existing_towers = db.query(Tower).filter(
            (Tower.opencellid_id.in_(list(incoming_ids))) | (Tower.cell_id.in_(list(incoming_ids)))
        ).all()

    existing_ids = set()
    for t in existing_towers:
        ocid = getattr(t, 'opencellid_id', None)
        cid = getattr(t, 'cell_id', None)
        if ocid is not None and ocid != "":
            existing_ids.add(ocid)
        if cid is not None and cid != "":
            existing_ids.add(cid)

    logger.info(f"📊 {len(existing_ids)} towers already exist in database")

    for c in cells:
        # Normalize fields from CSV
        cellid = str(c.get("cellid") or c.get("cell_id") or "")
        lat_c = c.get("lat") or c.get("latitude")
        lon_c = c.get("lon") or c.get("longitude")
        radio = (c.get("radio") or c.get("technology") or "").upper()
        tower_operator = c.get("operator") or "Unknown"

        if not cellid or lat_c is None or lon_c is None:
            continue

        # Skip if already exists
        if cellid in existing_ids:
            continue

        # Map technology
        tech = None
        if "LTE" in radio or "4G" in radio:
            tech = "4G"
        elif "NR" in radio or "5G" in radio:
            tech = "5G"
        elif "UMTS" in radio or "3G" in radio:
            tech = "3G"
        elif "GSM" in radio:
            tech = "2G"
        elif radio:
            tech = radio

        # Filter by operator if requested
        if operator and operator != 'all' and tower_operator != operator:
            continue

        tower = Tower(
            latitude=float(lat_c),
            longitude=float(lon_c),
            operator=tower_operator,
            cell_id=cellid,
            technology=tech,
            opencellid_id=cellid,
        )

        try:
            db.add(tower)
            db.commit()
            db.refresh(tower)

            imported.append({
                "lat": tower.latitude,
                "lng": tower.longitude,
                "operator": tower.operator,
                "signal_type": tower.technology,
                "distance_km": c.get("distance", 0),
            })
            existing_ids.add(cellid)
            logger.debug(f"✅ Tower {cellid} ({tower_operator}) imported successfully")
        except Exception as e:
            db.rollback()
            errors += 1
            logger.debug(f"❌ Error inserting tower {cellid}: {str(e)}")
            continue

    logger.info(f"🎉 Import completed: {len(imported)} towers inserted, {errors} errors")

    result = {
        "imported_count": len(imported),
        "towers": imported,
        "is_mock": False,
        "source": "opencellid_csv_724",
        "note": "✅ Using REAL data from CSV file (41k Brazilian towers)",
        "errors": errors,
        "total_found": len(cells),
    }

    return result
