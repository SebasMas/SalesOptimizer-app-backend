import httpx
import random
from faker import Faker
from typing import List, Dict
import asyncio
from datetime import datetime, timedelta
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
        
        self.categorias = [
            "Electrónica", "Ropa", "Hogar", "Deportes", "Libros",
            "Juguetes", "Jardín", "Automotriz", "Oficina", "Mascotas"
        ]

    async def close(self):
        """Cierra el cliente HTTP."""
        await self.client.aclose()

    async def get_existing_productos(self) -> List[Dict]:
        """
        Obtiene los productos existentes en la base de datos.

        Returns:
            List[Dict]: Lista de productos existentes
        """
        try:
            response = await self.client.get(f"{self.base_url}/productos/")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error obteniendo productos existentes: {str(e)}")
            return []

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

    async def create_cliente(self) -> Dict:
        """
        Crea un cliente ficticio y lo envía a la API.

        Returns:
            Dict: Datos del cliente creado
        """
        try:
            cliente_data = {
                "nombre": self.faker.name(),
                "email": self.faker.email(),
                "telefono": self.faker.phone_number(),
            }

            response = await self.client.post(
                f"{self.base_url}/clientes/",
                json=cliente_data
            )
            response.raise_for_status()
            cliente_creado = response.json()
            logger.info(f"Cliente creado: {cliente_creado['nombre']}")
            return cliente_creado
        except httpx.HTTPError as e:
            logger.error(f"Error creando cliente: {str(e)}")
            raise

    async def create_venta(self, cliente_id: int, productos: List[Dict]) -> Dict:
        """
        Crea una venta con sus detalles.

        Args:
            cliente_id (int): ID del cliente
            productos (List[Dict]): Lista de productos disponibles

        Returns:
            Dict: Datos de la venta creada
        """
        try:
            # Seleccionar productos aleatorios para la venta (1-5 productos)
            productos_venta = random.sample(productos, min(random.randint(1, 5), len(productos)))
            
            # Calcular total y crear detalles
            detalles_venta = []
            total = 0
            
            for producto in productos_venta:
                cantidad = random.randint(1, 3)
                precio_unitario = producto['precio']
                subtotal = cantidad * precio_unitario
                total += subtotal
                
                detalles_venta.append({
                    "producto_id": producto['id'],
                    "cantidad": cantidad,
                    "precio_unitario": precio_unitario
                })

            # Crear datos de la venta
            venta_data = {
                "cliente_id": cliente_id,
                "total": round(total, 2),
                "estado": random.choice(['completada', 'pendiente', 'cancelada']),
                "detalles_venta": detalles_venta
            }

            response = await self.client.post(
                f"{self.base_url}/ventas/",
                json=venta_data
            )
            response.raise_for_status()
            venta_creada = response.json()
            logger.info(f"Venta creada para cliente {cliente_id}: ${total:.2f}")
            return venta_creada

        except httpx.HTTPError as e:
            logger.error(f"Error creando venta: {str(e)}")
            raise

    async def create_historial_compras(self, cliente_id: int, productos: List[Dict], num_ventas: int = None) -> List[Dict]:
        """
        Crea un historial de compras para un cliente.

        Args:
            cliente_id (int): ID del cliente
            productos (List[Dict]): Lista de productos disponibles
            num_ventas (int, optional): Número de ventas a crear. Si es None, será aleatorio entre 1-10

        Returns:
            List[Dict]: Lista de ventas creadas
        """
        if num_ventas is None:
            num_ventas = random.randint(1, 10)
            
        ventas = []
        for _ in range(num_ventas):
            try:
                venta = await self.create_venta(cliente_id, productos)
                ventas.append(venta)
                # Pequeña pausa para no sobrecargar la API
                await asyncio.sleep(0.1)
            except Exception as e:
                logger.error(f"Error creando historial de compras: {str(e)}")
                continue
        return ventas

    async def seed_data(self, num_usuarios: int = 10, num_productos: int = 30, num_clientes: int = 20):
        """
        Genera y envía múltiples registros a la API.

        Args:
            num_usuarios (int): Número de usuarios a crear
            num_productos (int): Número de productos a crear
            num_clientes (int): Número de clientes a crear
        """
        try:
            logger.info("Iniciando proceso de seeding...")

            # Obtener productos existentes o crear nuevos
            productos_existentes = await self.get_existing_productos()
            if not productos_existentes:
                # Crear productos solo si no existen
                productos_tasks = [self.create_producto() for _ in range(num_productos)]
                productos_creados = await asyncio.gather(*productos_tasks, return_exceptions=True)
                productos_existentes = [p for p in productos_creados if not isinstance(p, Exception)]

            # Crear clientes y su historial de compras
            clientes_tasks = [self.create_cliente() for _ in range(num_clientes)]
            clientes_creados = await asyncio.gather(*clientes_tasks, return_exceptions=True)
            clientes_exitosos = [c for c in clientes_creados if not isinstance(c, Exception)]

            # Crear historial de compras para cada cliente
            for cliente in clientes_exitosos:
                await self.create_historial_compras(cliente['id'], productos_existentes)

            logger.info(f"""
                Proceso completado:
                - Productos disponibles: {len(productos_existentes)}
                - Clientes creados: {len(clientes_exitosos)}
            """)

        except Exception as e:
            logger.error(f"Error general en seed_data: {str(e)}")
            raise
        finally:
            await self.close()

async def main():
    """Función principal para ejecutar el seeder."""
    try:
        seeder = DataSeeder()
        await seeder.seed_data(num_usuarios=10, num_productos=30, num_clientes=20)
        
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