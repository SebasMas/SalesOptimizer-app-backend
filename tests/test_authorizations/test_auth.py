import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verificar_password
from app.models.usuario import Usuario
from app.main import app

@pytest.mark.authorizations
class TestAuth:
    """
    Suite de pruebas para el sistema de autenticación.
    """
    
    def test_register_user(self, client: TestClient, db_session: Session):
        """
        Prueba el registro exitoso de un nuevo usuario.
        
        Args:
            client (TestClient): Cliente de pruebas de FastAPI
            db_session (Session): Sesión de base de datos para pruebas
        """
        response = client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "username": "testuser",
                "password": "testpassword123",
                "password_confirm": "testpassword123",
                "rol": "usuario"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["username"] == "testuser"
        assert data["rol"] == "usuario"
        assert data["activo"] is True

        # Verificar que el usuario se guardó en la base de datos
        user = db_session.query(Usuario).filter(Usuario.email == "test@example.com").first()
        assert user is not None
        assert verificar_password("testpassword123", user.password)

    def test_register_duplicate_email(self, client: TestClient, db_session: Session):
        """
        Prueba el intento de registro con un email duplicado.
        
        Args:
            client (TestClient): Cliente de pruebas de FastAPI
            db_session (Session): Sesión de base de datos para pruebas
        """
        # Crear usuario inicial
        user = Usuario(
            email="test@example.com",
            username="existinguser",
            password=get_password_hash("password123"),
            rol="usuario"
        )
        db_session.add(user)
        db_session.commit()

        # Intentar registrar usuario con el mismo email
        response = client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "username": "newuser",
                "password": "testpassword123",
                "password_confirm": "testpassword123",
                "rol": "usuario"
            }
        )
        assert response.status_code == 400
        assert "email ya está registrado" in response.json()["detail"]

    def test_register_invalid_role(self, client: TestClient):
        """
        Prueba el intento de registro con un rol inválido.
        
        Args:
            client (TestClient): Cliente de pruebas de FastAPI
        """
        response = client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "username": "testuser",
                "password": "testpassword123",
                "password_confirm": "testpassword123",
                "rol": "rol_invalido"
            }
        )
        assert response.status_code == 422

    def test_login_success(self, client: TestClient, db_session: Session):
        """
        Prueba el login exitoso y la obtención del token JWT.
        
        Args:
            client (TestClient): Cliente de pruebas de FastAPI
            db_session (Session): Sesión de base de datos para pruebas
        """
        # Crear usuario de prueba
        user = Usuario(
            email="test@example.com",
            username="testuser",
            password=get_password_hash("testpassword123"),
            rol="usuario"
        )
        db_session.add(user)
        db_session.commit()

        # Probar login con email
        response = client.post(
            "/auth/login",
            data={
                "username": "test@example.com",
                "password": "testpassword123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

        # Probar login con username
        response = client.post(
            "/auth/login",
            data={
                "username": "testuser",
                "password": "testpassword123"
            }
        )
        assert response.status_code == 200
        assert "access_token" in response.json()

    def test_get_current_user(self, client: TestClient, db_session: Session):
        """
        Prueba la obtención de información del usuario actual.
        
        Args:
            client (TestClient): Cliente de pruebas de FastAPI
            db_session (Session): Sesión de base de datos para pruebas
        """
        # Crear usuario y obtener token
        user = Usuario(
            email="test@example.com",
            username="testuser",
            password=get_password_hash("testpassword123"),
            rol="usuario"
        )
        db_session.add(user)
        db_session.commit()

        # Login para obtener token
        response = client.post(
            "/auth/login",
            data={
                "username": "test@example.com",
                "password": "testpassword123"
            }
        )
        token = response.json()["access_token"]

        # Obtener información del usuario actual
        response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["username"] == "testuser"

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, db_session: Session):
        """
        Fixture para configuración y limpieza antes y después de cada prueba.
        
        Args:
            db_session (Session): Sesión de base de datos para pruebas
        """
        # Setup - si se necesita alguna configuración inicial
        yield
        # Teardown - limpieza después de cada prueba
        db_session.query(Usuario).delete()
        db_session.commit()