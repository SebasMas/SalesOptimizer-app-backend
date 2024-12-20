from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, validator
from decimal import Decimal

class RecomendacionBase(BaseModel):
    """
    Esquema base para Recomendacion que contiene los campos comunes.
    """
    cliente_id: int = Field(..., gt=0, description="ID del cliente para el que se genera la recomendación")
    producto_recomendado_id: int = Field(..., gt=0, description="ID del producto recomendado")
    score: float = Field(..., ge=0, le=1, description="Puntuación de la recomendación (0-1)")

class RecomendacionCreate(RecomendacionBase):
    """
    Esquema para crear una nueva Recomendacion.
    No incluye campos que se generan automáticamente.
    """
    pass

class RecomendacionUpdate(BaseModel):
    """
    Esquema para actualizar una Recomendacion.
    Todos los campos son opcionales para permitir actualizaciones parciales.
    """
    score: Optional[float] = Field(None, ge=0, le=1)
    efectiva: Optional[bool] = None

class Recomendacion(RecomendacionBase):
    """
    Esquema completo de Recomendacion que incluye todos los campos.
    Se usa para respuestas de la API.
    """
    id: int
    fecha_recomendacion: datetime
    efectiva: bool

    class Config:
        """Configuración del esquema para permitir ORM"""
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
class RecomendacionRequest(BaseModel):
    """
    Modelo de datos para la solicitud de recomendaciones.

    Attributes:
        cliente_id (int): ID del cliente para el que se generarán recomendaciones
        producto_id (Optional[int]): ID del producto semilla (opcional)
        limit (Optional[int]): Número máximo de recomendaciones a retornar
    """
    cliente_id: int = Field(..., gt=0, description="ID del cliente")
    producto_id: Optional[int] = Field(None, gt=0, description="ID del producto semilla")
    limit: Optional[int] = Field(5, ge=1, le=10, description="Número máximo de recomendaciones")