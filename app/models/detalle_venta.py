from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class DetalleVenta(Base):
    """
    Modelo que representa el detalle de una venta en el sistema.

    Attributes:
        id (int): Identificador único del detalle de venta.
        venta_id (int): ID de la venta a la que pertenece este detalle.
        producto_id (int): ID del producto vendido.
        cantidad (int): Cantidad del producto vendido.
        precio_unitario (float): Precio unitario del producto al momento de la venta.
        precio_promocion_recomendacion (float): Precio promocional si se aplicó una recomendación.
        venta (relationship): Relación con la venta a la que pertenece este detalle.
        producto (relationship): Relación con el producto vendido.
    """

    __tablename__ = "detalles_venta"

    id = Column(Integer, primary_key=True, index=True)
    venta_id = Column(Integer, ForeignKey("ventas.id"), nullable=False)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Float, nullable=False)
    precio_promocion_recomendacion = Column(Float)

    venta = relationship("Venta", back_populates="detalles_venta")
    producto = relationship("Producto", back_populates="detalles_venta")

    def __repr__(self):
        return f"<DetalleVenta(id={self.id}, venta_id={self.venta_id}, producto_id={self.producto_id}, cantidad={self.cantidad})>"