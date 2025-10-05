#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para instalar la biblioteca appdirs necesaria para la portabilidad del sistema
"""

import os
import sys
import subprocess
import platform

def main():
    print("=" * 80)
    print(" INSTALACIÓN DE APPDIRS PARA PORTABILIDAD ".center(80, "="))
    print("=" * 80 + "\n")
    
    # Determinar la ruta del entorno virtual
    project_dir = os.path.dirname(os.path.abspath(__file__))
    venv_dir = os.path.join(project_dir, ".venv")
    
    if not os.path.exists(venv_dir):
        print("❌ No se encontró el entorno virtual. Ejecute primero configurar.py")
        sys.exit(1)
    
    # Determinar el ejecutable de pip
    if platform.system() == "Windows":
        pip_path = os.path.join(venv_dir, "Scripts", "pip.exe")
    else:
        pip_path = os.path.join(venv_dir, "bin", "pip")
    
    if not os.path.exists(pip_path):
        print(f"❌ No se encontró pip en el entorno virtual: {pip_path}")
        sys.exit(1)
    
    try:
        print("Instalando appdirs...")
        subprocess.run([pip_path, "install", "appdirs"], check=True)
        print("\n✅ appdirs instalado correctamente")
        print("✅ El sistema ahora usará ubicaciones de datos específicas para cada sistema operativo")
        print("\nReinicie la aplicación para que los cambios surtan efecto.")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error al instalar appdirs: {e}")
        print("Intente ejecutar manualmente:")
        if platform.system() == "Windows":
            print(f"{venv_dir}\\Scripts\\pip install appdirs")
        else:
            print(f"{venv_dir}/bin/pip install appdirs")
    
    input("\nPresione Enter para continuar...")

if __name__ == "__main__":
    main()
