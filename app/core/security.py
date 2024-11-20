from datetime import datetime, timedelta
from typing import Any, Union, Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, status
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de seguridad
SECRET_KEY = os.getenv("SECRET_KEY") or "SOB2024"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Configuración de la encriptación de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuración del esquema OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

class SecurityError(Exception):
    """
    Clase base para excepciones de seguridad.
    
    Attributes:
        message (str): Mensaje de error
        status_code (int): Código de estado HTTP
    """
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

def verificar_password(password_plano: str, password_hash: str) -> bool:
    """
    Verifica si una contraseña en texto plano coincide con su hash.
    
    Args:
        password_plano (str): Contraseña en texto plano a verificar
        password_hash (str): Hash de la contraseña almacenada
        
    Returns:
        bool: True si la contraseña coincide, False en caso contrario
    """
    try:
        return pwd_context.verify(password_plano, password_hash)
    except Exception as e:
        raise SecurityError(
            message="Error al verificar la contraseña",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        ) from e

def get_password_hash(password: str) -> str:
    """
    Genera el hash de una contraseña.
    
    Args:
        password (str): Contraseña en texto plano
        
    Returns:
        str: Hash de la contraseña
        
    Raises:
        SecurityError: Si hay un error al generar el hash
    """
    try:
        return pwd_context.hash(password)
    except Exception as e:
        raise SecurityError(
            message="Error al generar el hash de la contraseña",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        ) from e

def crear_token_acceso(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un token JWT de acceso.
    
    Args:
        data (dict): Datos a codificar en el token
        expires_delta (Optional[timedelta]): Tiempo de expiración del token
        
    Returns:
        str: Token JWT generado
        
    Raises:
        SecurityError: Si hay un error al crear el token
    """
    try:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except Exception as e:
        raise SecurityError(
            message="Error al crear el token de acceso",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        ) from e

def verificar_token_acceso(token: str) -> dict:
    """
    Verifica y decodifica un token JWT.
    
    Args:
        token (str): Token JWT a verificar
        
    Returns:
        dict: Datos decodificados del token
        
    Raises:
        SecurityError: Si el token es inválido o ha expirado
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise SecurityError(
                message="Token de acceso inválido",
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        return payload
    except JWTError as e:
        raise SecurityError(
            message="Token de acceso inválido o expirado",
            status_code=status.HTTP_401_UNAUTHORIZED
        ) from e

def get_token_data(token: str) -> dict[str, Any]:
    """
    Obtiene los datos almacenados en un token JWT.
    
    Args:
        token (str): Token JWT
        
    Returns:
        dict[str, Any]: Datos almacenados en el token
        
    Raises:
        SecurityError: Si hay un error al decodificar el token
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        raise SecurityError(
            message="Error al decodificar el token",
            status_code=status.HTTP_401_UNAUTHORIZED
        ) from e