"""
Quick local-dev bootstrap: creates tables directly from the SQLAlchemy models.

This is NOT a migration tool — it won't handle schema changes safely once there's
real data. Add Alembic (`alembic init migrations`) before this service has anything
worth not losing, then delete this script in favour of `alembic upgrade head`.
"""

from app.db import Base, engine
from app.models import Organization, User  # noqa: F401 — import so Base knows about them

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("auth tables created")
