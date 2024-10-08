from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime

class Cliente(Base):
    """
    Modelo que representa a un cliente en el sistema.

    Attributes:
        id (int): Identificador único del cliente.
        nombre (str): Nombre del cliente.
        email (str): Correo electrónico del cliente.
        telefono (str): Número de teléfono del cliente.
        fecha_registro (datetime): Fecha y hora de registro del cliente.
        activo (bool): Indica si el cliente está activo en el sistema.
        historial_compras (relationship): Relación con las ventas realizadas por el cliente.
    """

    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    telefono = Column(String)
    fecha_registro = Column(DateTime, default=datetime.utcnow)
    activo = Column(Boolean, default=True)

    historial_compras = relationship("Venta", back_populates="cliente")

    def __repr__(self):
        return f"<Cliente(id={self.id}, nombre='{self.nombre}', email='{self.email}')>"