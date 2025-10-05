#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para crear un acceso directo en Windows
"""

import os
import sys
import platform

def main():
    # Verificar que estamos en Windows
    if platform.system() != "Windows":
        print("Este script solo funciona en Windows.")
        print("Para Linux, use crear_acceso_directo_linux.py")
        input("Presione Enter para salir...")
        return
    
    try:
        # Intentar importar la biblioteca win32com
        import win32com.client
    except ImportError:
        print("La biblioteca pywin32 no está instalada.")
        print("Instalando pywin32...")
        
        # Intentar instalar pywin32
        try:
            # Obtener la ruta del pip en el entorno virtual
            if os.path.exists(".venv\\Scripts\\pip.exe"):
                pip_path = ".venv\\Scripts\\pip.exe"
            else:
                pip_path = "pip"
            
            # Instalar pywin32
            import subprocess
            subprocess.run([pip_path, "install", "pywin32"], check=True)
            print("Biblioteca pywin32 instalada correctamente.")
            
            # Volver a importar
            import win32com.client
        except Exception as e:
            print(f"Error al instalar pywin32: {e}")
            print("Por favor, instale manualmente la biblioteca pywin32:")
            print("    pip install pywin32")
            input("Presione Enter para salir...")
            return

    print("=" * 80)
    print(" CREANDO ACCESO DIRECTO DE WINDOWS ".center(80, "="))
    print("=" * 80 + "\n")
    
    # Obtener la ruta completa al directorio actual
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Rutas a los archivos
    bat_file = os.path.join(current_dir, "iniciar_estacionamiento.bat")
    icon_file = os.path.join(current_dir, "icono.ico")
    
    # Verificar que existan los archivos necesarios
    if not os.path.exists(bat_file):
        print(f"❌ No se encontró el archivo {bat_file}")
        print("Ejecute primero el script configurar.py")
        input("Presione Enter para salir...")
        return
    
    # Si no existe icono.ico pero existe icono.png, convertir
    if not os.path.exists(icon_file) and os.path.exists(os.path.join(current_dir, "icono.png")):
        print("No se encontró icono.ico pero existe icono.png")
        print("Intentando convertir de PNG a ICO...")
        
        try:
            # Intentar instalar Pillow si no está instalada
            try:
                from PIL import Image
            except ImportError:
                print("Instalando biblioteca Pillow para convertir imágenes...")
                subprocess.run([pip_path, "install", "Pillow"], check=True)
                from PIL import Image
            
            # Convertir de PNG a ICO
            img = Image.open(os.path.join(current_dir, "icono.png"))
            icon_file = os.path.join(current_dir, "icono.ico")
            img.save(icon_file, sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
            print("✅ Icono convertido correctamente")
        except Exception as e:
            print(f"⚠️ No se pudo convertir el icono: {e}")
            print("Se usará un icono predeterminado")
            icon_file = ""
    
    # Definir la ubicación del acceso directo
    desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    shortcut_path = os.path.join(desktop, "Estacionamiento.lnk")
    
    # Crear el objeto shell y el acceso directo
    try:
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.TargetPath = bat_file
        shortcut.WorkingDirectory = current_dir
        shortcut.Description = "Sistema de Gestión de Estacionamiento"
        
        # Establecer el icono si existe
        if os.path.exists(icon_file):
            shortcut.IconLocation = icon_file
        
        # Guardar el acceso directo
        shortcut.save()
        
        print(f"✅ Acceso directo creado en el escritorio: {shortcut_path}")
    except Exception as e:
        print(f"❌ Error al crear el acceso directo: {e}")
    
    print("\n¿Desea crear también un acceso directo en el menú de inicio?")
    menu_start = input("(s/N): ").strip().lower()
    
    if menu_start == 's':
        try:
            # Crear acceso directo en el menú de inicio
            start_menu = os.path.join(os.environ['APPDATA'], 'Microsoft', 'Windows', 'Start Menu', 'Programs')
            start_menu_path = os.path.join(start_menu, "Estacionamiento.lnk")
            
            shortcut = shell.CreateShortCut(start_menu_path)
            shortcut.TargetPath = bat_file
            shortcut.WorkingDirectory = current_dir
            shortcut.Description = "Sistema de Gestión de Estacionamiento"
            
            # Establecer el icono si existe
            if os.path.exists(icon_file):
                shortcut.IconLocation = icon_file
            
            # Guardar el acceso directo
            shortcut.save()
            
            print(f"✅ Acceso directo creado en el menú de inicio: {start_menu_path}")
        except Exception as e:
            print(f"❌ Error al crear el acceso directo en el menú de inicio: {e}")
    
    input("\nPresione Enter para salir...")

if __name__ == "__main__":
    main()
