#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para empaquetar el Sistema de Gestión de Estacionamiento en un ejecutable
"""

import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path

def print_header(texto):
    """Imprime un encabezado con formato"""
    print("\n" + "=" * 80)
    print(f" {texto} ".center(80, "="))
    print("=" * 80 + "\n")

def main():
    print_header("EMPAQUETADOR DEL SISTEMA DE GESTIÓN DE ESTACIONAMIENTO")
    
    # Verificar si PyInstaller está instalado
    try:
        import PyInstaller
        print("✅ PyInstaller está instalado.")
    except ImportError:
        print("PyInstaller no está instalado. Instalando...")
        
        try:
            # Determinar la ruta del pip adecuada
            if os.path.exists(".venv/bin/pip"):
                pip_path = ".venv/bin/pip"
            elif os.path.exists(".venv/Scripts/pip.exe"):
                pip_path = ".venv/Scripts/pip.exe"
            else:
                pip_path = "pip"
            
            # Instalar PyInstaller
            subprocess.run([pip_path, "install", "pyinstaller"], check=True)
            print("✅ PyInstaller instalado correctamente.")
        except Exception as e:
            print(f"❌ Error al instalar PyInstaller: {e}")
            print("Por favor, instale manualmente PyInstaller:")
            print("    pip install pyinstaller")
            input("Presione Enter para salir...")
            return
    
    # Verificar que existan los archivos necesarios
    script_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    main_script = script_dir / "main.py"
    
    if not main_script.exists():
        print(f"❌ No se encontró el archivo principal {main_script}")
        input("Presione Enter para salir...")
        return
    
    # Buscar un icono adecuado para el ejecutable
    icon_file = None
    icon_candidates = [
        script_dir / "icono.ico",
        script_dir / "icono.png",
        script_dir / "icono_256x256.png",
        script_dir / "icono_128x128.png",
        script_dir / "icono_64x64.png"
    ]
    
    for candidate in icon_candidates:
        if candidate.exists():
            icon_file = candidate
            print(f"✅ Usando icono: {icon_file}")
            break
    
    if not icon_file:
        print("⚠️ No se encontró ningún archivo de icono.")
        print("El ejecutable no tendrá un ícono personalizado.")
        
        # Intentar crear iconos automáticamente
        print("¿Desea intentar generar iconos automáticamente?")
        if input("(s/N): ").strip().lower() == 's':
            # Ejecutar el script de creación de iconos si existe
            if (script_dir / "crear_icono.py").exists():
                print("Ejecutando script para generar iconos...")
                subprocess.run([sys.executable, str(script_dir / "crear_icono.py")], check=False)
                
                # Verificar si se generaron los iconos
                for candidate in icon_candidates:
                    if candidate.exists():
                        icon_file = candidate
                        print(f"✅ Usando icono generado: {icon_file}")
                        break
    
    # Preguntar al usuario por opciones de empaquetado
    print_header("OPCIONES DE EMPAQUETADO")
    
    # Nombre del ejecutable
    app_name = input("Nombre del ejecutable (sin extensión) [Estacionamiento]: ").strip()
    if not app_name:
        app_name = "Estacionamiento"
    
    # Modo de empaquetado
    print("\nModos de empaquetado:")
    print("1. Ejecutable único (--onefile)")
    print("   Todo el programa en un solo archivo ejecutable")
    print("2. Directorio (--onedir)")
    print("   Ejecutable con archivos de soporte en un directorio")
    
    while True:
        mode = input("\nSeleccione el modo (1/2) [1]: ").strip()
        if not mode or mode == "1":
            onefile = True
            break
        elif mode == "2":
            onefile = False
            break
        else:
            print("Opción no válida. Por favor, seleccione 1 o 2.")
    
    # Consola visible o no
    print("\n¿Desea que la consola sea visible cuando se ejecute la aplicación?")
    print("(Si elige 'no', no se verán mensajes de error en la consola)")
    console = input("(s/N): ").strip().lower() == 's'
    
    # Comando de PyInstaller
    pyinstaller_cmd = [
        "pyinstaller",
        "--name", app_name,
        "--clean",
        "--noconfirm"
    ]
    
    # Añadir opciones según selección
    if onefile:
        pyinstaller_cmd.append("--onefile")
    
    if not console:
        pyinstaller_cmd.append("--windowed")
    
    if icon_file:
        pyinstaller_cmd.extend(["--icon", str(icon_file)])
    
    # Añadir los directorios de datos como datos adicionales
    pyinstaller_cmd.extend(["--add-data", f"data{os.pathsep}data"])
    
    # Directorio de trabajo
    pyinstaller_cmd.extend(["--workpath", "build"])
    pyinstaller_cmd.extend(["--distpath", "dist"])
    
    # Archivo principal
    pyinstaller_cmd.append(str(main_script))
    
    # Ejecutar PyInstaller
    print_header("EMPAQUETANDO LA APLICACIÓN")
    print(f"Ejecutando comando: {' '.join(pyinstaller_cmd)}")
    
    try:
        result = subprocess.run(pyinstaller_cmd, check=True)
        
        if result.returncode == 0:
            # Determinar la ruta del ejecutable generado
            if onefile:
                if platform.system() == "Windows":
                    exe_path = os.path.join("dist", f"{app_name}.exe")
                else:
                    exe_path = os.path.join("dist", app_name)
            else:
                if platform.system() == "Windows":
                    exe_path = os.path.join("dist", app_name, f"{app_name}.exe")
                else:
                    exe_path = os.path.join("dist", app_name, app_name)
            
            if os.path.exists(exe_path):
                print_header("EMPAQUETADO EXITOSO")
                print(f"✅ Ejecutable generado en: {os.path.abspath(exe_path)}")
                
                # Crear acceso directo automáticamente
                print("\n¿Desea crear un acceso directo para el ejecutable?")
                create_shortcut = input("(s/N): ").strip().lower() == 's'
                
                if create_shortcut:
                    try:
                        if platform.system() == "Windows":
                            # En Windows, usar win32com para crear acceso directo
                            try:
                                import win32com.client
                                
                                desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
                                shortcut_path = os.path.join(desktop, f"{app_name}.lnk")
                                
                                shell = win32com.client.Dispatch("WScript.Shell")
                                shortcut = shell.CreateShortCut(shortcut_path)
                                shortcut.TargetPath = os.path.abspath(exe_path)
                                shortcut.WorkingDirectory = os.path.dirname(os.path.abspath(exe_path))
                                shortcut.Description = "Sistema de Gestión de Estacionamiento"
                                
                                if icon_file:
                                    shortcut.IconLocation = os.path.abspath(icon_file)
                                
                                shortcut.save()
                                print(f"✅ Acceso directo creado en el escritorio: {shortcut_path}")
                            except ImportError:
                                print("⚠️ No se pudo crear el acceso directo (win32com no está disponible)")
                                print("   Puede usar el script crear_acceso_directo.py después.")
                        else:
                            # En Linux, crear archivo .desktop
                            desktop_dir = os.path.join(os.path.expanduser("~"), "Desktop")
                            if not os.path.exists(desktop_dir):
                                desktop_dir = os.path.join(os.path.expanduser("~"), "Escritorio")
                            
                            if os.path.exists(desktop_dir):
                                desktop_file = os.path.join(desktop_dir, f"{app_name}.desktop")
                                
                                with open(desktop_file, "w") as f:
                                    f.write(f"""[Desktop Entry]
Type=Application
Name={app_name}
Comment=Sistema de Gestión de Estacionamiento
Exec={os.path.abspath(exe_path)}
Terminal=false
Categories=Office;
""")
                                    if icon_file:
                                        f.write(f"Icon={os.path.abspath(icon_file)}\n")
                                
                                os.chmod(desktop_file, 0o755)
                                print(f"✅ Acceso directo creado en el escritorio: {desktop_file}")
                            else:
                                print("⚠️ No se encontró el directorio del escritorio")
                    except Exception as e:
                        print(f"⚠️ Error al crear el acceso directo: {e}")
                
                print("\n¡Proceso completado exitosamente!")
                print("Ahora puede distribuir el ejecutable generado.")
            else:
                print(f"❌ No se encontró el ejecutable generado en la ruta esperada: {exe_path}")
        else:
            print(f"❌ Error al empaquetar la aplicación. Código de salida: {result.returncode}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al ejecutar PyInstaller: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
    
    input("\nPresione Enter para salir...")

if __name__ == "__main__":
    main()
