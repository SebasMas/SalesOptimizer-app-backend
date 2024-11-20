import pytest
from typing import Generator
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from app.db.base import Base, engine
from app.db.session import SessionLocal
from app.main import app, get_db

@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """
    Fixture que proporciona una sesión de base de datos para testing.
    Usa transacciones para aislar los tests y hacer rollback después de cada uno.
    """
    # Iniciar conexión y transacción
    connection = engine.connect()
    # Iniciar una transacción - esto asegura que podemos hacer rollback después
    transaction = connection.begin()
    
    # Crear una nueva sesión vinculada a esta conexión
    session = SessionLocal(bind=connection)
    
    try:
        yield session
    finally:
        # Asegurar que todo se limpia correctamente
        session.close()
        # Hacer rollback de la transacción - esto descarta todos los cambios
        transaction.rollback()
        # Cerrar la conexión
        connection.close()

@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """
    Fixture que proporciona un cliente de prueba de FastAPI.
    Configura la base de datos de prueba para cada test usando la sesión con transacción.
    
    Args:
        db_session (Session): Sesión de base de datos proporcionada por el fixture db_session
        
    Returns:
        Generator[TestClient, None, None]: Cliente de prueba de FastAPI
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass  # La limpieza se realiza en el fixture db_session

    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()