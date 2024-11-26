import os
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de seguridad
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Contexto para el hashing de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class SecurityError(Exception):
    """
    Excepción personalizada para errores de seguridad.
    
    Attributes:
        message (str): Mensaje descriptivo del error
        status_code (int): Código de estado HTTP correspondiente
    """
    def __init__(self, message: str, status_code: int = status.HTTP_401_UNAUTHORIZED):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

def get_password_hash(password: str) -> str:
    """
    Genera un hash seguro de la contraseña proporcionada.
    
    Args:
        password (str): Contraseña en texto plano
        
    Returns:
        str: Hash de la contraseña
        
    Raises:
        SecurityError: Si ocurre un error durante el proceso de hashing
    """
    try:
        return pwd_context.hash(password)
    except Exception as e:
        raise SecurityError(
            f"Error al generar hash de contraseña: {str(e)}",
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )

def verificar_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si una contraseña coincide con su hash.
    
    Args:
        plain_password (str): Contraseña en texto plano
        hashed_password (str): Hash de la contraseña almacenado
        
    Returns:
        bool: True si la contraseña coincide, False en caso contrario
        
    Raises:
        SecurityError: Si ocurre un error durante la verificación
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        raise SecurityError(
            f"Error al verificar contraseña: {str(e)}",
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )

def crear_token_acceso(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un token JWT de acceso.
    
    Args:
        data (Dict[str, Any]): Datos a incluir en el token
        expires_delta (Optional[timedelta]): Tiempo de expiración del token
        
    Returns:
        str: Token JWT generado
        
    Raises:
        SecurityError: Si ocurre un error durante la generación del token
    """
    try:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
            
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except Exception as e:
        raise SecurityError(
            f"Error al crear token de acceso: {str(e)}",
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )

def verificar_token_acceso(token: str) -> Dict[str, Any]:
    """
    Verifica y decodifica un token JWT.
    
    Args:
        token (str): Token JWT a verificar
        
    Returns:
        Dict[str, Any]: Payload del token decodificado
        
    Raises:
        SecurityError: Si el token es inválido o ha expirado
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if not payload:
            raise SecurityError("No se pudo validar credenciales")
        return payload
    except JWTError as e:
        raise SecurityError(f"Token JWT inválido: {str(e)}")
    except Exception as e:
        raise SecurityError(
            f"Error al verificar token: {str(e)}",
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )

def validate_token_scopes(required_scopes: list[str], token_scopes: list[str]) -> bool:
    """
    Valida que el token tenga los scopes requeridos.
    
    Args:
        required_scopes (list[str]): Lista de scopes requeridos
        token_scopes (list[str]): Lista de scopes del token
        
    Returns:
        bool: True si el token tiene los scopes requeridos, False en caso contrario
    """
    return all(scope in token_scopes for scope in required_scopes)