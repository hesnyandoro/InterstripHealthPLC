from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import CurrentUser, get_current_user
from app.db import get_db
from app.models import BedSnapshot, BedSnapshotOut, Facility, FacilityOut

router = APIRouter()

# org scoping now comes from the verified JWT (see app/auth.py), never from a
# client-supplied org_id — a hospital user can only ever see their own org's data.


@router.get("/facilities", response_model=list[FacilityOut])
def list_facilities(db: Session = Depends(get_db), user: CurrentUser = Depends(get_current_user)):
    return db.query(Facility).filter(Facility.organization_id == user.org_id).all()


@router.get("/facilities/{facility_id}/occupancy", response_model=list[BedSnapshotOut])
def occupancy_history(
    facility_id: int, db: Session = Depends(get_db), user: CurrentUser = Depends(get_current_user)
):
    facility = (
        db.query(Facility)
        .filter(Facility.id == facility_id, Facility.organization_id == user.org_id)
        .first()
    )
    if not facility:
        raise HTTPException(status_code=404, detail="Facility not found")

    snapshots = (
        db.query(BedSnapshot)
        .filter(BedSnapshot.facility_id == facility_id)
        .order_by(BedSnapshot.snapshot_date.desc())
        .limit(90)
        .all()
    )

    return [
        BedSnapshotOut(
            snapshot_date=s.snapshot_date,
            beds_occupied=s.beds_occupied,
            bed_capacity=facility.bed_capacity,
            occupancy_rate=round(s.beds_occupied / facility.bed_capacity, 3),
        )
        for s in snapshots
    ]
