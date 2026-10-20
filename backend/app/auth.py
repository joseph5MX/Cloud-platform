import os
import requests
from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from .database import get_db
from .models import User

load_dotenv()
KEYCLOAK_URL = os.environ.get("KEYCLOAK_URL", "http://localhost:8080")
REALM = os.environ.get("KEYCLOAK_REALM", "cloudplatform")
CLIENT_ID = os.environ.get("KEYCLOAK_CLIENT_ID", "cloud-frontend")
JWKS_URL = f"{KEYCLOAK_URL}/realms/{REALM}/protocol/openid-connect/certs"

bearer = HTTPBearer()
_keys = None


def get_keys():
    global _keys
    if _keys is None:
        try:
            data = requests.get(JWKS_URL, timeout=5).json()
        except requests.RequestException:
            raise HTTPException(503, "Identity provider unreachable")
        _keys = {"keys": [k for k in data["keys"] if k.get("use") == "sig"]}
    return _keys


def current_user(
    creds: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db),
):
    try:
        claims = jwt.decode(creds.credentials, get_keys(),
                            algorithms=["RS256"],
                            options={"verify_aud": False})
    except JWTError:
        raise HTTPException(401, "Invalid or expired token")
    if claims.get("azp") != CLIENT_ID:
        raise HTTPException(401, "Token was not issued for this application")

    roles = claims.get("realm_access", {}).get("roles", [])
    role = "admin" if "admin" in roles else "customer"
    user = db.get(User, claims["sub"])
    if user is None:
        user = User(id=claims["sub"], role=role,
                    username=claims.get("preferred_username", ""))
        db.add(user)
    else:
        user.role = role
    db.commit()
    return user


def require_admin(user: User = Depends(current_user)):
    if user.role != "admin":
        raise HTTPException(403, "Administrator role required")
    return user
