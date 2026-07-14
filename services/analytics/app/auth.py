import os

from fastapi import Header, HTTPException
from jose import JWTError, jwt
from pydantic import BaseModel

# Must match the auth service's signing secret exactly — both read from the
# same K8s secret "jwt-signing-key" / local .env JWT_SECRET.
JWT_SECRET = os.environ.get("JWT_SECRET", "dev-only-secret-change-me")
JWT_ALGORITHM = "HS256"

# NOTE: this file is intentionally near-identical to services/auth/app/security.py's
# decode half. Once there's a 3rd or 4th service repeating this, pull it into a
# shared internal package (e.g. published to a private PyPI index, or a git
# submodule) rather than copy-pasting further.


class CurrentUser(BaseModel):
    user_id: str
    org_id: str
    org_type: str
    role: str


def get_current_user(authorization: str = Header(...)) -> CurrentUser:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or malformed Authorization header")

    token = authorization.removeprefix("Bearer ").strip()
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return CurrentUser(
        user_id=payload["sub"],
        org_id=payload["org_id"],
        org_type=payload["org_type"],
        role=payload["role"],
    )
