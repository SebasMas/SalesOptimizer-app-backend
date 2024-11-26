from typing import Optional, List, Callable, Any
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from sqlalchemy.orm import Session
from functools import wraps
import logging

from app.core.security import verificar_token_acceso, SecurityError
from app.db.session import get_db
from app.models.usuario import Usuario

# Configuración del logger
logger = logging.getLogger(__name__)

# Configuración del esquema OAuth2
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="auth/login",
    scopes={
        "admin": "Acceso total al sistema",
        "vendedor": "Acceso a funciones de venta",
        "usuario": "Acceso básico"
    }
)

class AuthDependency:
    """
    Clase que proporciona las dependencias de autenticación y autorización.
    
    Esta clase implementa el patrón Singleton para asegurar una única instancia
    de las dependencias de autenticación en toda la aplicación.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AuthDependency, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Inicializa la instancia con la configuración necesaria."""
        self.oauth2_scheme = oauth2_scheme
        self._role_permissions = {
            "admin": ["admin", "vendedor", "usuario"],
            "vendedor": ["vendedor", "usuario"],
            "usuario": ["usuario"]
        }
    
    async def get_current_user(
        self,
        security_scopes: SecurityScopes,
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
    ) -> Usuario:
        """
        Obtiene el usuario actual basado en el token JWT y verifica sus permisos.
        
        Args:
            security_scopes (SecurityScopes): Scopes requeridos para la operación
            token (str): Token JWT de autenticación
            db (Session): Sesión de base de datos
            
        Returns:
            Usuario: Usuario autenticado y autorizado
            
        Raises:
            HTTPException: Si hay problemas de autenticación o autorización
        """
        try:
            if security_scopes.scopes:
                authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
            else:
                authenticate_value = "Bearer"
                
            credentials_exception = HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No se pudieron validar las credenciales",
                headers={"WWW-Authenticate": authenticate_value},
            )
            
            try:
                payload = verificar_token_acceso(token)
                username: str = payload.get("sub")
                if username is None:
                    raise credentials_exception
            except SecurityError as e:
                logger.error(f"Error al verificar token: {str(e)}")
                raise credentials_exception
                
            user = db.query(Usuario).filter(Usuario.username == username).first()
            if user is None:
                logger.warning(f"Usuario no encontrado: {username}")
                raise credentials_exception
                
            if not user.activo:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Usuario inactivo"
                )
                
            # Verificar permisos
            for scope in security_scopes.scopes:
                if scope not in self._role_permissions.get(user.rol, []):
                    logger.warning(
                        f"Usuario {username} intentó acceder a recurso sin permiso: {scope}"
                    )
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="No tiene suficientes permisos",
                        headers={"WWW-Authenticate": authenticate_value},
                    )
                    
            return user
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error no manejado en get_current_user: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno del servidor"
            )

    async def get_current_active_user(
        self,
        current_user: Usuario = Security(get_current_user, scopes=["usuario"])
    ) -> Usuario:
        """
        Verifica que el usuario actual esté activo.
        
        Args:
            current_user (Usuario): Usuario actual
            
        Returns:
            Usuario: Usuario activo verificado
            
        Raises:
            HTTPException: Si el usuario está inactivo
        """
        if not current_user.activo:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuario inactivo"
            )
        return current_user

def check_roles(roles: List[str]) -> Callable:
    """
    Decorador para verificar roles de usuario.
    
    Args:
        roles (List[str]): Lista de roles permitidos
        
    Returns:
        Callable: Decorador configurado
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, current_user: Usuario = Depends(AuthDependency().get_current_user), **kwargs: Any) -> Any:
            if current_user.rol not in roles:
                logger.warning(
                    f"Usuario {current_user.username} intentó acceder a recurso restringido"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="No tiene suficientes permisos para esta operación"
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
    Clase para verificación flexible de roles.
    
    Esta clase permite una verificación más granular de roles y permisos,
    útil para casos donde se necesita lógica de autorización compleja.
    """
    
    def __init__(self, allowed_roles: List[str]):
        """
        Inicializa el verificador de roles.
        
        Args:
            allowed_roles (List[str]): Lista de roles permitidos
        """
        self.allowed_roles = allowed_roles

    def __call__(self, user: Usuario = Depends(AuthDependency().get_current_user)) -> bool:
        """
        Verifica si el usuario tiene los roles permitidos.
        
        Args:
            user (Usuario): Usuario a verificar
            
        Returns:
            bool: True si el usuario tiene los permisos necesarios
            
        Raises:
            HTTPException: Si el usuario no tiene los permisos necesarios
        """
        if user.rol not in self.allowed_roles:
            logger.warning(
                f"Usuario {user.username} falló verificación de rol: {user.rol} no en {self.allowed_roles}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permisos suficientes para esta operación"
            )
        return True

# Instancia global de las dependencias de autenticación
auth_dependency = AuthDependency()