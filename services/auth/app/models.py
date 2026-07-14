import enum
import uuid

from pydantic import BaseModel, EmailStr
from sqlalchemy import Column, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db import Base


class OrgType(str, enum.Enum):
    hospital = "hospital"
    insurer = "insurer"
    government = "government"
    manufacturer = "manufacturer"  # MedSource supplier side
    internal = "internal"  # IHP staff


class UserRole(str, enum.Enum):
    admin = "admin"        # org-level admin
    member = "member"      # regular user in an org
    ihp_staff = "ihp_staff"  # cross-org internal access


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    org_type = Column(Enum(OrgType), nullable=False)

    users = relationship("User", back_populates="organization")


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.member)

    organization = relationship("Organization", back_populates="users")


# --- Pydantic schemas -------------------------------------------------------


class RegisterRequest(BaseModel):
    org_name: str
    org_type: OrgType
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: uuid.UUID
    email: str
    role: UserRole
    organization_id: uuid.UUID
    org_type: OrgType

    class Config:
        from_attributes = True
