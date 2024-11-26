import os
import pytest
import logging
from typing import Generator
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from dotenv import load_dotenv

# Configuración específica de logging para tests
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Solo usar StreamHandler para tests
    ]
)

# Cargar variables de entorno de prueba
load_dotenv(".env.test")

# Importar después de cargar variables de entorno
from app.db.base import Base
from app.main import app, get_db

# Crear engine de prueba
SQLALCHEMY_DATABASE_URL = (
    f"postgresql://{os.getenv('DATABASE_USER')}:{os.getenv('DATABASE_PASSWORD')}"
    f"@{os.getenv('DATABASE_HOST')}:{os.getenv('DATABASE_PORT')}/{os.getenv('DATABASE_NAME')}"
)

engine_test = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """
    Fixture que se ejecuta una vez por sesión de pruebas.
    Crea todas las tablas necesarias y las elimina al finalizar.
    """
    Base.metadata.create_all(bind=engine_test)
    yield
    Base.metadata.drop_all(bind=engine_test)

@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """
    Fixture que proporciona una sesión de base de datos para testing.
    Usa transacciones para aislar los tests y hacer rollback después de cada uno.
    """
    connection = engine_test.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    # Comenzar un savepoint
    nested = connection.begin_nested()

    # Si la sesión detecta un rollback, volver al savepoint
    @event.listens_for(session, "after_transaction_end")
    def end_savepoint(session, transaction):
        nonlocal nested
        if not nested.is_active:
            nested = connection.begin_nested()

    yield session

    # Rollback y cierre
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """
    Fixture que proporciona un cliente de prueba de FastAPI.
    
    Args:
        db_session (Session): Sesión de base de datos proporcionada por el fixture db_session
        
    Yields:
        TestClient: Cliente de prueba de FastAPI
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()

#hola