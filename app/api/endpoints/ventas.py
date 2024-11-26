from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from decimal import Decimal

from app.schemas.venta import Venta, VentaCreate
from app.models.venta import Venta as VentaModel
from app.models.detalle_venta import DetalleVenta as DetalleVentaModel
from app.models.producto import Producto as ProductoModel
from app.models.cliente import Cliente as ClienteModel
from app.db.session import get_db
from app.core.auth import require_vendedor
import logging

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/", response_model=Venta)
# @require_vendedor
async def create_venta(venta: VentaCreate, db: Session = Depends(get_db)):
    """
    Crea una nueva venta con sus detalles.

    Args:
        venta (VentaCreate): Datos de la venta a crear, incluyendo detalles
        db (Session): Sesión de la base de datos

    Returns:
        Venta: La venta creada con todos sus detalles

    Raises:
        HTTPException: Si el cliente no existe, si algún producto no existe,
                      o si no hay suficiente stock
    """
    try:
        # Verificar que el cliente existe
        cliente = db.query(ClienteModel).filter(ClienteModel.id == venta.cliente_id).first()
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")

        # Crear la venta
        db_venta = VentaModel(
            cliente_id=venta.cliente_id,
            total=venta.total,
            estado=venta.estado,
            fecha_venta=datetime.now()  # Siempre usar la fecha actual
        )
        db.add(db_venta)
        db.flush()

        # Procesar los detalles de la venta
        for detalle in venta.detalles_venta:
            # Verificar que el producto existe y hay suficiente stock
            producto = db.query(ProductoModel).filter(ProductoModel.id == detalle.producto_id).first()
            if not producto:
                db.rollback()
                raise HTTPException(status_code=404, detail=f"Producto {detalle.producto_id} no encontrado")
            
            if producto.stock < detalle.cantidad:
                db.rollback()
                raise HTTPException(
                    status_code=400,
                    detail=f"Stock insuficiente para el producto {producto.nombre}"
                )

            # Crear el detalle de venta
            db_detalle = DetalleVentaModel(
                venta_id=db_venta.id,
                producto_id=detalle.producto_id,
                cantidad=detalle.cantidad,
                precio_unitario=detalle.precio_unitario
            )
            db.add(db_detalle)

            # Actualizar el stock y ventas del producto
            producto.stock -= detalle.cantidad
            producto.ventas_ultimo_mes += detalle.cantidad

        db.commit()
        db.refresh(db_venta)
        return db_venta

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creando venta: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[Venta])
async def read_ventas(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Recupera una lista de ventas.

    Args:
        skip (int): Número de registros a omitir (para paginación)
        limit (int): Número máximo de registros a devolver
        db (Session): Sesión de la base de datos

    Returns:
        List[Venta]: Lista de ventas encontradas
    """
    ventas = db.query(VentaModel).offset(skip).limit(limit).all()
    return ventas

@router.get("/cliente/{cliente_id}", response_model=List[Venta])
async def read_ventas_by_cliente(
    cliente_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Recupera todas las ventas de un cliente específico.

    Args:
        cliente_id (int): ID del cliente
        skip (int): Número de registros a omitir
        limit (int): Número máximo de registros a devolver
        db (Session): Sesión de la base de datos

    Returns:
        List[Venta]: Lista de ventas del cliente

    Raises:
        HTTPException: Si el cliente no existe
    """
    if not db.query(ClienteModel).filter(ClienteModel.id == cliente_id).first():
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    ventas = db.query(VentaModel)\
        .filter(VentaModel.cliente_id == cliente_id)\
        .offset(skip)\
        .limit(limit)\
        .all()
    return ventas

@router.get("/{venta_id}", response_model=Venta)
async def read_venta(venta_id: int, db: Session = Depends(get_db)):
    """
    Recupera una venta específica por su ID.

    Args:
        venta_id (int): ID de la venta a recuperar
        db (Session): Sesión de la base de datos

    Returns:
        Venta: La venta encontrada

    Raises:
        HTTPException: Si la venta no existe
    """
    venta = db.query(VentaModel).filter(VentaModel.id == venta_id).first()
    if not venta:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    return venta