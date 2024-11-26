import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from app.core.security import get_password_hash, verificar_password
from app.models.usuario import Usuario
from app.main import app

# Configurar logging para los tests
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@pytest.mark.auth
class TestAuth:
    """Suite de pruebas para el sistema de autenticación."""

    def cleanup_test_users(self, db_session: Session):
        """
        Limpia solo los usuarios creados durante las pruebas.
        """
        test_emails = [
            "test.new@example.com",     # Para test_register_success
            "test.invalid@example.com",  # Para test_register_invalid_data
            "test.dup@example.com",      # Para test_register_duplicate_email
            "test.hash@example.com",     # Para test_password_is_hashed
            "test.login@example.com",    # Para tests de login
            "test.inactive@example.com", # Para test de usuario inactivo
        ]
        for email in test_emails:
            db_session.query(Usuario).filter(Usuario.email == email).delete()
        db_session.commit()

    @pytest.fixture(autouse=True)
    def setup_method(self, db_session: Session):
        """Limpia solo los usuarios de prueba antes y después de cada test."""
        self.cleanup_test_users(db_session)
        yield
        self.cleanup_test_users(db_session)

    def test_register_success(self, client: TestClient, db_session: Session):
        """Prueba el registro exitoso de un nuevo usuario."""
        response = client.post(
            "/auth/register",
            json={
                "email": "test.new@example.com",
                "username": "testnewuser",
                "password": "Test123!@#",
                "password_confirm": "Test123!@#",
                "rol": "usuario"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "test.new@example.com"
        assert data["username"] == "testnewuser"
        assert data["rol"] == "usuario"

    def test_register_invalid_data(self, client: TestClient):
        """Prueba el registro con datos inválidos."""
        response = client.post(
            "/auth/register",
            json={
                "email": "test.invalid@example.com",
                "username": "testinvalid",
                "password": "weak",
                "password_confirm": "weak",
                "rol": "usuario"
            }
        )
        assert response.status_code == 422

    def test_register_duplicate_email(self, client: TestClient, db_session: Session):
        """Prueba el registro con un email ya existente."""
        # Crear primer usuario
        response = client.post(
            "/auth/register",
            json={
                "email": "test.dup@example.com",
                "username": "testdup1",
                "password": "Test123!@#",
                "password_confirm": "Test123!@#",
                "rol": "usuario"
            }
        )
        assert response.status_code == 201

        # Intentar crear segundo usuario con el mismo email
        response = client.post(
            "/auth/register",
            json={
                "email": "test.dup@example.com",
                "username": "testdup2",
                "password": "Test123!@#",
                "password_confirm": "Test123!@#",
                "rol": "usuario"
            }
        )
        assert response.status_code == 400
        assert "email ya está registrado" in response.json()["detail"].lower()

    def test_password_is_hashed(self, client: TestClient, db_session: Session):
        """Verifica que las contraseñas se almacenen hasheadas."""
        # Registrar un nuevo usuario
        response = client.post(
            "/auth/register",
            json={
                "email": "test.hash@example.com",
                "username": "testhash",
                "password": "Test123!@#",
                "password_confirm": "Test123!@#",
                "rol": "usuario"
            }
        )
        logger.info(f"Register response status: {response.status_code}")
        if response.status_code != 201:
            logger.error(f"Register response body: {response.json()}")
        assert response.status_code == 201
        
        # Obtener el usuario de la base de datos
        user = db_session.query(Usuario).filter(Usuario.email == "test.hash@example.com").first()
        assert user is not None, "Usuario no encontrado en la base de datos"
        
        # Verificar que la contraseña almacenada NO sea igual a la contraseña en texto plano
        assert user.password != "Test123!@#", "La contraseña no está hasheada"
        
        # Verificar que la contraseña hasheada se pueda validar correctamente
        assert verificar_password("Test123!@#", user.password), "La contraseña no se puede verificar"
        
        # Verificar que una contraseña incorrecta no valide
        assert not verificar_password("WrongPassword123!", user.password), "La validación acepta contraseñas incorrectas"

    def test_login_success_with_username(self, client: TestClient, db_session: Session):
        """Prueba login exitoso usando nombre de usuario."""
        # Limpiar datos previos
        db_session.query(Usuario).filter(Usuario.email == "test.login@example.com").delete()
        db_session.commit()

        # Crear usuario de prueba
        user_data = {
            "email": "test.login@example.com",
            "username": "testlogin",
            "password": "Test123!@#",
            "password_confirm": "Test123!@#",
            "rol": "usuario"
        }
        
        # Registrar usuario
        response = client.post("/auth/register", json=user_data)
        logger.info(f"Register response status: {response.status_code}")
        logger.info(f"Register response body: {response.json()}")
        assert response.status_code == 201, f"Error en registro: {response.json()}"

        # Intentar login con username
        login_response = client.post(
            "/auth/login",
            data={
                "username": "testlogin",
                "password": "Test123!@#"
            }
        )
        
        logger.info(f"Login response status: {login_response.status_code}")
        logger.info(f"Login response body: {login_response.json()}")
        assert login_response.status_code == 200, f"Error en login: {login_response.json()}"
        data = login_response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    # """ def test_login_invalid_credentials(self, client: TestClient, db_session: Session):
    #     """Prueba login con credenciales inválidas."""
    #     # Limpiar datos previos
    #     db_session.query(Usuario).filter(Usuario.email == "test.login@example.com").delete()
    #     db_session.commit()

    #     # Crear usuario de prueba
    #     user_data = {
    #         "email": "test.login@example.com",
    #         "username": "testlogin",
    #         "password": "Test123!@#",
    #         "password_confirm": "Test123!@#",
    #         "rol": "usuario"
    #     }
        
    #     # Registrar usuario
    #     response = client.post("/auth/register", json=user_data)
    #     logger.info(f"Register response status: {response.status_code}")
    #     logger.info(f"Register response body: {response.json()}")
    #     assert response.status_code == 201, f"Error en registro: {response.json()}"

    #     # Intentar login con contraseña incorrecta
    #     login_response = client.post(
    #         "/auth/login",
    #         data={
    #             "username": "test.login@example.com",
    #             "password": "WrongPassword123!"
    #         }
    #     )
        
    #     logger.info(f"Invalid login response status: {login_response.status_code}")
    #     logger.info(f"Invalid login response body: {login_response.json()}")
    #     assert login_response.status_code == 401
    #     assert "Credenciales incorrectas" in login_response.json()["detail"]

    # def test_login_inactive_user(self, client: TestClient, db_session: Session):
    #     """Prueba login con usuario inactivo."""
    #     # Limpiar datos previos
    #     db_session.query(Usuario).filter(Usuario.email == "test.inactive@example.com").delete()
    #     db_session.commit()

    #     # Crear usuario inactivo directamente en la base de datos
    #     inactive_user = Usuario(
    #         email="test.inactive@example.com",
    #         username="testinactive",
    #         password=get_password_hash("Test123!@#"),
    #         rol="usuario",
    #         activo=False
    #     )
    #     db_session.add(inactive_user)
    #     db_session.commit()

    #     # Intentar login
    #     login_response = client.post(
    #         "/auth/login",
    #         data={
    #             "username": "test.inactive@example.com",
    #             "password": "Test123!@#"
    #         }
    #     )
        
    #     logger.info(f"Inactive user login response status: {login_response.status_code}")
    #     logger.info(f"Inactive user login response body: {login_response.json()}")
    #     assert login_response.status_code == 403, f"Expected 403 but got {login_response.status_code}"
    #     assert "Usuario inactivo" in login_response.json()["detail"] """

    def test_login_nonexistent_user(self, client: TestClient):
        """Prueba login con usuario que no existe."""
        login_response = client.post(
            "/auth/login",
            data={
                "username": "nonexistent@example.com",
                "password": "Test123!@#"
            }
        )
        
        logger.info(f"Nonexistent user login response status: {login_response.status_code}")
        logger.info(f"Nonexistent user login response body: {login_response.json()}")
        assert login_response.status_code == 401
        assert "Credenciales incorrectas" in login_response.json()["detail"]