from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
from datetime import datetime

class TokenBase(BaseModel):
    """
    Schema base para tokens de autenticación.
    
    Attributes:
        token_type (str): Tipo de token (por defecto "bearer")
    """
    token_type: str = "bearer"

class Token(TokenBase):
    """
    Schema para la respuesta del token JWT.
    
    Attributes:
        access_token (str): Token JWT de acceso
    """
    access_token: str

class TokenData(BaseModel):
    """
    Schema para los datos contenidos en el token JWT.
    
    Attributes:
        username (Optional[str]): Nombre de usuario
        scopes (List[str]): Lista de permisos del usuario
    """
    username: Optional[str] = None
    scopes: List[str] = []

class UserAuthBase(BaseModel):
    """
    Schema base para autenticación de usuarios.
    
    Attributes:
        email (EmailStr): Email del usuario
    """
    email: EmailStr = Field(..., description="Email del usuario")

class UserLogin(UserAuthBase):
    """
    Schema para la solicitud de login.
    
    Attributes:
        password (str): Contraseña del usuario (mínimo 8 caracteres)
    """
    password: str = Field(
        ..., 
        min_length=8,
        description="Contraseña del usuario (mínimo 8 caracteres)"
    )

class UserRegister(UserAuthBase):
    """
    Schema para el registro de usuarios.
    
    Attributes:
        username (str): Nombre de usuario
        password (str): Contraseña del usuario
        password_confirm (str): Confirmación de contraseña
        rol (str): Rol del usuario (admin, usuario, vendedor)
    """
    username: str = Field(
        ..., 
        min_length=3,
        max_length=50,
        description="Nombre de usuario (entre 3 y 50 caracteres)"
    )
    password: str = Field(
        ..., 
        min_length=8,
        description="Contraseña (mínimo 8 caracteres)"
    )
    password_confirm: str = Field(
        ..., 
        min_length=8,
        description="Confirmación de contraseña"
    )
    rol: str = Field(
        ...,
        pattern='^(admin|usuario|vendedor)$',
        description="Rol del usuario (admin, usuario, vendedor)"
    )

    @field_validator('password')
    def validate_password_strength(cls, v: str) -> str:
        """
        Valida que la contraseña cumpla con los requisitos mínimos de seguridad.
        
        Args:
            v (str): Contraseña a validar
            
        Returns:
            str: Contraseña validada
            
        Raises:
            ValueError: Si la contraseña no cumple con los requisitos
        """
        if not any(char.isupper() for char in v):
            raise ValueError('La contraseña debe contener al menos una mayúscula')
        if not any(char.islower() for char in v):
            raise ValueError('La contraseña debe contener al menos una minúscula')
        if not any(char.isdigit() for char in v):
            raise ValueError('La contraseña debe contener al menos un número')
        if not any(not char.isalnum() for char in v):
            raise ValueError('La contraseña debe contener al menos un carácter especial')
        return v

    @model_validator(mode='after')
    def passwords_match(self) -> 'UserRegister':
        """
        Valida que la contraseña y su confirmación coincidan.
        
        Returns:
            UserRegister: Instancia validada
            
        Raises:
            ValueError: Si las contraseñas no coinciden
        """
        if self.password != self.password_confirm:
            raise ValueError('Las contraseñas no coinciden')
        return self

class UserResponse(BaseModel):
    """
    Schema para la respuesta con información del usuario.
    
    Attributes:
        id (int): ID del usuario
        username (str): Nombre de usuario
        email (EmailStr): Email del usuario
        rol (str): Rol del usuario
        activo (bool): Estado del usuario
        fecha_registro (datetime): Fecha de registro
    """
    id: int
    username: str
    email: EmailStr
    rol: str
    activo: bool
    fecha_registro: datetime

    class Config:
        """Configuración del modelo Pydantic."""
        from_attributes = True

class PasswordChange(BaseModel):
    """
    Schema para el cambio de contraseña.
    
    Attributes:
        old_password (str): Contraseña actual
        new_password (str): Nueva contraseña
        new_password_confirm (str): Confirmación de nueva contraseña
    """
    old_password: str = Field(..., min_length=8)
    new_password: str = Field(..., min_length=8)
    new_password_confirm: str = Field(..., min_length=8)

    @model_validator(mode='after')
    def passwords_match(self) -> 'PasswordChange':
        """
        Valida que la nueva contraseña y su confirmación coincidan.
        
        Returns:
            PasswordChange: Instancia validada
            
        Raises:
            ValueError: Si las contraseñas no coinciden
        """
        if self.new_password != self.new_password_confirm:
            raise ValueError('Las contraseñas no coinciden')
        if self.old_password == self.new_password:
            raise ValueError('La nueva contraseña debe ser diferente a la actual')
        return self