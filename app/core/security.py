from operator import inv
import os
import token
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta, timezone
from typing import Literal, Optional
from pwdlib import PasswordHash
from sqlalchemy.orm import Session
from app.api.v1.auth.repository import UserRepository
from app.core.config import settings
from app.core.db import get_db



import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError, PyJWTError

from app.models.user import User

password_hash = PasswordHash.recommended()
outh2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
        )

def raise_expired_token():
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token has expired",
        headers={"WWW-Authenticate": "Bearer"},
        )
    
def raise_forbidden():
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="not enough permissions",
        )
    
def invalid_credentials():
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials"
        )
    
def decode_token(token: str) -> dict:
    playload = jwt.decode(jwt=token, key=settings.JWT_SECRET, algorithms=[settings.JWT_ALG])
    return playload

# def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
#     to_encode = data.copy()
#     expire = datetime.now(tz=timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
#     to_encode.update({"exp": expire})
#     token = jwt.encode(payload=to_encode, key=settings.JWT_SECRET, algorithm=settings.JWT_ALG)
#     return token

def create_access_token(sub: str, minutes: int | None = None) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return  jwt.encode({"sub": sub, "exp": expire}, key=settings.JWT_SECRET, algorithm=settings.JWT_ALG)
    
    

async def get_current_user(db: Session = Depends(get_db), token: str = Depends(outh2_scheme)) -> User:
    
    try:
        payload = decode_token(token)
        subject: Optional[str] = payload.get("sub")
    
        if not subject:
            raise credentials_exception
        user_id = int(subject)
    except ExpiredSignatureError:
        raise raise_expired_token()
    except InvalidTokenError:
        raise credentials_exception
    except PyJWTError:
        raise invalid_credentials()
    
    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise invalid_credentials()
    return user
   
def hash_password(plain: str) -> str:
    return password_hash.hash(plain)

def verify_password(plain: str, hashed: str) -> bool:
    return password_hash.verify(plain, hashed)


def require_role(min_role: Literal["admin", "user", "editor"]):
    order = {"user": 0, "editor": 1, "admin": 2}
    
    def evaluation(user: User = Depends(get_current_user)) -> User:
        if order[user.role] < order[min_role]:
            raise raise_forbidden()
        return user
    
    return evaluation

async def auth2_token(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    repository = UserRepository(db)
    user = repository.get_by_email(form.username)
    if not user or not verify_password(form.password, user.hashed_password):
        raise invalid_credentials()
    token = create_access_token(sub=str(user.id), minutes=60*24*7)  # 7 days
    return {"access_token": token, "token_type": "bearer"}
    

require_user = require_role("user")
require_editor = require_role("editor")
require_admin = require_role("admin")


    