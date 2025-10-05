#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para mostrar la ubicación de los datos del sistema
"""

import os
import sys
from pathlib import Path

def main():
    print("=" * 80)
    print(" UBICACIÓN DE LOS DATOS DEL SISTEMA ".center(80, "="))
    print("=" * 80 + "\n")
    
    # Intentar importar appdirs
    try:
        from appdirs import user_data_dir
        app_name = "SistemaEstacionamiento"
        app_author = "Parking"
        data_dir = Path(user_data_dir(app_name, app_author))
        
        print(f"✅ Biblioteca appdirs encontrada")
        print(f"✅ Ubicación de datos: {data_dir}")
        
        # Verificar si existen los directorios y archivos
        default_dir = data_dir / "default"
        if default_dir.exists():
            print(f"✅ Directorio de sede predeterminada: {default_dir}")
            
            # Listar archivos
            print("\nArchivos encontrados:")
            for file in default_dir.glob("*.txt"):
                size = file.stat().st_size
                print(f"  - {file.name} ({size} bytes)")
        else:
            print(f"❌ El directorio de sede no existe: {default_dir}")
            print("   Ejecute configurar.py para crear los directorios necesarios")
        
    except ImportError:
        # Si appdirs no está instalado, mostrar ubicación alternativa
        print("❌ La biblioteca appdirs no está instalada.")
        print("   El sistema está usando ubicaciones relativas.")
        
        # Obtener la ruta del script principal
        if getattr(sys, 'frozen', False):
            # Si es un ejecutable congelado (PyInstaller)
            app_path = os.path.dirname(sys.executable)
        else:
            # Si es un script Python normal
            app_path = os.path.dirname(os.path.abspath(sys.argv[0]))
        
        # Usar subdirectorio 'data' en la carpeta del ejecutable/script
        data_dir = Path(os.path.join(app_path, "data"))
        default_dir = data_dir / "default"
        
        print(f"\nUbicación de datos (relativa): {data_dir}")
        
        if default_dir.exists():
            print(f"✅ Directorio de sede predeterminada: {default_dir}")
            
            # Listar archivos
            print("\nArchivos encontrados:")
            for file in default_dir.glob("*.txt"):
                size = file.stat().st_size
                print(f"  - {file.name} ({size} bytes)")
        else:
            print(f"❌ El directorio de sede no existe: {default_dir}")
    
    print("\nPara instalar appdirs y mejorar la portabilidad, ejecute:")
    print("  python instalar_appdirs.py")
    
    input("\nPresione Enter para continuar...")

if __name__ == "__main__":
    main()
