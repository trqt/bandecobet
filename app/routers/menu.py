from fastapi import APIRouter, HTTPException
from sqlmodel import select
from datetime import datetime

from app.models import Cardapio, Prato, TipoRef
from app.db import SessionDep


router = APIRouter(
    prefix="/menu",
    tags=["menu"],
    #dependencies=[Depends(get_current_user)],
    responses={404: {"description": "Not found"}},
)


# return all today dishes
@router.get("/today", response_model=list[Prato])
async def read_weeks_menu(
        session: SessionDep,
):
    today = datetime.now().isocalendar()
    week = today.week
    year = today.year

    statement = select(Cardapio).where(Cardapio.semana == week).where(Cardapio.ano == year)
    menu = session.exec(statement).first()
    return menu.pratos

# return all today dishes
@router.get("/{year}/{week}", response_model=list[Prato])
async def read_menu(
        session: SessionDep,
        year: int,
        week: int
):
    statement = select(Cardapio).where(Cardapio.semana == week).where(Cardapio.ano == year)
    menu = session.exec(statement).first()
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found")
    return menu.pratos

@router.get("/sample", response_model=Cardapio)
def create_sample_menu(
        session: SessionDep,
):
    week = 50
    # Create a new menu
    lunch_menu = Cardapio(
        name="Summer Lunch Menu",
        description="Refreshing dishes for a hot day"
    )

    # Create dishes for the menu
    pedro_lucas = Prato(
        nome="Pedro Lucas",
        descricao="Pedro Lucas fresco com molho roty",
        tipo_refeicao=TipoRef.ALMOCO,
        cardapio=lunch_menu
    )

    ali_suaiden = Prato(
        nome="Massa Ali Suaiden",
        descricao="Massa Ali Suaiden com uma pitada de sal",
        tipo_refeicao=TipoRef.ALMOCO,
        cardapio=lunch_menu
    )

    # Add dishes to the menu
    lunch_menu.semana = week
    lunch_menu.ano = 2024
    lunch_menu.pratos = [pedro_lucas, ali_suaiden]

    # Add to session and commit
    session.add(lunch_menu)
    session.commit()
    session.refresh(lunch_menu)

    return lunch_menu
