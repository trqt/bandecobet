from fastapi import APIRouter
from sqlmodel import select

from app.db import SessionDep
from app.models import UsuarioRanking, Usuario


router = APIRouter(
    prefix="/ranking",
    tags=["ranking"],
    responses={404: {"description": "Not found"}},
)


# Make it a protected route?
# returns ranking
@router.get("/", response_model=list[UsuarioRanking])
async def read_ranking(session: SessionDep):
    stmt = select(Usuario).order_by(Usuario.pontos.desc()).limit(20)
    rank = session.exec(stmt)
    
    return rank.all()
