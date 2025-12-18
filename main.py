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
import ttkbootstrap as ttk
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
    from ventana_editar_fichas import mostrar_gestion_fichas
except ImportError as e:
    sys.exit(mostrar_error(
        "Error al importar módulos",
        f"No se pudieron cargar los componentes necesarios:\n{str(e)}\n\n" +
        "Verifique que la estructura del proyecto sea correcta y que todos los archivos estén presentes."
    ))

import json

# Archivo de configuración de temas
ARCHIVO_CONFIG = os.path.join(os.path.dirname(__file__), '.tema_config.json')

# Temas disponibles
TEMAS_DISPONIBLES = [
    "darkly",
    "superhero",
    "litera",
    "minty",
    "solar",
    "cyborg",
    "sandstone",
    "united",
    "morph",
    "journal",
    "flatly",
    "sketchy"
]

def cargar_tema_guardado():
    """Carga el tema guardado o retorna el predeterminado"""
    try:
        if os.path.exists(ARCHIVO_CONFIG):
            with open(ARCHIVO_CONFIG, 'r') as f:
                config = json.load(f)
                return config.get('tema', 'superhero')
    except:
        pass
    return 'superhero'

def guardar_tema(tema):
    """Guarda el tema seleccionado"""
    try:
        config = {'tema': tema}
        with open(ARCHIVO_CONFIG, 'w') as f:
            json.dump(config, f)
    except:
        pass

def cambiar_tema(root, nuevo_tema):
    """Cambia el tema de la aplicación"""
    try:
        root.tk.call("ttk::setTheme", nuevo_tema)
        guardar_tema(nuevo_tema)
        messagebox.showinfo("Tema cambiado", 
                           f"✅ Tema '{nuevo_tema}' aplicado correctamente.\n"
                           f"El cambio se verá en la próxima ejecución de la aplicación.")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo cambiar el tema: {e}")

def mostrar_selector_temas(root):
    """Muestra un diálogo para seleccionar un tema"""
    ventana = tk.Toplevel(root)
    ventana.title("Seleccionar Tema")
    ventana.geometry("400x500")
    ventana.transient(root)
    ventana.grab_set()
    
    # Título
    titulo = ttk.Label(ventana, text="🎨 SELECCIONAR TEMA", font=("Arial", 14, "bold"))
    titulo.pack(pady=15)
    
    # Descripción
    desc = ttk.Label(ventana, text="Elige un tema para personalizar la interfaz:", 
                    font=("Arial", 10))
    desc.pack(pady=(0, 15))
    
    # Frame con scrollbar para los botones
    canvas_frame = ttk.Frame(ventana)
    canvas_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    canvas = tk.Canvas(canvas_frame, highlightthickness=0)
    scroll = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scroll.set)
    
    # Obtener tema actual
    tema_actual = cargar_tema_guardado()
    
    # Crear botones para cada tema
    def crear_boton_tema(tema):
        btn_frame = ttk.Frame(scrollable_frame)
        btn_frame.pack(fill="x", pady=5)
        
        # Ícono y nombre del tema
        label_tema = ttk.Label(btn_frame, text=f"🎨 {tema.upper()}", 
                              font=("Arial", 11, "bold"))
        label_tema.pack(side="left", padx=10)
        
        # Botón
        if tema == tema_actual:
            btn = ttk.Button(btn_frame, text="✅ ACTUAL", state="disabled", width=20)
        else:
            btn = ttk.Button(btn_frame, text="Aplicar tema", 
                           command=lambda: cambiar_tema(root, tema), width=20)
        btn.pack(side="right", padx=10)
    
    for tema in TEMAS_DISPONIBLES:
        crear_boton_tema(tema)
    
    canvas.pack(side="left", fill="both", expand=True)
    scroll.pack(side="right", fill="y")
    
    # Botón cerrar
    ttk.Button(ventana, text="Cerrar", command=ventana.destroy).pack(pady=10)

