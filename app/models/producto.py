from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime

class Producto(Base):
    """
    Modelo que representa un producto en el sistema.

    Attributes:
        id (int): Identificador único del producto.
        nombre (str): Nombre del producto.
        descripcion (str): Descripción detallada del producto.
        precio (float): Precio actual del producto.
        stock (int): Cantidad disponible en inventario.
        categoria (str): Categoría a la que pertenece el producto.
        fecha_creacion (datetime): Fecha y hora de creación del producto.
        ventas_ultimo_mes (int): Número de ventas en el último mes.
        baja_rotacion (bool): Indica si el producto tiene baja rotación.
    """
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True, nullable=False)
    descripcion = Column(String)
    precio = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False)
    categoria = Column(String, index=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    ventas_ultimo_mes = Column(Integer, default=0)
    baja_rotacion = Column(Boolean, default=False)

    detalles_venta = relationship("DetalleVenta", back_populates="producto")
    recomendaciones = relationship("Recomendacion", back_populates="producto_recomendado")  # Cambiado aquí (antes back_populates="producto")

    def __repr__(self):
        return f"<Producto(id={self.id}, nombre='{self.nombre}', precio={self.precio}, stock={self.stock})>"
