from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import logging

from app.core.security import (
    verificar_password,
    get_password_hash,
    crear_token_acceso,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.core.auth import get_current_active_user
from app.schemas.auth import Token, UserRegister, UserResponse
from app.models.usuario import Usuario
from app.db.session import get_db

# Configuración del logger
logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    *,
    db: Session = Depends(get_db),
    user_in: UserRegister
) -> Any:
    """
    Endpoint para registrar un nuevo usuario.
    
    Args:
        db (Session): Sesión de base de datos
        user_in (UserRegister): Datos del usuario a registrar
        
    Returns:
        Usuario: Usuario creado
        
    Raises:
        HTTPException: Si el email o username ya están registrados
    """
    try:
        # Verificar si el email ya está registrado
        if db.query(Usuario).filter(Usuario.email == user_in.email).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Este email ya está registrado"
            )
        
        # Verificar si el username ya está registrado
        if db.query(Usuario).filter(Usuario.username == user_in.username).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Este nombre de usuario ya está registrado"
            )
        
        # Crear el usuario
        user = Usuario(
            email=user_in.email,
            username=user_in.username,
            password=get_password_hash(user_in.password),
            rol=user_in.rol
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        logger.info(f"Usuario registrado exitosamente: {user.username}")
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al registrar usuario: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al registrar usuario"
        )

@router.post("/login", response_model=Token)
async def login_access_token(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    Endpoint para obtener el token de acceso OAuth2 usando credenciales de usuario.
    
    Args:
        db (Session): Sesión de base de datos
        form_data (OAuth2PasswordRequestForm): Formulario con username y password
        
    Returns:
        Token: Token de acceso JWT
        
    Raises:
        HTTPException: Si las credenciales son inválidas
    """
    try:
        # Buscar usuario por email (permitimos login con email o username)
        user = None
        if "@" in form_data.username:
            user = db.query(Usuario).filter(Usuario.email == form_data.username).first()
        else:
            user = db.query(Usuario).filter(Usuario.username == form_data.username).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario o contraseña incorrectos",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        if not verificar_password(form_data.password, user.password):
            logger.warning(f"Intento de login fallido para usuario: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario o contraseña incorrectos",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        if not user.activo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Usuario inactivo"
            )
        
        # Crear token de acceso
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        token = crear_token_acceso(
            data={"sub": user.username, "rol": user.rol},
            expires_delta=access_token_expires
        )
        
        logger.info(f"Login exitoso para usuario: {user.username}")
        return {
            "access_token": token,
            "token_type": "bearer"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en el proceso de login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor durante el login"
        )

@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user: Usuario = Depends(get_current_active_user)
) -> Any:
    """
    Endpoint para obtener información del usuario actual.
    
    Args:
        current_user (Usuario): Usuario actual (inyectado por dependencia)
        
    Returns:
        Usuario: Información del usuario actual
    """
    return current_user