from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from collections import defaultdict

from app.models.producto import Producto
from app.models.cliente import Cliente
from app.models.venta import Venta
from app.models.detalle_venta import DetalleVenta
from app.models.recomendacion import Recomendacion

class RecomendacionService:
    """
    Servicio para generar recomendaciones de productos basadas en el historial de compras
    y comportamiento de los clientes.
    """

    def __init__(self, db: Session):
        """
        Inicializa el servicio de recomendaciones.

        Args:
            db (Session): Sesión de base de datos SQLAlchemy.
        """
        self.db = db
        self.MIN_SCORE = 0.1
        self.MAX_RECOMMENDATIONS = 10

    def _get_client_purchase_history(self, cliente_id: int) -> List[Tuple[int, str]]:
        """
        Obtiene el historial de compras de un cliente.

        Args:
            cliente_id (int): ID del cliente

        Returns:
            List[Tuple[int, str]]: Lista de tuplas (producto_id, categoria)
        """
        return (
            self.db.query(Producto.id, Producto.categoria)
            .join(DetalleVenta)
            .join(Venta)
            .filter(Venta.cliente_id == cliente_id)
            .distinct()
            .all()
        )

    def _get_category_preferences(self, cliente_id: int) -> Dict[str, float]:
        """
        Calcula las preferencias de categorías del cliente basado en su historial.

        Args:
            cliente_id (int): ID del cliente

        Returns:
            Dict[str, float]: Diccionario de categorías y sus scores de preferencia
        """
        category_counts = defaultdict(int)
        purchases = self._get_client_purchase_history(cliente_id)
        total_purchases = len(purchases)

        if total_purchases == 0:
            return {}

        for _, category in purchases:
            category_counts[category] += 1

        return {
            category: count / total_purchases 
            for category, count in category_counts.items()
        }

    def _get_frequently_bought_together(self, producto_id: int) -> List[Tuple[int, float]]:
        """
        Encuentra productos que frecuentemente se compran juntos.

        Args:
            producto_id (int): ID del producto semilla

        Returns:
            List[Tuple[int, float]]: Lista de tuplas (producto_id, score)
        """
        # Obtener ventas que contienen el producto semilla
        ventas_con_producto = (
            self.db.query(Venta.id)
            .join(DetalleVenta)
            .filter(DetalleVenta.producto_id == producto_id)
            .subquery()
        )

        # Encontrar otros productos en esas mismas ventas
        productos_relacionados = (
            self.db.query(
                DetalleVenta.producto_id,
                func.count(DetalleVenta.producto_id).label('frequency')
            )
            .join(ventas_con_producto, DetalleVenta.venta_id == ventas_con_producto.c.id)
            .filter(DetalleVenta.producto_id != producto_id)
            .group_by(DetalleVenta.producto_id)
            .order_by(desc('frequency'))
            .all()
        )

        if not productos_relacionados:
            return []

        max_frequency = max(freq for _, freq in productos_relacionados)
        return [(prod_id, freq/max_frequency) for prod_id, freq in productos_relacionados]

    def _calculate_recommendation_score(
        self, 
        producto: Producto, 
        categoria_actual: Optional[str] = None,
        categoria_preferences: Optional[Dict[str, float]] = None,
        bought_together_scores: Optional[Dict[int, float]] = None
    ) -> float:
        """
        Calcula el score de recomendación para un producto.

        Args:
            producto (Producto): Producto a evaluar
            categoria_actual (Optional[str]): Categoría del producto semilla
            categoria_preferences (Optional[Dict[str, float]]): Preferencias de categoría
            bought_together_scores (Optional[Dict[int, float]]): Scores de productos comprados juntos

        Returns:
            float: Score de recomendación entre 0 y 1
        """
        score = 0.0
        weights = {
            'categoria': 0.4,
            'ventas': 0.3,
            'bought_together': 0.3
        }

        # Score por categoría
        if categoria_actual and producto.categoria == categoria_actual:
            score += weights['categoria']
        elif categoria_preferences and producto.categoria in categoria_preferences:
            score += weights['categoria'] * categoria_preferences[producto.categoria]

        # Score por ventas recientes
        if producto.ventas_ultimo_mes > 0:
            score += weights['ventas'] * min(producto.ventas_ultimo_mes / 100, 1)

        # Score por productos comprados juntos
        if bought_together_scores and producto.id in bought_together_scores:
            score += weights['bought_together'] * bought_together_scores[producto.id]

        return max(min(score, 1.0), self.MIN_SCORE)

    def generar_recomendaciones(
        self,
        cliente_id: int,
        producto_id: Optional[int] = None,
        limit: int = 5
    ) -> List[Dict]:
        """
        Genera recomendaciones de productos para un cliente.

        Args:
            cliente_id (int): ID del cliente
            producto_id (Optional[int]): ID del producto semilla (opcional)
            limit (int): Número máximo de recomendaciones

        Returns:
            List[Dict]: Lista de recomendaciones con scores

        Raises:
            ValueError: Si el cliente o producto no existe
        """
        try:
            # Verificar que el cliente existe
            cliente = self.db.query(Cliente).filter(Cliente.id == cliente_id).first()
            if not cliente:
                raise ValueError(f"Cliente {cliente_id} no encontrado")

            # Variables para el cálculo de scores
            categoria_actual = None
            bought_together_scores = {}
            categoria_preferences = self._get_category_preferences(cliente_id)

            # Si hay producto semilla, obtener su información
            if producto_id:
                producto_semilla = self.db.query(Producto).filter(Producto.id == producto_id).first()
                if not producto_semilla:
                    raise ValueError(f"Producto {producto_id} no encontrado")
                
                categoria_actual = producto_semilla.categoria
                productos_relacionados = self._get_frequently_bought_together(producto_id)
                bought_together_scores = dict(productos_relacionados)

            # Obtener productos candidatos
            productos_query = self.db.query(Producto).filter(Producto.stock > 0)
            if producto_id:
                productos_query = productos_query.filter(Producto.id != producto_id)

            productos = productos_query.all()

            # Calcular scores y ordenar recomendaciones
            recomendaciones = []
            for producto in productos:
                score = self._calculate_recommendation_score(
                    producto,
                    categoria_actual,
                    categoria_preferences,
                    bought_together_scores
                )

                recomendaciones.append({
                    'producto_id': producto.id,
                    'nombre': producto.nombre,
                    'categoria': producto.categoria,
                    'precio': producto.precio,
                    'score': score,
                    'baja_rotacion': producto.baja_rotacion
                })

            # Ordenar por score y limitar resultados
            recomendaciones.sort(key=lambda x: x['score'], reverse=True)
            recomendaciones = recomendaciones[:min(limit, self.MAX_RECOMMENDATIONS)]

            # Registrar recomendaciones en la base de datos
            for rec in recomendaciones:
                nueva_recomendacion = Recomendacion(
                    cliente_id=cliente_id,
                    producto_recomendado_id=rec['producto_id'],
                    score=rec['score'],
                    efectiva=False
                )
                self.db.add(nueva_recomendacion)
            
            self.db.commit()

            return recomendaciones

        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Error generando recomendaciones: {str(e)}")