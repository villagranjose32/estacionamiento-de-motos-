#!/bin/bash
echo "========================================"
echo "Sistema de Gestion de Estacionamiento"
echo "========================================"
echo ""
echo "Iniciando el sistema..."

# Obtener el directorio donde está el script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Verificar si existe el entorno virtual
if [ -f ".venv/bin/python" ]; then
    .venv/bin/python main.py
else
    echo ""
    echo "No se encontró el entorno virtual."
    echo ""
    echo "Por favor, ejecute primero el script de configuración:"
    echo "  python configurar.py"
    echo ""
    read -p "Presione Enter para continuar..."
fi
