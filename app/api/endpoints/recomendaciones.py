from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.db.session import get_db
from app.services.recomendacion.sistema_recomendaciones import RecomendacionService
from app.core.auth import require_vendedor

# Configuración del logger
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/", response_model=List[dict])
async def obtener_recomendaciones(
    cliente_id: int,
    producto_id: Optional[int] = None,
    limit: Optional[int] = Query(default=5, le=10, ge=1),
    db: Session = Depends(get_db)
):
    """
    Obtiene recomendaciones de productos para un cliente específico.

    Args:
        cliente_id (int): ID del cliente para el que se generarán recomendaciones
        producto_id (Optional[int]): ID del producto semilla (opcional)
        limit (Optional[int]): Número máximo de recomendaciones (entre 1 y 10)
        db (Session): Sesión de base de datos

    Returns:
        List[dict]: Lista de recomendaciones de productos con sus scores

    Raises:
        HTTPException: Si ocurre un error al generar las recomendaciones
    """
    try:
        servicio_recomendacion = RecomendacionService(db)
        recomendaciones = servicio_recomendacion.generar_recomendaciones(
            cliente_id=cliente_id,
            producto_id=producto_id,
            limit=limit
        )
        return recomendaciones

    except ValueError as e:
        logger.error(f"Error al generar recomendaciones: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error interno: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")