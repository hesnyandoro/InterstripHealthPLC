import os
from datetime import datetime, timedelta, timezone

from jose import jwt
from passlib.context import CryptContext

# Shared secret used to SIGN tokens here, and to VERIFY them in every other service.
# In K8s this comes from the same "jwt-signing-key" Secret mounted into each service.
# NOTE: HS256 + shared secret is the simple starting point. Once services are deployed
# by different teams/pipelines, switch to RS256 (auth signs with a private key, other
# services verify with a public key/JWKS endpoint) so the secret doesn't have to be
# distributed to every service.
JWT_SECRET = os.environ.get("JWT_SECRET", "dev-only-secret-change-me")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 8  # 8 hour session

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(*, user_id: str, org_id: str, org_type: str, role: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": user_id,
        "org_id": org_id,
        "org_type": org_type,
        "role": role,
        "exp": expire,
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
