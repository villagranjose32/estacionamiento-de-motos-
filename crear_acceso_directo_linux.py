#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para crear un acceso directo en Linux (.desktop file)
"""

import os
import sys
import platform
import subprocess
from pathlib import Path

def main():
    # Verificar que estamos en Linux
    if platform.system() not in ["Linux", "Darwin"]:
        print("Este script solo funciona en Linux o macOS.")
        print("Para Windows, use crear_acceso_directo.py")
        input("Presione Enter para salir...")
        return
    
    print("=" * 80)
    print(" CREANDO ACCESO DIRECTO DE LINUX ".center(80, "="))
    print("=" * 80 + "\n")
    
    # Obtener la ruta completa al directorio actual
    current_dir = os.path.abspath(os.path.dirname(__file__))
    
    # Rutas a los archivos
    script_file = os.path.join(current_dir, "iniciar_estacionamiento.sh")
    icon_file = os.path.join(current_dir, "icono.png")
    
    # Verificar que existan los archivos necesarios
    if not os.path.exists(script_file):
        print(f"❌ No se encontró el archivo {script_file}")
        print("Ejecute primero el script configurar.py")
        input("Presione Enter para salir...")
        return
    
    # Buscar un ícono adecuado
    if not os.path.exists(icon_file):
        # Buscar cualquier archivo de imagen que pueda servir como ícono
        icon_candidates = [
            os.path.join(current_dir, "icono.ico"),
            os.path.join(current_dir, "icono_256x256.png"),
            os.path.join(current_dir, "icono_128x128.png"),
            os.path.join(current_dir, "icono_64x64.png"),
            os.path.join(current_dir, "icono_32x32.png")
        ]
        
        for candidate in icon_candidates:
            if os.path.exists(candidate):
                icon_file = candidate
                break
        else:
            print("⚠️ No se encontró ningún archivo de ícono.")
            print("Se usará un ícono genérico.")
            icon_file = ""
    
    # Hacer el script ejecutable
    try:
        subprocess.run(["chmod", "+x", script_file], check=True)
    except Exception as e:
        print(f"⚠️ No se pudo hacer ejecutable el script: {e}")
    
    # Nombre para el archivo .desktop
    desktop_file_name = "Estacionamiento.desktop"
    
    # Contenido del archivo .desktop
    desktop_content = f"""[Desktop Entry]
Type=Application
Name=Sistema de Estacionamiento
Comment=Sistema de Gestión de Estacionamiento
Exec={script_file}
Terminal=false
Categories=Office;
"""
    
    # Agregar ícono si existe
    if icon_file:
        desktop_content += f"Icon={icon_file}\n"
    
    # Rutas posibles para instalar el acceso directo
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    xdg_desktop_path = os.path.join(os.path.expanduser("~"), "Escritorio")
    applications_path = os.path.join(os.path.expanduser("~"), ".local", "share", "applications")
    
    # Asegurarse de que exista el directorio de aplicaciones
    os.makedirs(applications_path, exist_ok=True)
    
    # Guardar en applications (siempre)
    applications_file = os.path.join(applications_path, desktop_file_name)
    try:
        with open(applications_file, "w") as f:
            f.write(desktop_content)
        os.chmod(applications_file, 0o755)  # Hacer ejecutable
        print(f"✅ Acceso directo creado en el menú de aplicaciones: {applications_file}")
    except Exception as e:
        print(f"❌ Error al crear el acceso directo en el menú: {e}")
    
    # Preguntar si también quiere en el escritorio
    print("\n¿Desea crear también un acceso directo en el escritorio?")
    desktop_too = input("(s/N): ").strip().lower()
    
    if desktop_too == 's':
        # Intentar determinar la ruta correcta del escritorio
        desktop_dir = None
        if os.path.exists(desktop_path):
            desktop_dir = desktop_path
        elif os.path.exists(xdg_desktop_path):
            desktop_dir = xdg_desktop_path
        else:
            print("⚠️ No se pudo encontrar la carpeta del escritorio.")
            desktop_dir = input("Ingrese la ruta a su carpeta de escritorio: ").strip()
            if not os.path.exists(desktop_dir):
                print(f"❌ La ruta {desktop_dir} no existe.")
                desktop_dir = None
        
        if desktop_dir:
            desktop_file = os.path.join(desktop_dir, desktop_file_name)
            try:
                with open(desktop_file, "w") as f:
                    f.write(desktop_content)
                os.chmod(desktop_file, 0o755)  # Hacer ejecutable
                print(f"✅ Acceso directo creado en el escritorio: {desktop_file}")
            except Exception as e:
                print(f"❌ Error al crear el acceso directo en el escritorio: {e}")
    
    # Actualizar la base de datos de aplicaciones
    try:
        print("\nActualizando la base de datos de aplicaciones...")
        subprocess.run(["update-desktop-database", applications_path], check=True)
    except:
        print("⚠️ No se pudo actualizar la base de datos de aplicaciones.")
        print("   Esto no debería afectar el funcionamiento del acceso directo.")
    
    print("\n¡Acceso directo creado correctamente!")
    print("Ahora puede iniciar el sistema haciendo clic en el ícono en el menú de aplicaciones o escritorio.")
    input("\nPresione Enter para salir...")

if __name__ == "__main__":
    main()
