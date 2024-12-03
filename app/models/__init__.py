from pydantic import EmailStr, BaseModel
from sqlmodel import Field, Relationship, SQLModel, Column, Enum
from typing import Optional 
from datetime import date
import enum

class TipoRef(str, enum.Enum):
    ALMOCO = "almoco"
    JANTA = "janta"


class PratoBase(SQLModel):
    nome: str
    descricao: str

class PratoPublic(PratoBase):
    id: int

class Prato(PratoBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    data: date
    tipo_refeicao: TipoRef = Column(Enum(TipoRef))
    cardapio_id: Optional[int] = Field(default=None, foreign_key="cardapio.id")
    cardapio: Optional["Cardapio"] = Relationship(back_populates="pratos")

class Aposta(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    data: date = Field(default_factory=date.today)
    resultado: bool = Field(default=False)
    prato_id: int = Field(foreign_key="prato.id")
    prato: Prato = Relationship()
    owner_id: int = Field(foreign_key="usuario.id")
    owner: "Usuario" = Relationship(back_populates="aposta")

class UsuarioBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    numero_usp: str = Field(unique=True, index=True, max_length=10)
    nome: str

class UsuarioRanking(SQLModel):
    nome: str
    pontos: int
    taxa_acerto: int

class UsuarioCreate(UsuarioBase):
    password: str = Field(min_length=8, max_length=60)

class UsuarioPublic(UsuarioBase):
    id: int
    pontos: int
    taxa_acerto: int

    

class Usuario(UsuarioBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    pontos: int = Field(default=2000)
    taxa_acerto: int = Field(default=0)
    aposta: list[Aposta] = Relationship(back_populates="owner", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    hashed_password: str 

class Cardapio(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    semana: int
    ano: int
    pratos: list[Prato] = Relationship(back_populates="cardapio")

class Token(BaseModel):
    access_token: str
    numero_usp: Optional[int] = None
