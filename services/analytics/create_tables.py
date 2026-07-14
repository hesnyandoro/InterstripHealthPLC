"""
Quick local-dev bootstrap: creates tables directly from the SQLAlchemy models.
Replace with Alembic migrations before this service holds real data — see the
same note in services/auth/create_tables.py.
"""

from app.db import Base, engine
from app.models import BedSnapshot, Facility  # noqa: F401

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("analytics tables created")
