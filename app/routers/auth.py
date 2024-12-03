from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

from app.models import UsuarioPublic, UsuarioCreate, Usuario, Token
from app.db import SessionDep

from app.dependencies import get_password_hash, authenticate, create_access_token
from app.dependencies import ACCESS_TOKEN_EXPIRE_MINUTES


router = APIRouter()

@router.post("/register", response_model=UsuarioPublic)
async def register(user: UsuarioCreate, session: SessionDep):
    db_user = Usuario.model_validate(user, update={"hashed_password": get_password_hash(user.password)})
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

@router.post("/login")
async def login(session: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    user = authenticate(session=session, nusp=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return Token(
        access_token=create_access_token(
            user.numero_usp, expires_delta=access_token_expires
        ),
        numero_usp = user.numero_usp
    )

