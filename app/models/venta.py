from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime

class Venta(Base):
    """
    Modelo que representa una venta en el sistema.

    Attributes:
        id (int): Identificador único de la venta.
        cliente_id (int): ID del cliente que realizó la compra.
        fecha_venta (datetime): Fecha y hora de la venta.
        total (float): Monto total de la venta.
        estado (str): Estado actual de la venta.
        cliente (relationship): Relación con el cliente que realizó la compra.
        detalles_venta (relationship): Relación con los detalles de la venta.
    """

    __tablename__ = "ventas"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    fecha_venta = Column(DateTime, default=datetime.utcnow)
    total = Column(Float, nullable=False)
    estado = Column(String, nullable=False)

    cliente = relationship("Cliente", back_populates="historial_compras")
    detalles_venta = relationship("DetalleVenta", back_populates="venta")

    def __repr__(self):
        return f"<Venta(id={self.id}, cliente_id={self.cliente_id}, fecha_venta='{self.fecha_venta}', total={self.total})>"