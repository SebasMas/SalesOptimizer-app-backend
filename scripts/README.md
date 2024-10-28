# Scripts de Utilidad

Este directorio contiene scripts de utilidad para el desarrollo y mantenimiento del proyecto.

## Seeder (seeder.py)

Script para poblar la base de datos con datos de prueba.

### Uso

```bash
# Desde la raíz del proyecto
python scripts/seeder.py
```

### Requisitos
- httpx
- faker

Los requisitos están incluidos en el requirements.txt principal del proyecto.

### Configuración

Por defecto, el script:
- Crea 10 usuarios con roles aleatorios
- Crea 30 productos con datos aleatorios
- Los logs se guardan en `logs/seeder.log`

Para modificar estos valores, editar las variables al final del script.