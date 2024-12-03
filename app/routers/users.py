from typing import Annotated
from fastapi import APIRouter, Depends
from app.models import UsuarioPublic, Usuario
from app.dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UsuarioPublic)
async def read_users_me(
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    return current_user
