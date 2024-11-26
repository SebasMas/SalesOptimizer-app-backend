from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.schemas.cliente import Cliente, ClienteCreate, ClienteUpdate
from app.models.cliente import Cliente as ClienteModel
from app.db.session import get_db
from app.core.auth import require_usuario  # Para autenticación si es necesaria

router = APIRouter()

@router.post("/", response_model=Cliente)
async def create_cliente(cliente: ClienteCreate, db: Session = Depends(get_db)):
    """
    Crea un nuevo cliente en la base de datos.

    Args:
        cliente (ClienteCreate): Datos del cliente a crear
        db (Session): Sesión de la base de datos

    Returns:
        Cliente: El cliente creado

    Raises:
        HTTPException: Si ya existe un cliente con el mismo email
    """
    # Verificar si ya existe un cliente con el mismo email
    if db.query(ClienteModel).filter(ClienteModel.email == cliente.email).first():
        raise HTTPException(status_code=400, detail="Este email ya está registrado")
    
    db_cliente = ClienteModel(**cliente.dict())
    db.add(db_cliente)
    db.commit()
    db.refresh(db_cliente)
    return db_cliente

@router.get("/", response_model=List[Cliente])
async def read_clientes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Recupera una lista de clientes.

    Args:
        skip (int): Número de registros a omitir (para paginación)
        limit (int): Número máximo de registros a devolver
        db (Session): Sesión de la base de datos

    Returns:
        List[Cliente]: Lista de clientes encontrados
    """
    clientes = db.query(ClienteModel).offset(skip).limit(limit).all()
    return clientes

@router.get("/{cliente_id}", response_model=Cliente)
async def read_cliente(cliente_id: int, db: Session = Depends(get_db)):
    """
    Recupera un cliente específico por su ID.

    Args:
        cliente_id (int): ID del cliente a recuperar
        db (Session): Sesión de la base de datos

    Returns:
        Cliente: El cliente encontrado

    Raises:
        HTTPException: Si el cliente no existe
    """
    db_cliente = db.query(ClienteModel).filter(ClienteModel.id == cliente_id).first()
    if db_cliente is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return db_cliente

@router.put("/{cliente_id}", response_model=Cliente)
async def update_cliente(
    cliente_id: int,
    cliente: ClienteUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualiza un cliente existente.

    Args:
        cliente_id (int): ID del cliente a actualizar
        cliente (ClienteUpdate): Datos actualizados del cliente
        db (Session): Sesión de la base de datos

    Returns:
        Cliente: El cliente actualizado

    Raises:
        HTTPException: Si el cliente no existe o si hay conflicto con el email
    """
    db_cliente = db.query(ClienteModel).filter(ClienteModel.id == cliente_id).first()
    if db_cliente is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    # Si se está actualizando el email, verificar que no exista
    if cliente.email and cliente.email != db_cliente.email:
        if db.query(ClienteModel).filter(ClienteModel.email == cliente.email).first():
            raise HTTPException(status_code=400, detail="Este email ya está registrado")

    for key, value in cliente.dict(exclude_unset=True).items():
        setattr(db_cliente, key, value)

    db.commit()
    db.refresh(db_cliente)
    return db_cliente

@router.delete("/{cliente_id}", response_model=Cliente)
async def delete_cliente(cliente_id: int, db: Session = Depends(get_db)):
    """
    Elimina un cliente.

    Args:
        cliente_id (int): ID del cliente a eliminar
        db (Session): Sesión de la base de datos

    Returns:
        Cliente: El cliente eliminado

    Raises:
        HTTPException: Si el cliente no existe
    """
    db_cliente = db.query(ClienteModel).filter(ClienteModel.id == cliente_id).first()
    if db_cliente is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    db.delete(db_cliente)
    db.commit()
    return db_cliente