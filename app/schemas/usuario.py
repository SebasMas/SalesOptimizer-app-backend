from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UsuarioBase(BaseModel):
    username: str
    email: EmailStr
    rol: str

class UsuarioCreate(UsuarioBase):
    password: str

class UsuarioUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    rol: Optional[str] = None
    activo: Optional[bool] = None

class UsuarioInDB(UsuarioBase):
    id: int
    fecha_registro: datetime
    activo: bool

    class Config:
        orm_mode = True

class Usuario(UsuarioInDB):
    pass