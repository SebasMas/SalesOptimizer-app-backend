from sqlalchemy import Column, Integer, Float, DateTime, Boolean, ForeignKey, String
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime

class Recomendacion(Base):
    """
    Modelo que representa una recomendación de producto para un cliente en el sistema.

    Attributes:
        id (int): Identificador único de la recomendación.
        cliente_id (int): ID del cliente para el que se genera la recomendación.
        producto_recomendado_id (int): ID del producto recomendado.
        fecha_recomendacion (datetime): Fecha y hora en que se generó la recomendación.
        score (float): Puntuación o relevancia de la recomendación.
        efectiva (bool): Indica si la recomendación resultó en una venta.
        cliente (relationship): Relación con el cliente para el que se generó la recomendación.
        producto_recomendado (relationship): Relación con el producto recomendado.
    """

    __tablename__ = "recomendaciones"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    producto_recomendado_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    fecha_recomendacion = Column(DateTime, default=datetime.utcnow)
    score = Column(Float, nullable=False)
    efectiva = Column(Boolean, default=False)
    cliente = relationship("Cliente", back_populates="recomendaciones")
    producto_recomendado = relationship("Producto", back_populates="recomendaciones")

    def __repr__(self):
        return f"<Recomendacion(id={self.id}, cliente_id={self.cliente_id}, producto_recomendado_id={self.producto_recomendado_id}, score={self.score}, efectiva={self.efectiva})>"