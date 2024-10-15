from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ProductoBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    precio: float
    stock: int
    categoria: Optional[str] = None

class ProductoCreate(ProductoBase):
    pass

class ProductoUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    precio: Optional[float] = None
    stock: Optional[int] = None
    categoria: Optional[str] = None
    baja_rotacion: Optional[bool] = None

class ProductoInDB(ProductoBase):
    id: int
    fecha_creacion: datetime
    ventas_ultimo_mes: int
    baja_rotacion: bool

    class Config:
        orm_mode = True

class Producto(ProductoInDB):
    pass