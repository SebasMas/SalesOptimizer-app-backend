from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import logging

from app.core.security import (
    get_password_hash,
    verificar_password,
    crear_token_acceso,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.schemas.auth import UserRegister, UserResponse, Token
from app.models.usuario import Usuario
from app.db.session import get_db

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    *,
    db: Session = Depends(get_db),
    user_in: UserRegister
) -> Usuario:
    """
    Registra un nuevo usuario en el sistema.
    
    Args:
        db: Sesión de base de datos
        user_in: Datos del usuario a registrar
        
    Returns:
        Usuario: El usuario registrado
        
    Raises:
        HTTPException: Si el email o username ya están registrados
    """
    try:
        # Verificar email duplicado
        if db.query(Usuario).filter(Usuario.email == user_in.email).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Este email ya está registrado"
            )
        
        # Verificar username duplicado
        if db.query(Usuario).filter(Usuario.username == user_in.username).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Este nombre de usuario ya está registrado"
            )

        # Crear nuevo usuario
        db_user = Usuario(
            email=user_in.email,
            username=user_in.username,
            password=get_password_hash(user_in.password),
            rol=user_in.rol
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return db_user
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error al registrar usuario: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.post("/login", response_model=Token)
async def login_access_token(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Token:
    """
    OAuth2 compatible token login, devuelve un token de acceso JWT.
    
    Args:
        db: Sesión de base de datos
        form_data: Datos del formulario OAuth2
        
    Returns:
        Token: Token de acceso JWT
        
    Raises:
        HTTPException: Si las credenciales son inválidas o el usuario está inactivo
    """
    try:
        # Buscar usuario por email o username
        user = None
        if "@" in form_data.username:
            user = db.query(Usuario).filter(Usuario.email == form_data.username).first()
        else:
            user = db.query(Usuario).filter(Usuario.username == form_data.username).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not verificar_password(form_data.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.activo:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuario inactivo"
            )

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = crear_token_acceso(
            data={"sub": user.username, "rol": user.rol},
            expires_delta=access_token_expires
        )

        return Token(access_token=access_token, token_type="bearer")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )