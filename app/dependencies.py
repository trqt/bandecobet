from typing import Annotated, Optional, Any

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jwt.exceptions import InvalidTokenError
import jwt

from app.db import SessionDep

# Fix passlib bug
import bcrypt
if not hasattr(bcrypt, '__about__'):
    bcrypt.__about__ = type('about', (object,), {'__version__': bcrypt.__version__})

from app.models import Usuario

# TODO: Load from .env
SECRET_KEY="totallysecretandsecure"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # 60min * 24 * 7 = 7 days

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

AuthDep = Annotated[str, Depends(oauth2_scheme)]

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_user_by_nusp(*, session: Session, nusp: str) -> Optional[Usuario]:
    statement = select(Usuario).where(Usuario.numero_usp == nusp)
    session_user = session.exec(statement).first()
    return session_user

def authenticate(*, session: Session, nusp: str, password: str) -> Optional[Usuario]:
    db_user = get_user_by_nusp(session=session, nusp=nusp)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user

def create_access_token(subject: str | Any, expires_delta: timedelta) -> str:
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt

async def get_current_user(session: SessionDep, token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        nusp: str = payload.get("sub")
        if nusp is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
    user = get_user_by_nusp(session=session, nusp=nusp)
    if user is None:
        raise credentials_exception
    return user

