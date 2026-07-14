from datetime import date

from pydantic import BaseModel
from sqlalchemy import Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db import Base

# --- SQLAlchemy ORM models -------------------------------------------------


class Facility(Base):
    __tablename__ = "facilities"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(String, index=True, nullable=False)  # tenant scoping
    name = Column(String, nullable=False)
    county = Column(String, nullable=False)
    bed_capacity = Column(Integer, nullable=False)

    snapshots = relationship("BedSnapshot", back_populates="facility")


class BedSnapshot(Base):
    __tablename__ = "bed_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    facility_id = Column(Integer, ForeignKey("facilities.id"), nullable=False)
    snapshot_date = Column(Date, nullable=False)
    beds_occupied = Column(Integer, nullable=False)

    facility = relationship("Facility", back_populates="snapshots")


# --- Pydantic schemas (API request/response) -------------------------------


class FacilityOut(BaseModel):
    id: int
    name: str
    county: str
    bed_capacity: int

    class Config:
        from_attributes = True


class BedSnapshotOut(BaseModel):
    snapshot_date: date
    beds_occupied: int
    bed_capacity: int
    occupancy_rate: float

    class Config:
        from_attributes = True
