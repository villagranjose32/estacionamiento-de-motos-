#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para generar iconos en diferentes tamaños a partir de una imagen base
"""

import os
import sys
import platform

def main():
    print("=" * 80)
    print(" GENERADOR DE ICONOS ".center(80, "="))
    print("=" * 80 + "\n")
    
    # Verificar si existe Pillow
    try:
        from PIL import Image
    except ImportError:
        print("La biblioteca Pillow no está instalada.")
        print("Instalando Pillow...")
        
        try:
            # Determinar la ruta del pip adecuada
            if os.path.exists(".venv/bin/pip"):
                pip_path = ".venv/bin/pip"
            elif os.path.exists(".venv/Scripts/pip.exe"):
                pip_path = ".venv/Scripts/pip.exe"
            else:
                pip_path = "pip"
            
            # Instalar Pillow
            import subprocess
            subprocess.run([pip_path, "install", "Pillow"], check=True)
            print("Biblioteca Pillow instalada correctamente.")
            
            # Volver a importar
            from PIL import Image
        except Exception as e:
            print(f"Error al instalar Pillow: {e}")
            print("Por favor, instale manualmente la biblioteca Pillow:")
            print("    pip install Pillow")
            input("Presione Enter para salir...")
            return
    
    # Obtener la ruta del script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Buscar la imagen base
    base_image_path = os.path.join(script_dir, "icono.png")
    if not os.path.exists(base_image_path):
        print("No se encontró la imagen base 'icono.png'.")
        print("Por favor, seleccione una imagen para usar como base:")
        
        # Listar imágenes disponibles
        images = [f for f in os.listdir(script_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]
        
        if not images:
            print("❌ No se encontraron imágenes en el directorio del script.")
            input("Presione Enter para salir...")
            return
        
        # Mostrar opciones
        print("\nImágenes disponibles:")
        for i, img in enumerate(images, 1):
            print(f"{i}. {img}")
        
        # Pedir selección
        while True:
            try:
                choice = int(input("\nSeleccione una imagen (número): ").strip())
                if 1 <= choice <= len(images):
                    base_image_path = os.path.join(script_dir, images[choice - 1])
                    break
                else:
                    print("Selección no válida.")
            except ValueError:
                print("Por favor, ingrese un número.")
    
    # Tamaños a generar
    sizes = [16, 32, 48, 64, 128, 256]
    
    try:
        # Abrir la imagen base
        base_image = Image.open(base_image_path)
        
        # Generar iconos en diferentes tamaños
        print(f"\nGenerando iconos a partir de: {os.path.basename(base_image_path)}")
        
        for size in sizes:
            # Nombre del archivo de salida
            output_file = os.path.join(script_dir, f"icono_{size}x{size}.png")
            
            # Redimensionar imagen
            resized = base_image.resize((size, size), Image.Resampling.LANCZOS)
            
            # Guardar imagen redimensionada
            resized.save(output_file)
            print(f"✅ Generado: {os.path.basename(output_file)}")
        
        # Generar icono ICO (solo si estamos en Windows o lo necesitamos)
        ico_file = os.path.join(script_dir, "icono.ico")
        if platform.system() == "Windows" or input("\n¿Desea generar también un archivo ICO? (s/N): ").strip().lower() == 's':
            print("Generando archivo ICO...")
            
            # Crear una lista de imágenes redimensionadas para el ICO
            ico_sizes = [(size, size) for size in sizes]
            base_image.save(ico_file, format='ICO', sizes=ico_sizes)
            print(f"✅ Generado: {os.path.basename(ico_file)}")
        
        print("\n¡Iconos generados correctamente!")
        print("Ahora puede ejecutar los scripts para crear accesos directos.")
    except Exception as e:
        print(f"\n❌ Error al generar iconos: {e}")
    
    input("\nPresione Enter para salir...")

if __name__ == "__main__":
    main()
