from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import LoginRequest, Organization, RegisterRequest, TokenResponse, User
from app.security import create_access_token, hash_password, verify_password

router = APIRouter()


@router.post("/register", response_model=TokenResponse)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    org = Organization(name=payload.org_name, org_type=payload.org_type)
    db.add(org)
    db.flush()  # get org.id before creating the user

    user = User(
        organization_id=org.id,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role="admin",  # first user in a new org is its admin
    )
    db.add(user)
    db.commit()

    token = create_access_token(
        user_id=str(user.id), org_id=str(org.id), org_type=org.org_type.value, role=user.role.value
    )
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    org = user.organization
    token = create_access_token(
        user_id=str(user.id), org_id=str(org.id), org_type=org.org_type.value, role=user.role.value
    )
    return TokenResponse(access_token=token)
