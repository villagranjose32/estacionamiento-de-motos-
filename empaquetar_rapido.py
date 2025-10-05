#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para empaquetar la aplicación con ajustes predeterminados optimizados
"""

import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path
import time

def main():
    print("\n" + "=" * 80)
    print(" EMPAQUETADOR RÁPIDO DEL SISTEMA DE ESTACIONAMIENTO ".center(80, "="))
    print("=" * 80 + "\n")
    
    # Obtener directorio actual
    script_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    
    # Verificar entorno virtual
    venv_path = None
    if os.path.exists(script_dir / ".venv"):
        if platform.system() == "Windows":
            venv_python = script_dir / ".venv" / "Scripts" / "python.exe"
        else:
            venv_python = script_dir / ".venv" / "bin" / "python"
        
        if venv_python.exists():
            venv_path = venv_python
    
    if not venv_path:
        print("❌ No se encontró el entorno virtual.")
        print("Ejecute primero el script configurar.py")
        input("Presione Enter para salir...")
        return
    
    # Instalar PyInstaller si no está instalado
    print("Verificando/instalando PyInstaller...")
    try:
        # Determinar la ruta del pip adecuada
        if platform.system() == "Windows":
            pip_path = script_dir / ".venv" / "Scripts" / "pip.exe"
        else:
            pip_path = script_dir / ".venv" / "bin" / "pip"
        
        # Instalar PyInstaller
        subprocess.run([str(pip_path), "install", "pyinstaller"], check=True)
        print("✅ PyInstaller está disponible.")
    except Exception as e:
        print(f"❌ Error al verificar/instalar PyInstaller: {e}")
        input("Presione Enter para salir...")
        return
    
    # Verificar que exista el icono, o crear uno
    icon_file = script_dir / "icono.ico" if platform.system() == "Windows" else script_dir / "icono.png"
    
    if not icon_file.exists():
        # Buscar alternativas
        alternatives = [
            script_dir / "icono_256x256.png",
            script_dir / "icono_128x128.png",
            script_dir / "icono_64x64.png",
            script_dir / "icono_32x32.png",
        ]
        
        for alt in alternatives:
            if alt.exists():
                icon_file = alt
                break
        else:
            # Si no hay iconos, intentar generar
            print("No se encontró ningún icono.")
            print("Intentando generar iconos automáticamente...")
            
            if (script_dir / "crear_icono.py").exists():
                try:
                    subprocess.run([str(venv_python), str(script_dir / "crear_icono.py")], check=False)
                    
                    # Verificar si se generó algún icono
                    time.sleep(1)  # Dar tiempo a que se creen los archivos
                    for alt in alternatives:
                        if alt.exists():
                            icon_file = alt
                            print(f"✅ Icono generado: {icon_file.name}")
                            break
                    else:
                        print("⚠️ No se pudo generar ningún icono.")
                        icon_file = None
                except Exception as e:
                    print(f"⚠️ Error al generar iconos: {e}")
                    icon_file = None
            else:
                print("⚠️ No se encontró el script para generar iconos.")
                icon_file = None
    
    # Nombre de la aplicación
    app_name = "Estacionamiento"
    
    # Preparar comando de PyInstaller
    cmd = [
        str(venv_python), "-m", "PyInstaller",
        "--name", app_name,
        "--onefile",  # Un solo archivo ejecutable
        "--windowed",  # Sin consola
        "--clean",
        "--noconfirm"
    ]
    
    # Añadir icono si existe
    if icon_file and icon_file.exists():
        cmd.extend(["--icon", str(icon_file)])
    
    # Incluir datos
    cmd.extend(["--add-data", f"data{os.pathsep}data"])
    
    # Directorio de trabajo
    cmd.extend(["--workpath", "build"])
    cmd.extend(["--distpath", "dist"])
    
    # Archivo principal
    cmd.append(str(script_dir / "main.py"))
    
    # Ejecutar PyInstaller
    print("\n" + "=" * 80)
    print(" EMPAQUETANDO APLICACIÓN ".center(80, "="))
    print("=" * 80)
    
    print(f"\nEjecutando PyInstaller...")
    print(f"Esto puede tardar unos minutos...")
    
    try:
        subprocess.run(cmd, check=True)
        
        # Determinar ruta del ejecutable generado
        if platform.system() == "Windows":
            exe_path = script_dir / "dist" / f"{app_name}.exe"
        else:
            exe_path = script_dir / "dist" / app_name
        
        if exe_path.exists():
            print("\n" + "=" * 80)
            print(" EMPAQUETADO EXITOSO ".center(80, "="))
            print("=" * 80)
            
            print(f"\n✅ Ejecutable generado en: {exe_path}")
            
            # Crear acceso directo automáticamente
            print("\n¿Desea crear un acceso directo para el ejecutable?")
            if input("(s/N): ").strip().lower() == 's':
                if platform.system() == "Windows":
                    # En Windows, usar el script existente
                    if (script_dir / "crear_acceso_directo.py").exists():
                        print("\nEjecutando script para crear acceso directo...")
                        shortcut_cmd = [
                            str(venv_python),
                            str(script_dir / "crear_acceso_directo.py")
                        ]
                        subprocess.run(shortcut_cmd, check=False)
                else:
                    # En Linux, usar el script existente
                    if (script_dir / "crear_acceso_directo_linux.py").exists():
                        print("\nEjecutando script para crear acceso directo...")
                        shortcut_cmd = [
                            str(venv_python),
                            str(script_dir / "crear_acceso_directo_linux.py")
                        ]
                        subprocess.run(shortcut_cmd, check=False)
            
            print("\n¡Proceso completado exitosamente!")
            print("Ahora puede distribuir el ejecutable generado.")
        else:
            print(f"\n❌ No se encontró el ejecutable generado en la ruta esperada: {exe_path}")
    except Exception as e:
        print(f"\n❌ Error durante el empaquetado: {e}")
    
    input("\nPresione Enter para salir...")

if __name__ == "__main__":
    main()
