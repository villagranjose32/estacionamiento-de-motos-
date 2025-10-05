#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para restaurar un respaldo de los datos del sistema
"""

import os
import sys
import shutil
import zipfile
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox

def main():
    # Crear una ventana raíz (la ocultaremos)
    root = tk.Tk()
    root.withdraw()
    
    print("=" * 80)
    print(" RESTAURACIÓN DE RESPALDO ".center(80, "="))
    print("=" * 80 + "\n")
    
    # Pedir al usuario que seleccione el archivo de respaldo
    print("Por favor, seleccione el archivo de respaldo a restaurar...")
    backup_path = filedialog.askopenfilename(
        title="Seleccionar archivo de respaldo",
        filetypes=[("Archivos ZIP", "*.zip"), ("Todos los archivos", "*.*")]
    )
    
    if not backup_path:
        print("❌ No se seleccionó ningún archivo.")
        return
    
    print(f"\nArchivo seleccionado: {backup_path}")
    
    # Determinar la ubicación de destino
    try:
        from appdirs import user_data_dir
        app_name = "SistemaEstacionamiento"
        app_author = "Parking"
        data_dir = Path(user_data_dir(app_name, app_author))
        appdirs_available = True
    except ImportError:
        appdirs_available = False
        data_dir = Path(os.path.dirname(os.path.abspath(__file__))) / "data"
    
    # Preguntar al usuario dónde restaurar
    if appdirs_available:
        print("\nOpciones de restauración:")
        print(f"1. Ubicación específica del sistema ({data_dir})")
        print(f"2. Directorio local (data/)")
        print("3. Otra ubicación")
        
        while True:
            choice = input("\nSeleccione una opción (1-3): ").strip()
            if choice == "1":
                restore_dir = data_dir
                break
            elif choice == "2":
                restore_dir = Path(os.path.dirname(os.path.abspath(__file__))) / "data"
                break
            elif choice == "3":
                print("Por favor, seleccione el directorio de destino...")
                restore_path = filedialog.askdirectory(title="Seleccionar directorio de destino")
                if not restore_path:
                    print("❌ No se seleccionó ningún directorio.")
                    return
                restore_dir = Path(restore_path)
                break
            else:
                print("Opción no válida, intente nuevamente.")
    else:
        print("\nLa biblioteca appdirs no está disponible.")
        print("Se restaurará en el directorio 'data' local.")
        restore_dir = data_dir
    
    # Confirmar con el usuario
    print(f"\nSe restaurará el respaldo en: {restore_dir}")
    confirm = input("¿Desea continuar? (s/N): ").strip().lower()
    if confirm != 's':
        print("\n❌ Restauración cancelada.")
        return
    
    # Crear directorio de destino si no existe
    os.makedirs(restore_dir, exist_ok=True)
    
    # Extraer el respaldo
    try:
        print("\nRestaurando respaldo...")
        with zipfile.ZipFile(backup_path, 'r') as zipf:
            # Mostrar contenido
            print("\nContenido del respaldo:")
            for file in zipf.namelist():
                print(f"  - {file}")
            
            # Extraer archivos
            zipf.extractall(path=restore_dir.parent)
        
        print(f"\n✅ Respaldo restaurado exitosamente en: {restore_dir}")
    except Exception as e:
        print(f"\n❌ Error al restaurar el respaldo: {e}")
    
    input("\nPresione Enter para continuar...")

if __name__ == "__main__":
    main()