def modificar_capacidad_fichas(root):
    """Abre un diálogo para modificar la capacidad de fichas"""
    ventana = tk.Toplevel(root)
    ventana.title("Modificar Capacidad de Fichas")
    ventana.geometry("350x200")
    ventana.transient(root)
    ventana.grab_set()
    
    # Centrar en la pantalla
    ventana.update_idletasks()
    x = (ventana.winfo_screenwidth() // 2) - (350 // 2)
    y = (ventana.winfo_screenheight() // 2) - (200 // 2)
    ventana.geometry(f"+{x}+{y}")
    
    # Título
    ttk.Label(ventana, text="🎫 MODIFICAR CAPACIDAD DE FICHAS", 
             font=("Arial", 12, "bold")).pack(pady=15)
    
    # Frame para entrada
    frame_entrada = ttk.Frame(ventana, padding=10)
    frame_entrada.pack(fill="x", padx=20, pady=10)
    
    ttk.Label(frame_entrada, text="Nueva capacidad (1-1000):", 
             font=("Arial", 11)).grid(row=0, column=0, sticky="w", pady=5)
    
    var_capacidad = tk.StringVar()
    spinbox = ttk.Spinbox(frame_entrada, from_=1, to=1000, 
                         textvariable=var_capacidad, width=15, 
                         font=("Arial", 12))
    spinbox.grid(row=0, column=1, sticky="w", padx=10)
    spinbox.set(120)  # Valor por defecto
    
    # Frame de botones
    frame_botones = ttk.Frame(ventana, padding=10)
    frame_botones.pack(fill="x", padx=20, pady=15)
    
    def guardar_cambios():
        try:
            nueva_capacidad = int(var_capacidad.get())
            if nueva_capacidad < 1 or nueva_capacidad > 1000:
                messagebox.showerror("Error", "La capacidad debe estar entre 1 y 1000")
                return
            
            # Modificar la capacidad usando ConfigRepo
            try:
                from domain.infra.paths import SedePaths
                from domain.infra.config_repo import ConfigRepo
                
                paths = SedePaths()
                repo = ConfigRepo(paths)
                
                # Cargar configuración actual
                config = repo.load_or_create_defaults()
                
                # Actualizar capacidad
                config.capacidad = nueva_capacidad
                
                # Guardar cambios
                repo.save(config)
                
                messagebox.showinfo("Éxito", 
                                  f"✅ Capacidad actualizada a {nueva_capacidad} fichas.\n"
                                  f"El cambio se verá al reiniciar la aplicación.")
                ventana.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo actualizar: {e}")
        except ValueError:
            messagebox.showerror("Error", "Ingrese un número válido")
    
    ttk.Button(frame_botones, text="💾 Guardar", command=guardar_cambios, 
              bootstyle="success").pack(side="left", padx=5)
    ttk.Button(frame_botones, text="❌ Cancelar", command=ventana.destroy,
              bootstyle="secondary").pack(side="left", padx=5)

def main():
    """Función principal para iniciar la aplicación"""
    try:
        # Cargar tema guardado
        tema_inicial = cargar_tema_guardado()
        
        # Crear la ventana principal con ttkbootstrap
        root = ttk.Window(themename=tema_inicial)
        root.title("Sistema de Gestión de Estacionamiento")
        
        # Centrar la ventana en la pantalla
        root.update_idletasks()
        width = 1200
        height = 750
        x = (root.winfo_screenwidth() // 2) - (width // 2)
        y = (root.winfo_screenheight() // 2) - (height // 2)
        root.geometry(f"{width}x{height}+{x}+{y}")
        
        # Crear menú
        menu_bar = tk.Menu(root)
        root.config(menu=menu_bar)
        
        # Menú Sistema
        sistema_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Sistema", menu=sistema_menu)
        
        sistema_menu.add_command(label="📋 Editar Fichas", 
                               command=lambda: mostrar_gestion_fichas(root))
        sistema_menu.add_separator()
        sistema_menu.add_command(label="🎨 Seleccionar Tema", 
                               command=lambda: mostrar_selector_temas(root))
        sistema_menu.add_command(label="🎫 Modificar Capacidad de Fichas", 
                               command=lambda: modificar_capacidad_fichas(root))
        sistema_menu.add_separator()
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
        print(f"Tema actual: {tema_inicial}")
        root.mainloop()
        
    except Exception as e:
        print(f"Error al iniciar la aplicación: {e}")
        messagebox.showerror("Error", f"No se pudo iniciar la aplicación:\n{e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
