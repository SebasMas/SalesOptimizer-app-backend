import pytest
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.models.cliente import Cliente
from app.models.producto import Producto
from app.models.venta import Venta
from app.models.detalle_venta import DetalleVenta
from app.services.recomendacion.sistema_recomendaciones import RecomendacionService

@pytest.fixture
def setup_test_data(db_session: Session):
    """
    Fixture que crea datos de prueba necesarios para los tests.
    Incluye productos, clientes y algunas ventas.
    """
    # Crear productos de prueba
    productos = [
        Producto(
            nombre=f"Producto {i}",
            precio=100.0 * i,
            stock=50,
            categoria="categoria1" if i < 3 else "categoria2",
            ventas_ultimo_mes=10 if i < 2 else 5
        ) for i in range(1, 5)
    ]
    for p in productos:
        db_session.add(p)
    
    # Crear cliente de prueba
    cliente = Cliente(
        nombre="Cliente Test",
        email="test@example.com",
        telefono="1234567890"
    )
    db_session.add(cliente)
    db_session.commit()

    # Crear algunas ventas para el historial
    venta = Venta(
        cliente_id=cliente.id,
        total=300.0,
        estado="completada",
        fecha_venta=datetime.utcnow() - timedelta(days=5)
    )
    db_session.add(venta)
    db_session.commit()

    # Agregar detalles de venta
    detalles = [
        DetalleVenta(
            venta_id=venta.id,
            producto_id=productos[0].id,
            cantidad=2,
            precio_unitario=100.0
        ),
        DetalleVenta(
            venta_id=venta.id,
            producto_id=productos[1].id,
            cantidad=1,
            precio_unitario=200.0
        )
    ]
    for d in detalles:
        db_session.add(d)
    db_session.commit()

    return {
        'cliente': cliente,
        'productos': productos,
        'venta': venta
    }

def test_get_client_purchase_history(db_session: Session, setup_test_data):
    """
    Test unitario que verifica la obtención correcta del historial de compras de un cliente.
    """
    servicio = RecomendacionService(db_session)
    cliente = setup_test_data['cliente']
    
    historial = servicio._get_client_purchase_history(cliente.id)
    assert len(historial) == 2  # Debe haber dos productos en el historial
    assert all(isinstance(item[0], int) and isinstance(item[1], str) for item in historial)

def test_calculate_recommendation_score(db_session: Session, setup_test_data):
    """
    Test unitario que verifica el cálculo correcto del score de recomendación.
    """
    servicio = RecomendacionService(db_session)
    producto = setup_test_data['productos'][0]
    
    # Probar con diferentes combinaciones de parámetros
    score1 = servicio._calculate_recommendation_score(
        producto,
        categoria_actual="categoria1",
        categoria_preferences={"categoria1": 0.7},
        bought_together_scores={producto.id: 0.8}
    )
    assert 0 <= score1 <= 1  # El score debe estar entre 0 y 1
    
    # Probar sin categoría actual
    score2 = servicio._calculate_recommendation_score(
        producto,
        categoria_preferences={"categoria1": 0.7}
    )
    assert 0 <= score2 <= 1
    assert score2 < score1  # Debería ser menor sin la coincidencia de categoría actual

def test_generar_recomendaciones_integration(db_session: Session, setup_test_data):
    """
    Test de integración que verifica el flujo completo de generación de recomendaciones.
    """
    servicio = RecomendacionService(db_session)
    cliente = setup_test_data['cliente']
    
    # Probar generación de recomendaciones sin producto semilla
    recomendaciones = servicio.generar_recomendaciones(
        cliente_id=cliente.id,
        limit=3
    )
    
    assert isinstance(recomendaciones, list)
    assert len(recomendaciones) <= 3
    for rec in recomendaciones:
        assert all(key in rec for key in ['producto_id', 'nombre', 'score', 'baja_rotacion'])
        assert 0 <= rec['score'] <= 1

def test_generar_recomendaciones_cliente_inexistente(db_session: Session):
    """
    Test unitario que verifica el manejo correcto de errores cuando se intenta generar
    recomendaciones para un cliente que no existe.
    """
    servicio = RecomendacionService(db_session)
    
    with pytest.raises(ValueError) as excinfo:
        servicio.generar_recomendaciones(cliente_id=99999)
    assert "Cliente 99999 no encontrado" in str(excinfo.value)