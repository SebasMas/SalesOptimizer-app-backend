import pytest
from fastapi.testclient import TestClient
from app.main import app  # Asegúrar de importar tu aplicación FastAPI
from app.db.session import get_db
from app.models.producto import Producto as ProductoModel
from app.schemas.producto import ProductoCreate, ProductoUpdate

client = TestClient(app)

@pytest.fixture(scope="module")
def test_db():
    # Aquí se debe crear una base de datos de prueba y configurarla
    yield  # Esto ejecuta las pruebas
    # Aquí se debe limpiar la base de datos de prueba

def test_create_producto(test_db):
    response = client.post("/productos/", json={
        "nombre": "testproduct",
        "descripcion": "A product for testing",
        "precio": 10.0,
        "stock": 100,
        "categoria": "test"
    })
    assert response.status_code == 200
    assert response.json()["nombre"] == "testproduct"

def test_read_productos(test_db):
    response = client.get("/productos/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_read_producto(test_db):
    response = client.get("/productos/1")  # Asegúrar de que el ID 1 exista
    assert response.status_code == 200
    assert response.json()["nombre"] == "testproduct"

def test_update_producto(test_db):
    response = client.put("/productos/1", json={"nombre": "updatedproduct"})
    assert response.status_code == 200
    assert response.json()["nombre"] == "updatedproduct"

def test_delete_producto(test_db):
    response = client.delete("/productos/1")  # Asegúrar de que el ID 1 exista
    assert response.status_code == 200
    assert response.json()["nombre"] == "updatedproduct"  # Compruebar el producto eliminado
