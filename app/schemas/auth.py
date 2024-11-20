# Importaciones necesarias
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime

class Token(BaseModel):
    """
    Schema para la respuesta del token JWT.
    
    Atributos:
        access_token (str): El token JWT de acceso
        token_type (str): El tipo de token (normalmente "bearer")
    """
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """
    Schema para los datos del payload del token JWT.
    
    Atributos:
        username: Optional[str]: El nombre de usuario almacenado en el token
        scopes: Optional[list[str]]: Lista de permisos (para uso futuro)
    """
    username: Optional[str] = None
    scopes: Optional[list[str]] = []

class UserLogin(BaseModel):
    """
    Schema para la solicitud de inicio de sesión del usuario.
    
    Atributos:
        email (EmailStr): Dirección de correo electrónico del usuario
        password (str): Contraseña del usuario (mínimo 8 caracteres)
    """
    email: EmailStr
    password: str = Field(..., min_length=8)

class UserRegister(BaseModel):
    """
    Schema para la solicitud de registro de usuario.
    
    Atributos:
        email (EmailStr): Dirección de correo electrónico del usuario
        username (str): Nombre de usuario
        password (str): Contraseña (mínimo 8 caracteres)
        password_confirm (str): Confirmación de contraseña
        rol (str): Rol del usuario en el sistema (admin, usuario o vendedor)
    """
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    password_confirm: str = Field(..., min_length=8)
    # El patrón asegura que solo se puedan asignar los roles permitidos
    rol: str = Field(..., pattern='^(admin|usuario|vendedor)$')

    @validator('password_confirm')
    def passwords_match(cls, v, values, **kwargs):
        """
        Valida que la contraseña y su confirmación coincidan.
        
        Args:
            v (str): El valor de confirmación de contraseña
            values (dict): Diccionario con los valores de otros campos
            
        Returns:
            str: El valor de confirmación de contraseña validado
            
        Raises:
            ValueError: Si las contraseñas no coinciden
        """
        if 'password' in values and v != values['password']:
            raise ValueError('Las contraseñas no coinciden')
        return v

class UserResponse(BaseModel):
    """
    Schema para la respuesta de datos de usuario (usado después del registro/login).
    
    Atributos:
        id (int): ID del usuario en la base de datos
        username (str): Nombre de usuario
        email (EmailStr): Dirección de correo electrónico
        rol (str): Rol del usuario en el sistema
        activo (bool): Indica si el usuario está activo
        fecha_registro (datetime): Fecha y hora de registro del usuario
    """
    id: int
    username: str
    email: EmailStr
    rol: str
    activo: bool
    fecha_registro: datetime

    class Config:
        """Configuración de Pydantic para el modelo."""
        from_attributes = True  # Permite la conversión desde atributos de instancia SQLAlchemy