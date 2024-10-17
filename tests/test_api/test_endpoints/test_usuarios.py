import pytest
from fastapi.testclient import TestClient
from app.main import app  # Asegúrar de importar tu aplicación FastAPI
from app.db.session import get_db
from app.models.usuario import Usuario as UsuarioModel
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate

client = TestClient(app)

@pytest.fixture(scope="module")
def test_db():
    # Aquí se debe crear una base de datos de prueba y configurarla
    yield  # Esto ejecuta las pruebas
    # Aquí se debe limpiar la base de datos de prueba

def test_create_usuario(test_db):
    response = client.post("/usuarios/", json={
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "securepassword",
        "rol": "user"
    })
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"

def test_read_usuarios(test_db):
    response = client.get("/usuarios/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_read_usuario(test_db):
    response = client.get("/usuarios/1")  # Asegúrar de que el ID 1 exista
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"

def test_update_usuario(test_db):
    response = client.put("/usuarios/1", json={"username": "updateduser"})
    assert response.status_code == 200
    assert response.json()["username"] == "updateduser"

def test_delete_usuario(test_db):
    response = client.delete("/usuarios/1")  # Asegúrar de que el ID 1 exista
    assert response.status_code == 200
    assert response.json()["username"] == "updateduser"  # Compruebar el usuario eliminado
