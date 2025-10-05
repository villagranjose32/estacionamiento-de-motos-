#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Gestión de Estacionamiento
Archivo principal para ejecutar la aplicación
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox
import platform

# Configurar la codificación en Windows
if platform.system() == "Windows":
    import locale
    # Establecer la codificación predeterminada
    locale.setlocale(locale.LC_ALL, '')

# Agregar el directorio raíz al path para importar los módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Definir función para mostrar errores
def mostrar_error(titulo, mensaje):
    """Muestra un error en interfaz gráfica y consola"""
    print(f"ERROR: {titulo}")
    print(mensaje)
    
    # Intentar mostrar ventana de error
    try:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(titulo, mensaje)
        root.destroy()
    except:
        # Si falla la interfaz gráfica, solo mostrar en consola
        pass
    
    return 1

# Verificar requisitos del sistema
def verificar_requisitos():
    """Verifica que el sistema tenga los requisitos necesarios"""
    
    # Verificar versión de Python
    if sys.version_info.major < 3 or (sys.version_info.major == 3 and sys.version_info.minor < 8):
        return mostrar_error(
            "Versión de Python incompatible",
            f"Se requiere Python 3.8 o superior.\nVersión actual: {sys.version}"
        )
    
    # Verificar Tkinter
    try:
        import tkinter
    except ImportError:
        return mostrar_error(
            "Tkinter no disponible",
            "No se pudo importar la biblioteca Tkinter necesaria para la interfaz gráfica.\n" +
            "Por favor, instale Tkinter para su versión de Python."
        )
    
    return 0

# Verificar requisitos antes de importar módulos de la aplicación
error_code = verificar_requisitos()
if error_code != 0:
    sys.exit(error_code)

# Intentar importar los módulos de la aplicación
try:
    from ventana_operacion import VentanaOperacion
    from ventana_configuracion import ConfiguracionWindow
except ImportError as e:
    sys.exit(mostrar_error(
        "Error al importar módulos",
        f"No se pudieron cargar los componentes necesarios:\n{str(e)}\n\n" +
        "Verifique que la estructura del proyecto sea correcta y que todos los archivos estén presentes."
    ))

def main():
    """Función principal para iniciar la aplicación"""
    try:
        # Crear la ventana principal
        root = tk.Tk()
        root.title("Sistema de Gestión de Estacionamiento")
        
        # Centrar la ventana en la pantalla
        root.update_idletasks()
        width = 1000
        height = 700
        x = (root.winfo_screenwidth() // 2) - (width // 2)
        y = (root.winfo_screenheight() // 2) - (height // 2)
        root.geometry(f"{width}x{height}+{x}+{y}")
        
        # Crear menú
        menu_bar = tk.Menu(root)
        root.config(menu=menu_bar)
        
        # Menú Sistema
        sistema_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Sistema", menu=sistema_menu)
        
        sistema_menu.add_command(label="Configuración de tarifas y turnos (F4)", 
                               command=lambda: ConfiguracionWindow(root))
        sistema_menu.add_separator()
        sistema_menu.add_command(label="Salir", command=lambda: on_closing())
        
        # Menú Ayuda
        ayuda_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Ayuda", menu=ayuda_menu)
        
        ayuda_menu.add_command(label="Acerca de", 
                             command=lambda: messagebox.showinfo("Acerca de", 
                                                               "Sistema de Gestión de Estacionamiento\n\n"
                                                               "Versión 1.0"))
        
        # Crear la aplicación principal
        app = VentanaOperacion(root)
        
        # Configurar el protocolo de cierre
        def on_closing():
            if messagebox.askokcancel("Salir", "¿Desea cerrar el sistema de estacionamiento?"):
                root.destroy()
        
        # Agregar atajos de teclado globales
        def abrir_configuracion(event=None):
            ConfiguracionWindow(root)
        
        root.bind("<F4>", abrir_configuracion)
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Iniciar el bucle principal
        print("Iniciando Sistema de Gestión de Estacionamiento...")
        root.mainloop()
        
    except Exception as e:
        print(f"Error al iniciar la aplicación: {e}")
        messagebox.showerror("Error", f"No se pudo iniciar la aplicación:\n{e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
