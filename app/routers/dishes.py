from fastapi import APIRouter
from sqlmodel import select

from app.models import  Prato, PratoPublic
from app.db import SessionDep


router = APIRouter(
    prefix="/dishes",
    tags=["dishes"],
    #dependencies=[Depends(get_current_user)],
    responses={404: {"description": "Not found"}},
)


# return all today dishes
@router.get("/", response_model=list[PratoPublic])
async def read_dishes(
        session: SessionDep,
):
    statement = select(Prato)
    dishes = session.exec(statement)
    return dishes

