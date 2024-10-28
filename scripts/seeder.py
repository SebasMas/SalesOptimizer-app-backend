import httpx
import random
from faker import Faker
from typing import List, Dict
import asyncio
from datetime import datetime
import logging
from pathlib import Path
import sys

# Añadir el directorio raíz del proyecto al PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('seeder.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DataSeeder:
    """
    Clase para generar y enviar datos ficticios a los endpoints de la API.

    Attributes:
        base_url (str): URL base de la API
        faker (Faker): Instancia de Faker para generar datos ficticios
        client (httpx.AsyncClient): Cliente HTTP asíncrono
    """

    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Inicializa el generador de datos.

        Args:
            base_url (str): URL base de la API
        """
        self.base_url = base_url
        self.faker = Faker(['es_ES'])  # Usar locale español
        self.client = httpx.AsyncClient(timeout=30.0)
        
        # Categorías de productos para usar en la generación
        self.categorias = [
            "Electrónica", "Ropa", "Hogar", "Deportes", "Libros",
            "Juguetes", "Jardín", "Automotriz", "Oficina", "Mascotas"
        ]

    async def close(self):
        """Cierra el cliente HTTP."""
        await self.client.aclose()

    async def create_usuario(self) -> Dict:
        """
        Crea un usuario ficticio y lo envía a la API.

        Returns:
            Dict: Datos del usuario creado
        
        Raises:
            httpx.HTTPError: Si hay un error en la petición HTTP
        """
        try:
            usuario_data = {
                "username": self.faker.user_name(),
                "email": self.faker.email(),
                "password": "password123",  # En un caso real, usar contraseñas seguras
                "rol": random.choice(["admin", "vendedor", "supervisor"]),
            }

            response = await self.client.post(
                f"{self.base_url}/usuarios/",
                json=usuario_data
            )
            response.raise_for_status()
            usuario_creado = response.json()
            logger.info(f"Usuario creado: {usuario_creado['username']}")
            return usuario_creado

        except httpx.HTTPError as e:
            logger.error(f"Error creando usuario: {str(e)}")
            raise

    async def create_producto(self) -> Dict:
        """
        Crea un producto ficticio y lo envía a la API.

        Returns:
            Dict: Datos del producto creado
        
        Raises:
            httpx.HTTPError: Si hay un error en la petición HTTP
        """
        try:
            producto_data = {
                "nombre": self.faker.catch_phrase(),
                "descripcion": self.faker.text(max_nb_chars=200),
                "precio": round(random.uniform(10.0, 1000.0), 2),
                "stock": random.randint(0, 100),
                "categoria": random.choice(self.categorias),
                "ventas_ultimo_mes": random.randint(0, 50),
                "baja_rotacion": random.choice([True, False])
            }

            response = await self.client.post(
                f"{self.base_url}/productos/",
                json=producto_data
            )
            response.raise_for_status()
            producto_creado = response.json()
            logger.info(f"Producto creado: {producto_creado['nombre']}")
            return producto_creado

        except httpx.HTTPError as e:
            logger.error(f"Error creando producto: {str(e)}")
            raise

    async def seed_data(self, num_usuarios: int = 10, num_productos: int = 30):
        """
        Genera y envía múltiples usuarios y productos a la API.

        Args:
            num_usuarios (int): Número de usuarios a crear
            num_productos (int): Número de productos a crear
        """
        try:
            logger.info(f"Iniciando la generación de {num_usuarios} usuarios y {num_productos} productos...")
            
            # Crear usuarios
            usuarios_tasks = [self.create_usuario() for _ in range(num_usuarios)]
            usuarios_creados = await asyncio.gather(*usuarios_tasks, return_exceptions=True)
            
            usuarios_exitosos = [u for u in usuarios_creados if not isinstance(u, Exception)]
            logger.info(f"Usuarios creados exitosamente: {len(usuarios_exitosos)}/{num_usuarios}")

            # Crear productos
            productos_tasks = [self.create_producto() for _ in range(num_productos)]
            productos_creados = await asyncio.gather(*productos_tasks, return_exceptions=True)
            
            productos_exitosos = [p for p in productos_creados if not isinstance(p, Exception)]
            logger.info(f"Productos creados exitosamente: {len(productos_exitosos)}/{num_productos}")

        except Exception as e:
            logger.error(f"Error general en seed_data: {str(e)}")
            raise
        finally:
            await self.close()

async def main():
    """Función principal para ejecutar el seeder."""
    try:
        seeder = DataSeeder()
        await seeder.seed_data(num_usuarios=10, num_productos=30)
        
    except Exception as e:
        logger.error(f"Error en la ejecución principal: {str(e)}")
        raise

if __name__ == "__main__":
    # Crear directorio de logs si no existe
    Path("logs").mkdir(exist_ok=True)
    
    # Ejecutar el seeder
    start_time = datetime.now()
    logger.info("Iniciando proceso de seeding...")
    
    asyncio.run(main())
    
    end_time = datetime.now()
    duration = end_time - start_time
    logger.info(f"Proceso completado en {duration.total_seconds():.2f} segundos")