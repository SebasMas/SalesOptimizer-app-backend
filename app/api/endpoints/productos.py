from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.schemas.producto import Producto, ProductoCreate, ProductoUpdate #-- Se agregó app. a la ruta
from app.models.producto import Producto as ProductoModel #-- Se agregó app. a la ruta
from app.db.session import get_db #-- Se agregó app. a la ruta

router = APIRouter()

@router.post("/", response_model=Producto)
def create_producto(producto: ProductoCreate, db: Session = Depends(get_db)):
    """
    Crea un nuevo producto en la get_db de datos.

    Args:
        producto (ProductoCreate): Datos del producto a crear.
        db (Session): Sesión de la get_db de datos.

    Returns:
        Producto: El producto creado.

    Raises:
        HTTPException: Si ocurre un error al crear el producto.
    """
    db_producto = ProductoModel(**producto.dict())
    db.add(db_producto)
    db.commit()
    db.refresh(db_producto)
    return db_producto

@router.get("/", response_model=List[Producto])
def read_productos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Recupera una lista de productos de la get_db de datos.

    Args:
        skip (int): Número de registros a omitir (para paginación).
        limit (int): Número máximo de registros a devolver.
        db (Session): Sesión de la get_db de datos.

    Returns:
        List[Producto]: Lista de productos recuperados.
    """
    productos = db.query(ProductoModel).offset(skip).limit(limit).all()
    return productos

@router.get("/{producto_id}", response_model=Producto)
def read_producto(producto_id: int, db: Session = Depends(get_db)):
    """
    Recupera un producto específico por su ID.

    Args:
        producto_id (int): ID del producto a recuperar.
        db (Session): Sesión de la get_db de datos.

    Returns:
        Producto: El producto recuperado.

    Raises:
        HTTPException: Si el producto no se encuentra.
    """
    db_producto = db.query(ProductoModel).filter(ProductoModel.id == producto_id).first()
    if db_producto is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return db_producto

@router.put("/{producto_id}", response_model=Producto)
def update_producto(producto_id: int, producto: ProductoUpdate, db: Session = Depends(get_db)):
    """
    Actualiza un producto existente en la get_db de datos.

    Args:
        producto_id (int): ID del producto a actualizar.
        producto (ProductoUpdate): Datos actualizados del producto.
        db (Session): Sesión de la get_db de datos.

    Returns:
        Producto: El producto actualizado.

    Raises:
        HTTPException: Si el producto no se encuentra.
    """
    db_producto = db.query(ProductoModel).filter(ProductoModel.id == producto_id).first()
    if db_producto is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    for key, value in producto.dict(exclude_unset=True).items():
        setattr(db_producto, key, value)
    db.commit()
    db.refresh(db_producto)
    return db_producto

@router.delete("/{producto_id}", response_model=Producto)
def delete_producto(producto_id: int, db: Session = Depends(get_db)):
    """
    Elimina un producto de la get_db de datos.

    Args:
        producto_id (int): ID del producto a eliminar.
        db (Session): Sesión de la get_db de datos.

    Returns:
        Producto: El producto eliminado.

    Raises:
        HTTPException: Si el producto no se encuentra.
    """
    db_producto = db.query(ProductoModel).filter(ProductoModel.id == producto_id).first()
    if db_producto is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    db.delete(db_producto)
    db.commit()
    return db_producto