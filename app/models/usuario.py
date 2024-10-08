from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from db.base import Base
from datetime import datetime

class Usuario(Base):
    """
    Modelo que representa a un usuario del sistema.

    Attributes:
        id (int): Identificador único del usuario.
        username (str): Nombre de usuario único.
        email (str): Correo electrónico del usuario.
        password (str): Contraseña hash del usuario.
        rol (str): Rol del usuario en el sistema.
        fecha_registro (datetime): Fecha y hora de registro del usuario.
        activo (bool): Indica si el usuario está activo en el sistema.
    """

    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    rol = Column(String, nullable=False)
    fecha_registro = Column(DateTime, default=datetime.utcnow)
    activo = Column(Boolean, default=True)

    def __repr__(self):
        return f"<Usuario(id={self.id}, username='{self.username}', email='{self.email}', rol='{self.rol}')>"