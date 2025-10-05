#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para realizar respaldo de los datos del sistema
"""

import os
import sys
import shutil
import datetime
from pathlib import Path
import zipfile

def main():
    print("=" * 80)
    print(" RESPALDO DEL SISTEMA DE ESTACIONAMIENTO ".center(80, "="))
    print("=" * 80 + "\n")
    
    # Obtener fecha actual para el nombre del respaldo
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    backup_filename = f"respaldo_estacionamiento_{timestamp}.zip"
    
    # Detectar la ubicación de los datos
    data_paths = []
    
    # Intentar con appdirs primero
    try:
        from appdirs import user_data_dir
        app_name = "SistemaEstacionamiento"
        app_author = "Parking"
        data_dir = Path(user_data_dir(app_name, app_author))
        if data_dir.exists():
            data_paths.append(data_dir)
            print(f"✅ Datos encontrados en ubicación de appdirs: {data_dir}")
    except ImportError:
        print("ℹ️ La biblioteca appdirs no está instalada.")
    
    # Añadir la ubicación relativa de respaldo
    script_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    relative_data_dir = script_dir / "data"
    if relative_data_dir.exists():
        data_paths.append(relative_data_dir)
        print(f"✅ Datos encontrados en ubicación relativa: {relative_data_dir}")
    
    if not data_paths:
        print("❌ No se encontraron directorios de datos para respaldar.")
        input("\nPresione Enter para continuar...")
        return
    
    # Crear el respaldo
    backup_path = script_dir / backup_filename
    
    try:
        print(f"\nCreando respaldo en: {backup_path}")
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Respaldar cada ubicación encontrada
            for data_dir in data_paths:
                print(f"\nRespaldando datos de: {data_dir}")
                for root, _, files in os.walk(data_dir):
                    for file in files:
                        if file.endswith('.txt'):
                            file_path = Path(root) / file
                            arcname = os.path.relpath(file_path, start=data_dir.parent)
                            print(f"  - Añadiendo: {arcname}")
                            zipf.write(file_path, arcname)
        
        print(f"\n✅ Respaldo creado exitosamente: {backup_path}")
    except Exception as e:
        print(f"\n❌ Error al crear respaldo: {e}")
    
    input("\nPresione Enter para continuar...")

if __name__ == "__main__":
    main()
