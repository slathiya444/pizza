# app/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.core.config import settings
from app.database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = crud.user.get_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def get_current_active_admin(
    current_user: models.User = Depends(get_current_active_user),
) -> models.User:
    if current_user.role != models.UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user

def get_current_active_delivery_partner(
    current_user: models.User = Depends(get_current_active_user),
) -> models.User:
    if current_user.role != models.UserRole.DELIVERY_PARTNER:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user