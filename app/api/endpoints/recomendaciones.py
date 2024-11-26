from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.db.session import get_db
from app.schemas.recomendacion import RecomendacionRequest
from app.services.recomendacion.sistema_recomendaciones import RecomendacionService
from app.core.auth import require_vendedor

# Configuración del logger
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/", response_model=List[dict])
async def obtener_recomendaciones(
    request: RecomendacionRequest,
    db: Session = Depends(get_db)
):
    """
    Obtiene recomendaciones de productos para un cliente específico.

    Args:
        request (RecomendacionRequest): Datos de la solicitud de recomendaciones
        db (Session): Sesión de base de datos

    Returns:
        List[dict]: Lista de recomendaciones de productos con sus scores

    Raises:
        HTTPException: Si ocurre un error al generar las recomendaciones
    """
    try:
        servicio_recomendacion = RecomendacionService(db)
        recomendaciones = servicio_recomendacion.generar_recomendaciones(
            cliente_id=request.cliente_id,
            producto_id=request.producto_id,
            limit=request.limit
        )
        return recomendaciones

    except ValueError as e:
        logger.error(f"Error al generar recomendaciones: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error interno: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")