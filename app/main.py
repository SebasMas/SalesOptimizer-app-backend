import logging
from logging.handlers import RotatingFileHandler
import sys
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect
from sqlalchemy.orm import Session

from app.models import cliente, detalle_venta, producto, recomendacion, usuario, venta
from app.db.base import engine, SessionLocal, Base
from app.api.endpoints import clientes, usuarios, productos, auth, ventas

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurar el manejador de archivos rotativo
file_handler = RotatingFileHandler('app.log', maxBytes=10240, backupCount=10)
file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
file_handler.setLevel(logging.INFO)

# Configurar el manejador de consola
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

# Añadir los manejadores al logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

app = FastAPI(title="SalesOptimizer API", version="0.1.0")

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar los orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(usuarios.router, prefix="/usuarios", tags=["usuarios"])
app.include_router(productos.router, prefix="/productos", tags=["productos"])
app.include_router(clientes.router, prefix="/clientes", tags=["clientes"])
app.include_router(ventas.router, prefix="/ventas", tags=["ventas"])

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_table_creation():
    """
    Verifica que todas las tablas del modelo de datos se hayan creado correctamente en la base de datos.
    """
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    expected_tables = [
        "usuarios",
        "clientes",
        "ventas",
        "productos",
        "detalles_venta",
        "recomendaciones"
    ]

    for table in expected_tables:
        if table in tables:
            logger.info(f"Tabla '{table}' creada correctamente.")
        else:
            logger.error(f"Tabla '{table}' no encontrada.")

    # Verificar columnas de la tabla productos
    columns = [column['name'] for column in inspector.get_columns('productos')]
    if 'baja_rotacion' in columns:
        logger.info("Campo 'baja_rotacion' encontrado en la tabla 'productos'.")
    else:
        logger.error("Campo 'baja_rotacion' no encontrado en la tabla 'productos'.")

@app.on_event("startup")
async def startup_event():
    """
    Evento que se ejecuta al iniciar la aplicación.
    Crea las tablas en la base de datos y verifica su estructura.
    """
    logger.info("Iniciando la aplicación...")
    Base.metadata.create_all(bind=engine)
    logger.info("Tablas creadas. Verificando estructura de la base de datos...")
    verify_table_creation()

@app.get("/")
def read_root():
    """
    Endpoint raíz que retorna un mensaje de bienvenida.
    
    Returns:
        dict: Mensaje de bienvenida
    """
    return {"message": "Bienvenido a SalesOptimizer API"}

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    """
    Endpoint para verificar el estado de la aplicación.
    
    Args:
        db (Session): Sesión de base de datos
        
    Returns:
        dict: Estado de la aplicación y la base de datos
        
    Raises:
        Exception: Si hay problemas con la base de datos
    """
    try:
        # Intenta hacer una consulta simple para verificar la conexión
        db.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Error de salud en la API: {str(e)}")
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    logger.info("Iniciando el servidor...")
    uvicorn.run(app, host="0.0.0.0", port=8000)