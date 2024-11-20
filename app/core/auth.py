from typing import Optional, List
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from functools import wraps

from app.core.security import verificar_token_acceso, SecurityError
from app.db.session import get_db
from app.models.usuario import Usuario

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> Usuario:
    """
    Obtiene el usuario actual basado en el token JWT.
    
    Args:
        db (Session): Sesión de base de datos
        token (str): Token JWT de autenticación
        
    Returns:
        Usuario: Instancia del usuario actual
        
    Raises:
        HTTPException: Si el token es inválido o el usuario no existe
    """
    try:
        payload = verificar_token_acceso(token)
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No se pudo validar las credenciales",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except SecurityError as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=str(e.message),
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(Usuario).filter(Usuario.username == username).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    if not user.activo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo"
        )
    
    return user

async def get_current_active_user(
    current_user: Usuario = Depends(get_current_user)
) -> Usuario:
    """
    Verifica que el usuario actual esté activo.
    
    Args:
        current_user (Usuario): Usuario actual
        
    Returns:
        Usuario: Usuario validado
        
    Raises:
        HTTPException: Si el usuario está inactivo
    """
    if not current_user.activo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo"
        )
    return current_user

def check_roles(roles: List[str]):
    """
    Decorador para verificar roles de usuario.
    
    Args:
        roles (List[str]): Lista de roles permitidos
        
    Returns:
        Callable: Decorador de verificación de roles
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: Usuario = Depends(get_current_active_user), **kwargs):
            if current_user.rol not in roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="No tiene permisos suficientes para realizar esta acción"
                )
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator

# Decoradores predefinidos para roles comunes
require_admin = check_roles(["admin"])
require_vendedor = check_roles(["admin", "vendedor"])
require_usuario = check_roles(["admin", "vendedor", "usuario"])

class RoleChecker:
    """
    Clase para verificar roles de usuario de forma más flexible.
    
    Attributes:
        roles (List[str]): Lista de roles permitidos
    """
    def __init__(self, roles: List[str]):
        self.roles = roles

    def __call__(self, user: Usuario = Depends(get_current_active_user)) -> bool:
        """
        Verifica si el usuario tiene los roles requeridos.
        
        Args:
            user (Usuario): Usuario a verificar
            
        Returns:
            bool: True si el usuario tiene los permisos necesarios
            
        Raises:
            HTTPException: Si el usuario no tiene los permisos necesarios
        """
        if user.rol not in self.roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permisos suficientes para realizar esta acción"
            )
        return True

# Ejemplo de uso del RoleChecker:
# allow_create_users = RoleChecker(["admin"])
# @router.post("/users/", dependencies=[Depends(allow_create_users)])