from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.schemas.usuario import Usuario, UsuarioCreate, UsuarioUpdate #-- Se agregó app. a la ruta
from app.models.usuario import Usuario as UsuarioModel #-- Se agregó app. a la ruta
from app.db.session import get_db #-- Se agregó app. a la ruta

router = APIRouter()

@router.post("/", response_model=Usuario)
def create_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    """
    Crea un nuevo usuario en la get_db de datos.

    Args:
        usuario (UsuarioCreate): Datos del usuario a crear.
        db (Session): Sesión de la get_db de datos.

    Returns:
        Usuario: El usuario creado.

    Raises:
        HTTPException: Si ocurre un error al crear el usuario.
    """
    db_usuario = UsuarioModel(**usuario.dict())
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario

@router.get("/", response_model=List[Usuario])
def read_usuarios(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Recupera una lista de usuarios de la get_db de datos.

    Args:
        skip (int): Número de registros a omitir (para paginación).
        limit (int): Número máximo de registros a devolver.
        db (Session): Sesión de la get_db de datos.

    Returns:
        List[Usuario]: Lista de usuarios recuperados.
    """
    usuarios = db.query(UsuarioModel).offset(skip).limit(limit).all()
    return usuarios

@router.get("/{usuario_id}", response_model=Usuario)
def read_usuario(usuario_id: int, db: Session = Depends(get_db)):
    """
    Recupera un usuario específico por su ID.

    Args:
        usuario_id (int): ID del usuario a recuperar.
        db (Session): Sesión de la get_db de datos.

    Returns:
        Usuario: El usuario recuperado.

    Raises:
        HTTPException: Si el usuario no se encuentra.
    """
    db_usuario = db.query(UsuarioModel).filter(UsuarioModel.id == usuario_id).first()
    if db_usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return db_usuario

@router.put("/{usuario_id}", response_model=Usuario)
def update_usuario(usuario_id: int, usuario: UsuarioUpdate, db: Session = Depends(get_db)):
    """
    Actualiza un usuario existente en la get_db de datos.

    Args:
        usuario_id (int): ID del usuario a actualizar.
        usuario (UsuarioUpdate): Datos actualizados del usuario.
        db (Session): Sesión de la get_db de datos.

    Returns:
        Usuario: El usuario actualizado.

    Raises:
        HTTPException: Si el usuario no se encuentra.
    """
    db_usuario = db.query(UsuarioModel).filter(UsuarioModel.id == usuario_id).first()
    if db_usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    for key, value in usuario.dict(exclude_unset=True).items():
        setattr(db_usuario, key, value)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario

@router.delete("/{usuario_id}", response_model=Usuario)
def delete_usuario(usuario_id: int, db: Session = Depends(get_db)):
    """
    Elimina un usuario de la get_db de datos.

    Args:
        usuario_id (int): ID del usuario a eliminar.
        db (Session): Sesión de la get_db de datos.

    Returns:
        Usuario: El usuario eliminado.

    Raises:
        HTTPException: Si el usuario no se encuentra.
    """
    db_usuario = db.query(UsuarioModel).filter(UsuarioModel.id == usuario_id).first()
    if db_usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    db.delete(db_usuario)
    db.commit()
    return db_usuario