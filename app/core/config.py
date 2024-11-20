from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache

class Settings(BaseSettings):
    """
    Configuraciones de la aplicación cargadas desde variables de entorno.
    
    Attributes:
        PROJECT_NAME (str): Nombre del proyecto
        DATABASE_USER (str): Usuario de la base de datos
        DATABASE_PASSWORD (str): Contraseña de la base de datos
        DATABASE_HOST (str): Host de la base de datos
        DATABASE_PORT (str): Puerto de la base de datos
        DATABASE_NAME (str): Nombre de la base de datos
        SECRET_KEY (str): Clave secreta para JWT
        ACCESS_TOKEN_EXPIRE_MINUTES (int): Tiempo de expiración del token en minutos
    """
    PROJECT_NAME: str = "SalesOptimizer"
    
    # Configuración de Base de datos
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_HOST: str
    DATABASE_PORT: str
    DATABASE_NAME: str
    
    # Configuración de seguridad
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    class Config:
        """
        Configuración de Pydantic para cargar variables de entorno.
        """
        env_file = ".env"
        case_sensitive = True

    @property
    def DATABASE_URL(self) -> str:
        """
        Construye y retorna la URL de conexión a la base de datos.
        
        Returns:
            str: URL de conexión a la base de datos
        """
        return f"postgresql://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"

@lru_cache()
def get_settings() -> Settings:
    """
    Retorna una instancia cacheada de las configuraciones.
    
    Returns:
        Settings: Instancia de configuraciones
    """
    return Settings()

# Instancia global de configuraciones
settings = get_settings()