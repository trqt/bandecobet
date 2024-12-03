from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import select

from app.models import Aposta, Usuario
from app.db import SessionDep
from app.dependencies import get_current_user

import datetime
from datetime import date

router = APIRouter(
    prefix="/bet",
    tags=["bets"],
    dependencies=[Depends(get_current_user)],
    responses={404: {"description": "Not found"}},
)


# return all bets
@router.get("/")
async def read_bets(
        session: SessionDep,
        current_user: Annotated[Usuario, Depends(get_current_user)]
) -> list[Aposta]:
    statement = select(Aposta).where(Aposta.owner_id == current_user.id)
    bets = session.exec(statement)
    return bets

# return the bet with its id
@router.get("/{bet_id}")
async def read_bet(bet_id: int, session: SessionDep,
    current_user: Annotated[Usuario, Depends(get_current_user)]) -> Aposta:
    bet = session.get(Aposta, bet_id)
    if not bet or bet.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Bet not found")
    return bet 


# TODO: update bet if its open to change
@router.put("/{bet_id}")
async def update_bet(bet_id: int):
    return {"item_id": bet_id}

# create new bet for the day
@router.post("/new")
async def new_bet(day: date,
                  prato_id: int,
                  session: SessionDep,
                  current_user: Annotated[Usuario, Depends(get_current_user)]
                  ) -> Aposta:

    today = datetime.now()

    if day < today:
        raise HTTPException(status_code=403, detail="Can't bet to the past")

    db_bet = Aposta(prato=plate, date=day, owner=current_user)
    session.add(db_bet)
    session.commit()
    session.refresh(db_bet)

    #return {"status": "ok"}
    return db_bet
