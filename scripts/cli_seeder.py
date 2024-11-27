#!/usr/bin/env python
import click
import asyncio
import logging
from pathlib import Path
from datetime import datetime
import sys
import os

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Añadir el directorio raíz del proyecto al PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from scripts.seeder import DataSeeder

@click.command()
@click.option('--usuarios', default=10, help='Número de usuarios a crear')
@click.option('--productos', default=30, help='Número de productos a crear')
@click.option('--clientes', default=20, help='Número de clientes a crear')
@click.option('--url', default=None, help='URL base de la API')
def seed_data(usuarios, productos, clientes, url):
    """Script para poblar la base de datos con datos de prueba."""
    try:
        # Si se proporciona URL, usarla, sino usar valor por defecto
        base_url = url or os.getenv('API_URL', 'http://localhost:8000')
        logger.info(f"Iniciando proceso de seeding en {base_url}")
        
        start_time = datetime.now()
        seeder = DataSeeder(base_url=base_url)
        
        # Ejecutar el seeder
        asyncio.run(seeder.seed_data(
            num_usuarios=usuarios,
            num_productos=productos,
            num_clientes=clientes
        ))
        
        end_time = datetime.now()
        duration = end_time - start_time
        logger.info(f"Proceso completado en {duration.total_seconds():.2f} segundos")
        
    except Exception as e:
        logger.error(f"Error durante el seeding: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    seed_data()