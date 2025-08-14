import os
import jwt
import logging

from datetime import datetime, timedelta
from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from jwt import PyJWTError
from functools import wraps

# Cargar variables de entorno
load_dotenv()

# Logger para esta utilidad
logger = logging.getLogger(__name__)

# Tomamos la clave secreta de .env
SECRET_KEY = os.getenv("SECRET_KEY")
logger.info(f"Loaded SECRET_KEY: {repr(SECRET_KEY)}")

# HTTPBearer para Depends()
security = HTTPBearer()


def create_jwt_token(
    firstname: str,
    lastname: str,
    email: str,
    active: bool,
    admin: bool,
    id: str
) -> str:
    """
    Crea un JWT con expiración de 1 hora.
    Arroja HTTPException(500) si falta SECRET_KEY o falla la codificación.
    """
    # Validar que exista la clave
    if not SECRET_KEY:
        logger.error("SECRET_KEY no está configurada.")
        raise HTTPException(
            status_code=500,
            detail="Configuration error: SECRET_KEY is missing"
        )

    payload = {
        "id": id,
        "firstname": firstname,
        "lastname": lastname,
        "email": email,
        "active": active,
        "admin": admin,
        "exp": datetime.utcnow() + timedelta(hours=1),
        "iat": datetime.utcnow()
    }

    try:
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        return token
    except Exception as e:
        logger.error(f"JWT encoding failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Token generation error"
        )


def validateuser(func):
    """
    Decorador para endpoints que requieren token válido de usuario.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request: Request = kwargs.get("request")
        if not request:
            raise HTTPException(status_code=400, detail="Request object not found")

        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise HTTPException(status_code=400, detail="Authorization header missing")

        try:
            schema, token = auth_header.split()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid Authorization header format")

        if schema.lower() != "bearer":
            raise HTTPException(status_code=400, detail="Invalid auth schema")

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except PyJWTError:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        # Validaciones de claims
        exp = payload.get("exp")
        if datetime.utcfromtimestamp(exp) < datetime.utcnow():
            raise HTTPException(status_code=401, detail="Expired token")

        if not payload.get("active", False):
            raise HTTPException(status_code=401, detail="Inactive user")

        # Adjuntamos info al request
        request.state.email = payload.get("email")
        request.state.firstname = payload.get("firstname")
        request.state.lastname = payload.get("lastname")
        request.state.id = payload.get("id")

        return await func(*args, **kwargs)

    return wrapper


def validateadmin(func):
    """
    Decorador para endpoints que requieren token válido de administrador.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request: Request = kwargs.get("request")
        if not request:
            raise HTTPException(status_code=400, detail="Request object not found")

        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise HTTPException(status_code=400, detail="Authorization header missing")

        try:
            schema, token = auth_header.split()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid Authorization header format")

        if schema.lower() != "bearer":
            raise HTTPException(status_code=400, detail="Invalid auth schema")

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except PyJWTError:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        # Validaciones de claims
        exp = payload.get("exp")
        if datetime.utcfromtimestamp(exp) < datetime.utcnow():
            raise HTTPException(status_code=401, detail="Expired token")

        if not payload.get("active", False) or not payload.get("admin", False):
            raise HTTPException(status_code=401, detail="Inactive user or not admin")

        # Adjuntamos info al request
        request.state.email = payload.get("email")
        request.state.firstname = payload.get("firstname")
        request.state.lastname = payload.get("lastname")
        request.state.id = payload.get("id")
        request.state.admin = payload.get("admin")

        return await func(*args, **kwargs)

    return wrapper


def validate_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Dependency para FastAPI: valida token de usuario (no admin).
    """
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    exp = payload.get("exp")
    if datetime.utcfromtimestamp(exp) < datetime.utcnow():
        raise HTTPException(status_code=401, detail="Expired token")

    if not payload.get("active", False):
        raise HTTPException(status_code=401, detail="Inactive user")

    return {
        "id": payload.get("id"),
        "email": payload.get("email"),
        "firstname": payload.get("firstname"),
        "lastname": payload.get("lastname"),
        "active": payload.get("active"),
        "role": "admin" if payload.get("admin", False) else "user"
    }


def validate_admin(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Dependency para FastAPI: valida token de administrador.
    """
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    exp = payload.get("exp")
    if datetime.utcfromtimestamp(exp) < datetime.utcnow():
        raise HTTPException(status_code=401, detail="Expired token")

    if not payload.get("active", False) or not payload.get("admin", False):
        raise HTTPException(status_code=401, detail="Inactive user or not admin")

    return {
        "id": payload.get("id"),
        "email": payload.get("email"),
        "firstname": payload.get("firstname"),
        "lastname": payload.get("lastname"),
        "active": payload.get("active"),
        "role": "admin"
    }
