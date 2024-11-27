from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.db.session import get_db
from scripts.seeder import DataSeeder
import logging

router = APIRouter(tags=["seeding"])
logger = logging.getLogger(__name__)

is_seeding = False

@router.post("/seed")
async def seed_database(
    background_tasks: BackgroundTasks,
    force: bool = False,
    num_usuarios: int = 10,
    num_productos: int = 30,
    num_clientes: int = 20,
    db: Session = Depends(get_db)
):
    """
    Endpoint para poblar la base de datos con datos de prueba.
    
    Args:
        background_tasks: Tareas en segundo plano
        force: Si es True, permite repoblar incluso si ya hay datos
        num_usuarios: Número de usuarios a crear
        num_productos: Número de productos a crear
        num_clientes: Número de clientes a crear
        db: Sesión de base de datos
    """
    global is_seeding
    
    try:
        if is_seeding:
            return {"message": "Ya hay un proceso de seeding en ejecución"}

        if not force:
            has_data = db.execute("SELECT 1 FROM usuarios LIMIT 1").scalar()
            if has_data:
                return {"message": "La base de datos ya contiene datos. Usa force=true para sobrescribir"}

        async def seed_task():
            global is_seeding
            try:
                is_seeding = True
                seeder = DataSeeder()
                await seeder.seed_data(
                    num_usuarios=num_usuarios,
                    num_productos=num_productos,
                    num_clientes=num_clientes
                )
                logger.info("Seeding completado exitosamente")
            except Exception as e:
                logger.error(f"Error durante el seeding: {str(e)}")
            finally:
                is_seeding = False

        background_tasks.add_task(seed_task)
        
        return {
            "message": "Proceso de seeding iniciado",
            "configuracion": {
                "usuarios": num_usuarios,
                "productos": num_productos,
                "clientes": num_clientes
            }
        }
        
    except Exception as e:
        logger.error(f"Error iniciando seeding: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/seed/status")
async def get_seed_status():
    """Retorna el estado actual del proceso de seeding."""
    return {"is_running": is_seeding}