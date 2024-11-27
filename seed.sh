#!/bin/bash

# Activar el entorno virtual si es necesario
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Asegurarse de que los requerimientos están instalados
pip install -r requirements.txt

# Ejecutar el seeder
python scripts/cli_seeder.py --url $RENDER_EXTERNAL_URL

# Verificar el resultado
if [ $? -eq 0 ]; then
    echo "✅ Seeding completado exitosamente"
    exit 0
else
    echo "❌ Error durante el seeding"
    exit 1
fi