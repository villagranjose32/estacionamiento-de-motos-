#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo de Temas disponibles en ttkbootstrap
Permite previsualizacion de todos los temas
"""

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

# Temas disponibles en ttkbootstrap
TEMAS = [
    "darkly",      # Oscuro moderno
    "litera",      # Claro y limpio
    "minty",       # Verde pastel
    "solar",       # Naranja oscuro
    "superhero",   # Azul oscuro
    "cyborg",      # Gris oscuro
    "sandstone",   # Café arena
    "united",      # Rojo y gris
    "lumen",       # Claro profesional
    "flatly",      # Azul plano
    "morph",       # Colores vibrantes
    "simplex",     # Minimalist
]

def crear_demo(tema):
    """Crea una ventana de demostración con el tema especificado"""
    
    root = ttk.Window(themename=tema)
    root.title(f"Tema: {tema.upper()}")
    root.geometry("900x600")
    
    # Marco principal
    main = ttk.Frame(root, padding=20)
    main.pack(fill=BOTH, expand=True)
    
    # Título
    titulo = ttk.Label(main, text=f"🎨 TEMA: {tema.upper()}", 
                      font=("Arial", 20, "bold"))
    titulo.pack(pady=(0, 20))
    
    # Sección de botones
    btn_frame = ttk.Labelframe(main, text="Estilos de Botones", padding=15)
    btn_frame.pack(fill=X, pady=(0, 15))
    
    botones = [
        ("Success", "success-lg"),
        ("Danger", "danger-lg"),
        ("Warning", "warning-lg"),
        ("Info", "info-lg"),
        ("Primary", "primary-lg"),
        ("Secondary", "secondary"),
    ]
    
    for texto, estilo in botones:
        ttk.Button(btn_frame, text=texto, bootstyle=estilo).pack(side=LEFT, padx=5, pady=10)
    
    # Sección de inputs
    entrada_frame = ttk.Labelframe(main, text="Campos de Entrada", padding=15)
    entrada_frame.pack(fill=X, pady=(0, 15))
    
    ttk.Label(entrada_frame, text="Campo de texto:").pack(anchor=W, pady=(0, 5))
    ttk.Entry(entrada_frame).pack(fill=X, pady=(0, 10))
    
    ttk.Label(entrada_frame, text="Combobox:").pack(anchor=W, pady=(0, 5))
    ttk.Combobox(entrada_frame, values=["Opción 1", "Opción 2", "Opción 3"]).pack(fill=X, pady=(0, 10))
    
    # Sección de indicadores
    indicadores_frame = ttk.Labelframe(main, text="Indicadores", padding=15)
    indicadores_frame.pack(fill=X, pady=(0, 15))
    
    ttk.Label(indicadores_frame, text="Barra de progreso:").pack(anchor=W, pady=(0, 5))
    progress = ttk.Progressbar(indicadores_frame, value=65, length=400)
    progress.pack(fill=X, pady=(0, 10))
    
    ttk.Label(indicadores_frame, text="Checkbutton:").pack(anchor=W)
    ttk.Checkbutton(indicadores_frame, text="Opción 1").pack(anchor=W)
    ttk.Checkbutton(indicadores_frame, text="Opción 2").pack(anchor=W)
    
    # Info del tema
    info_frame = ttk.Frame(main)
    info_frame.pack(fill=X, side=BOTTOM, pady=(20, 0))
    
    ttk.Label(info_frame, 
             text=f"💡 Este es el tema '{tema}'. Para usarlo en tu aplicación:\nttk.Window(themename='{tema}')",
             font=("Arial", 10, "italic")).pack()
    
    root.mainloop()


def mostrar_menu():
    """Muestra un menú para seleccionar tema"""
    
    root = ttk.Window(themename="darkly")
    root.title("🎨 Selector de Temas - ttkbootstrap")
    root.geometry("600x500")
    
    # Marco principal
    main = ttk.Frame(root, padding=20)
    main.pack(fill=BOTH, expand=True)
    
    # Título
    titulo = ttk.Label(main, text="🎨 SELECCIONA UN TEMA", 
                      font=("Arial", 18, "bold"))
    titulo.pack(pady=(0, 20))
    
    # Descripción
    desc = ttk.Label(main, 
                    text="Haz clic en uno de los botones para ver una demostración del tema.",
                    font=("Arial", 11))
    desc.pack(pady=(0, 20))
    
    # Frame scrollable para los botones
    canvas = tk.Canvas(main, highlightthickness=0)
    scrollbar = ttk.Scrollbar(main, orient=VERTICAL, command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    # Crear botones para cada tema
    for tema in TEMAS:
        btn = ttk.Button(scrollable_frame, text=f"Ver tema: {tema.upper()}", 
                        command=lambda t=tema: crear_demo(t), bootstyle="info")
        btn.pack(fill=X, pady=5)
    
    canvas.pack(side=LEFT, fill=BOTH, expand=True)
    scrollbar.pack(side=RIGHT, fill=Y)
    
    root.mainloop()


if __name__ == "__main__":
    print("Disponibles estos temas en ttkbootstrap:")
    for i, tema in enumerate(TEMAS, 1):
        print(f"  {i}. {tema}")
    print("\nAbriendo selector de temas...")
    mostrar_menu()
