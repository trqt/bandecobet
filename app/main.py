from fastapi import Depends, FastAPI
from starlette.responses import FileResponse

from .dependencies import oauth2_scheme
from .internal import admin
from .routers import auth, bets, ranking, users, dishes, menu

from .db import create_db_and_tables

app = FastAPI()#dependencies=[Depends(get_query_token)])


@app.on_event("startup")
def on_startup():
    create_db_and_tables()

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(bets.router)
app.include_router(ranking.router)
app.include_router(dishes.router)
app.include_router(menu.router)
app.include_router(
    admin.router,
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(oauth2_scheme)],
    responses={418: {"description": "I'm a teapot"}},
)

@app.get("/")
async def root():
    return FileResponse('public/index.html')
