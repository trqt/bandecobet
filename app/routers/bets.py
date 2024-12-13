from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import select

from app.models import Aposta, Usuario, Prato, Cardapio
from app.db import SessionDep
from app.dependencies import get_current_user

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
                  value: int,
                  current_user: Annotated[Usuario, Depends(get_current_user)]
                  ) -> Aposta:

    today = date.today()

    #if day <= today:
    #    raise HTTPException(status_code=403, detail="Can't bet to the past")

    if value <= 0 or value > current_user.pontos:
        raise HTTPException(status_code=403, detail="Can't make leveraged bets")
    # subtract points
    db_user = session.get(Usuario, current_user.id)
    db_user.pontos -= value
    session.add(db_user)
    session.commit()
    
    plate = session.get(Prato, prato_id)

    if not plate:
        raise HTTPException(status_code=400, detail="Plate doesn't exists")

    db_bet = Aposta(prato=plate, valor=value, data=day, owner=current_user)
    session.add(db_bet)
    session.commit()
    session.refresh(db_bet)

    #return {"status": "ok"}
    return db_bet

@router.post("/finalise")
async def collapse_bet(session: SessionDep,
                  current_user: Annotated[Usuario, Depends(get_current_user)]
                  ) -> Aposta:

    today = date.today()

    stmt = select(Aposta).where(Aposta.owner_id == current_user.id).where(Aposta.resultado == False).where(Aposta.data <= today)
    bets = session.exec(stmt).all()

    stmt = select(Aposta).where(Aposta.owner_id == current_user.id)
    bets_len = len(session.exec(stmt).all())

    if not bets:
        raise HTTPException(status_code=400, detail="You don't have any bets to finalise")

    print(f"Bets:\n")
    for bet in bets:
        print(f"Bet: {bet}")
        bet.resultado = True

        bdate = bet.data.isocalendar()
        statement = select(Cardapio).where(Cardapio.semana == bdate.week).where(Cardapio.ano == bdate.year)
        menu = session.exec(statement).first()

        if bet.prato in menu.pratos:
            # TODO: Variable odds
            db_user = session.get(Usuario, current_user.id)
            db_user.pontos += bet.valor * 2
            db_user.taxa_acerto = int((db_user.taxa_acerto + 1/bets_len) * 100)
            session.add(db_user)
            session.commit()

        session.add(bet)

    session.commit()

    bets = session.refresh(bets)

    return bets

