from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, validator
from decimal import Decimal

class VentaBase(BaseModel):
    """
    Esquema base para Venta que contiene los campos comunes.
    """
    cliente_id: int = Field(..., gt=0, description="ID del cliente que realiza la compra")
    total: Decimal = Field(..., ge=0, description="Monto total de la venta")
    estado: str = Field(..., description="Estado actual de la venta")

    @validator('estado')
    def validate_estado(cls, v):
        """Valida que el estado sea uno de los permitidos"""
        estados_validos = {'pendiente', 'completada', 'cancelada', 'en_proceso'}
        if v.lower() not in estados_validos:
            raise ValueError(f'Estado debe ser uno de: {", ".join(estados_validos)}')
        return v.lower()

class VentaCreate(VentaBase):
    """
    Esquema para crear una nueva Venta.
    No incluye campos que se generan automáticamente.
    """
    pass

class VentaUpdate(BaseModel):
    """
    Esquema para actualizar una Venta.
    Todos los campos son opcionales para permitir actualizaciones parciales.
    """
    total: Optional[Decimal] = Field(None, ge=0)
    estado: Optional[str] = None

    @validator('estado')
    def validate_estado(cls, v):
        if v is not None:
            estados_validos = {'pendiente', 'completada', 'cancelada', 'en_proceso'}
            if v.lower() not in estados_validos:
                raise ValueError(f'Estado debe ser uno de: {", ".join(estados_validos)}')
            return v.lower()
        return v

class Venta(VentaBase):
    """
    Esquema completo de Venta que incluye todos los campos.
    Se usa para respuestas de la API.
    """
    id: int
    fecha_venta: datetime

    class Config:
        """Configuración del esquema para permitir ORM"""
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: str(v)
        }