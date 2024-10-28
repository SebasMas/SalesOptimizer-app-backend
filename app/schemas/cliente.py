from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, validator
from decimal import Decimal

# Cliente Schemas
class ClienteBase(BaseModel):
    """
    Esquema base para Cliente que contiene los campos comunes.
    """
    nombre: str = Field(..., min_length=2, max_length=100, description="Nombre completo del cliente")
    email: EmailStr = Field(..., description="Correo electrónico del cliente")
    telefono: Optional[str] = Field(None, max_length=20, description="Número de teléfono del cliente")

class ClienteCreate(ClienteBase):
    """
    Esquema para crear un nuevo Cliente.
    No incluye campos que se generan automáticamente.
    """
    pass

class ClienteUpdate(BaseModel):
    """
    Esquema para actualizar un Cliente.
    Todos los campos son opcionales para permitir actualizaciones parciales.
    """
    nombre: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    telefono: Optional[str] = Field(None, max_length=20)
    activo: Optional[bool] = None

class Cliente(ClienteBase):
    """
    Esquema completo de Cliente que incluye todos los campos.
    Se usa para respuestas de la API.
    """
    id: int
    fecha_registro: datetime
    activo: bool

    class Config:
        """Configuración del esquema para permitir ORM"""
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }