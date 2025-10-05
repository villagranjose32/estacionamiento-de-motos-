#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ventana de configuración de tarifas y turnos para el Sistema de Gestión de Estacionamiento
"""

import os
import sys
import tkinter as tk
from tkinter import messagebox
import csv
import datetime

# Importamos los módulos necesarios del proyecto
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from domain.infra.paths import get_default_data_path, SedePaths

# Definimos los días de la semana directamente para evitar problemas de importación
DIAS_SEMANA = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]

class ConfiguracionWindow:
    def __init__(self, parent=None):
        # Crear ventana principal si no se proporciona un parent
        if parent is None:
            self.root = tk.Tk()
            self.root.title("Configuración del Sistema de Estacionamiento")
            self.root.geometry("1000x700")
            self.is_toplevel = False
        else:
            self.root = tk.Toplevel(parent)
            self.root.title("Configuración del Sistema de Estacionamiento")
            self.root.geometry("1000x700")
            self.is_toplevel = True
            
        # Obtener ruta de datos
        self.sede_paths = SedePaths(get_default_data_path())
        
        # Crear notebook (pestañas)
        self.notebook = tk.Frame(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Variables para los botones de pestañas
        self.current_tab = tk.StringVar(value="general")
        
        # Crear botones para las pestañas
        tabs_frame = tk.Frame(self.notebook)
        tabs_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.btn_general = tk.Button(tabs_frame, text="CONFIGURACIÓN GENERAL", 
                                   font=("Arial", 12, "bold"), bg='lightblue',
                                   command=lambda: self.show_tab("general"))
        self.btn_general.pack(side=tk.LEFT, padx=10, pady=5)
        
        self.btn_turnos = tk.Button(tabs_frame, text="TURNOS", 
                                  font=("Arial", 12, "bold"),
                                  command=lambda: self.show_tab("turnos"))
        self.btn_turnos.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Crear frames para las pestañas
        self.tab_general = tk.Frame(self.notebook)
        self.tab_turnos = tk.Frame(self.notebook)
        
        # Mostrar inicialmente la pestaña general
        self.tab_general.pack(fill=tk.BOTH, expand=True)
        
        # Configurar las pestañas
        self.setup_general_tab()
        self.setup_turnos_tab()
        
        # Cargar datos
        self.cargar_configuracion()
        self.cargar_turnos()
        
        # Frame para botones inferiores
        bottom_frame = tk.Frame(self.root)
        bottom_frame.pack(fill=tk.X, pady=15)
        
        # Botón para guardar toda la configuración (duplicado para facilidad de acceso)
        btn_guardar_todo = tk.Button(bottom_frame, text="GUARDAR CONFIGURACIÓN", 
                                   command=self.guardar_configuracion, 
                                   font=("Arial", 14, "bold"), bg='green', fg='white',
                                   width=30)
        btn_guardar_todo.pack(side=tk.LEFT, padx=20, pady=5)
        
        # Botón para cerrar
        btn_cerrar = tk.Button(bottom_frame, text="CERRAR", command=self.cerrar, 
                             font=("Arial", 12), bg='gray', fg='white', width=15)
        btn_cerrar.pack(side=tk.RIGHT, padx=20, pady=5)
        
        # Centrar la ventana
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        
        # Hacer la ventana modal si es una ventana secundaria
        if self.is_toplevel:
            self.root.transient(parent)
            self.root.grab_set()
            self.root.focus_set()
    
    def show_tab(self, tab_name):
        """Muestra la pestaña seleccionada"""
        # Ocultar todas las pestañas
        self.tab_general.pack_forget()
        self.tab_turnos.pack_forget()
        
        # Restablecer colores de los botones
        self.btn_general.config(bg='SystemButtonFace')
        self.btn_turnos.config(bg='SystemButtonFace')
        
        # Mostrar la pestaña seleccionada
        if tab_name == "general":
            self.tab_general.pack(fill=tk.BOTH, expand=True)
            self.btn_general.config(bg='lightblue')
            self.current_tab.set("general")
        elif tab_name == "turnos":
            self.tab_turnos.pack(fill=tk.BOTH, expand=True)
            self.btn_turnos.config(bg='lightblue')
            self.current_tab.set("turnos")
    
    def setup_general_tab(self):
        """Configura la pestaña de configuración general"""
        # Frame principal con scroll
        main_frame = tk.Frame(self.tab_general)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas con scrollbar
        canvas = tk.Canvas(main_frame)
        scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas)
        
        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Frame para la configuración
        frame = tk.LabelFrame(scroll_frame, text="CONFIGURACIÓN GENERAL", 
                            font=("Arial", 14, "bold"), padx=10, pady=10)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Variables para los campos
        self.var_nombre = tk.StringVar()
        self.var_capacidad = tk.IntVar()
        self.var_gracia_min = tk.IntVar()
        self.var_fraccion_min = tk.IntVar()
        self.var_precio_fraccion = tk.DoubleVar()
        self.var_aplica_diaria = tk.StringVar(value="si")
        self.var_umbral_diaria = tk.IntVar()
        self.var_tarifa_diaria = tk.DoubleVar()
        self.var_aplica_turno = tk.StringVar(value="si")
        self.var_redondeo_turno = tk.StringVar(value="entero")
        self.var_exceso_turno = tk.StringVar(value="mas_barato")
        self.var_regla_eleccion = tk.StringVar(value="mas_barato")
        self.var_prioridad = tk.StringVar(value="turno>diaria>fraccion")
        self.var_cubre_vencimiento = tk.StringVar(value="si")
        self.var_dias_alerta = tk.IntVar()
        
        # Crear grid de etiquetas y entradas
        row = 0
        
        # Nombre del estacionamiento
        tk.Label(frame, text="Nombre del estacionamiento:", 
               font=("Arial", 12)).grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        tk.Entry(frame, textvariable=self.var_nombre, 
               width=35, font=("Arial", 12)).grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)
        row += 1
        
        # Capacidad
        tk.Label(frame, text="Capacidad (lugares):", 
               font=("Arial", 12)).grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        tk.Spinbox(frame, from_=1, to=1000, textvariable=self.var_capacidad, 
                 width=12, font=("Arial", 12)).grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)
        row += 1
        
        # Separador
        tk.Frame(frame, height=2, bg="gray").grid(row=row, column=0, columnspan=4, sticky=tk.EW, padx=5, pady=10)
        row += 1
        
        # Título para tarifas
        tk.Label(frame, text="Configuración de Tarifas", 
               font=("Arial", 14, "bold")).grid(row=row, column=0, columnspan=4, sticky=tk.W, padx=5, pady=5)
        row += 1
        
        # Tarifa por fracción
        tk.Label(frame, text="Minutos de gracia:", 
               font=("Arial", 12)).grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        tk.Spinbox(frame, from_=0, to=60, textvariable=self.var_gracia_min, 
                 width=12, font=("Arial", 12)).grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)
        row += 1
        
        tk.Label(frame, text="Minutos por fracción:", 
               font=("Arial", 12)).grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        tk.Spinbox(frame, from_=1, to=120, textvariable=self.var_fraccion_min, 
                 width=12, font=("Arial", 12)).grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)
        row += 1
        
        # Precio por fracción con signo de $
        tk.Label(frame, text="Precio por fracción:", 
               font=("Arial", 12)).grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        precio_frame = tk.Frame(frame)
        precio_frame.grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)
        tk.Entry(precio_frame, textvariable=self.var_precio_fraccion, 
               width=15, font=("Arial", 12, "bold")).pack(side=tk.LEFT)
        tk.Label(precio_frame, text="$", font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=5)
        row += 1
        
        # Precio por hora (destacado)
        self.var_precio_hora = tk.DoubleVar(value=1000.0)  # Valor por defecto
        
        # Separador
        tk.Frame(frame, height=2, bg="gray").grid(row=row, column=0, columnspan=4, sticky=tk.EW, padx=5, pady=10)
        row += 1
        
        # Título para precio por hora
        tk.Label(frame, text="PRECIO POR HORA", bg="lightblue", 
               font=("Arial", 16, "bold")).grid(row=row, column=0, columnspan=4, sticky=tk.EW, padx=5, pady=10)
        row += 1
        
        # Campo de precio por hora destacado
        hora_label = tk.Label(frame, text="Precio por hora:", font=("Arial", 14, "bold"))
        hora_label.grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        
        precio_hora_frame = tk.Frame(frame)
        precio_hora_frame.grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)
        
        hora_entry = tk.Entry(precio_hora_frame, textvariable=self.var_precio_hora, 
                           width=15, font=("Arial", 16, "bold"))
        hora_entry.pack(side=tk.LEFT)
        tk.Label(precio_hora_frame, text="$", font=("Arial", 16, "bold")).pack(side=tk.LEFT, padx=5)
        row += 1
        
        # Separador después del precio por hora
        tk.Frame(frame, height=2, bg="gray").grid(row=row, column=0, columnspan=4, sticky=tk.EW, padx=5, pady=10)
        row += 1
        
        # Tarifa diaria
        tk.Label(frame, text="Aplica tarifa diaria:", 
               font=("Arial", 12)).grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        frame_diaria = tk.Frame(frame)
        frame_diaria.grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)
        tk.Radiobutton(frame_diaria, text="Sí", variable=self.var_aplica_diaria, value="si", 
                     font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(frame_diaria, text="No", variable=self.var_aplica_diaria, value="no", 
                     font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
        row += 1
        
        tk.Label(frame, text="Umbral para tarifa diaria (horas):", 
               font=("Arial", 12)).grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        tk.Spinbox(frame, from_=1, to=24, textvariable=self.var_umbral_diaria, 
                 width=12, font=("Arial", 12)).grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)
        row += 1
        
        # Tarifa diaria con signo de $
        tk.Label(frame, text="Tarifa diaria:", font=("Arial", 12)).grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        diaria_frame = tk.Frame(frame)
        diaria_frame.grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)
        tk.Entry(diaria_frame, textvariable=self.var_tarifa_diaria, 
               width=15, font=("Arial", 12, "bold")).pack(side=tk.LEFT)
        tk.Label(diaria_frame, text="$", font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=5)
        row += 1
        
        # Tarifa por turno
        tk.Label(frame, text="Aplica tarifa por turno:", 
               font=("Arial", 12)).grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        frame_turno = tk.Frame(frame)
        frame_turno.grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)
        tk.Radiobutton(frame_turno, text="Sí", variable=self.var_aplica_turno, value="si", 
                     font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(frame_turno, text="No", variable=self.var_aplica_turno, value="no", 
                     font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
        row += 1
        
        tk.Label(frame, text="Redondeo de turnos:", 
               font=("Arial", 12)).grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        frame_redondeo = tk.Frame(frame)
        frame_redondeo.grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)
        tk.Radiobutton(frame_redondeo, text="Entero", variable=self.var_redondeo_turno, value="entero", 
                     font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(frame_redondeo, text="Proporcional", variable=self.var_redondeo_turno, value="proporcional", 
                     font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
        row += 1
        
        tk.Label(frame, text="Exceso entre turnos:", 
               font=("Arial", 12)).grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        frame_exceso = tk.Frame(frame)
        frame_exceso.grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)
        tk.Radiobutton(frame_exceso, text="Más barato", variable=self.var_exceso_turno, value="mas_barato", 
                     font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(frame_exceso, text="Más caro", variable=self.var_exceso_turno, value="mas_caro", 
                     font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
        row += 1
        
        # Reglas de elección
        tk.Label(frame, text="Regla de elección de monto:", 
               font=("Arial", 12)).grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        frame_regla = tk.Frame(frame)
        frame_regla.grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)
        tk.Radiobutton(frame_regla, text="Más barato", variable=self.var_regla_eleccion, value="mas_barato", 
                     font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(frame_regla, text="Más caro", variable=self.var_regla_eleccion, value="mas_caro", 
                     font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
        row += 1
        
        tk.Label(frame, text="Prioridad de cálculo:", 
               font=("Arial", 12)).grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        prioridad_options = ["turno>diaria>fraccion", "turno>fraccion>diaria", 
                             "diaria>turno>fraccion", "diaria>fraccion>turno",
                             "fraccion>turno>diaria", "fraccion>diaria>turno"]
        prioridad_combobox = tk.OptionMenu(frame, self.var_prioridad, *prioridad_options)
        prioridad_combobox.config(font=("Arial", 12), width=20)
        prioridad_combobox.grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)
        row += 1
        
        # Separador
        tk.Frame(frame, height=2, bg="gray").grid(row=row, column=0, columnspan=4, sticky=tk.EW, padx=5, pady=10)
        row += 1
        
        # Configuración de abonos
        tk.Label(frame, text="Configuración de Abonos", 
               font=("Arial", 14, "bold")).grid(row=row, column=0, columnspan=4, sticky=tk.W, padx=5, pady=5)
        row += 1
        
        tk.Label(frame, text="Cubre hasta egreso si vence durante estadía:", 
               font=("Arial", 12)).grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        frame_cubre = tk.Frame(frame)
        frame_cubre.grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)
        tk.Radiobutton(frame_cubre, text="Sí", variable=self.var_cubre_vencimiento, value="si", 
                     font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(frame_cubre, text="No", variable=self.var_cubre_vencimiento, value="no", 
                     font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
        row += 1
        
        tk.Label(frame, text="Días de alerta de vencimiento:", 
               font=("Arial", 12)).grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        tk.Spinbox(frame, from_=1, to=30, textvariable=self.var_dias_alerta, 
                 width=12, font=("Arial", 12)).grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)
        row += 1
        
        # Botones de acción
        frame_buttons = tk.Frame(frame)
        frame_buttons.grid(row=row, column=0, columnspan=4, sticky=tk.EW, padx=5, pady=15)
        
        # Botón Guardar más grande y visible
        btn_guardar = tk.Button(frame_buttons, text="GUARDAR CONFIGURACIÓN", 
                              command=self.guardar_configuracion, 
                              font=("Arial", 14, "bold"), bg='green', fg='white',
                              width=30)
        btn_guardar.pack(side=tk.LEFT, padx=10, pady=10)
        
        btn_restaurar = tk.Button(frame_buttons, text="Restaurar", 
                               command=self.cargar_configuracion,
                               font=("Arial", 12), bg='gray', fg='white')
        btn_restaurar.pack(side=tk.LEFT, padx=10, pady=10)
    
    def setup_turnos_tab(self):
        """Configura la pestaña de turnos"""
        frame = tk.Frame(self.tab_turnos)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame para la lista de turnos
        frame_list = tk.LabelFrame(frame, text="TURNOS CONFIGURADOS", 
                                 font=("Arial", 14, "bold"), padx=10, pady=10)
        frame_list.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, padx=5, pady=5)
        
        # Instrucciones para el usuario
        tk.Label(frame_list, text="Haga clic en un turno para editarlo", 
               font=("Arial", 12, "italic")).pack(pady=5)
        
        # Lista para los turnos
        self.listbox_turnos = tk.Listbox(frame_list, font=("Arial", 12), height=15, width=50)
        self.listbox_turnos.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, padx=5, pady=5)
        
        # Scrollbar para la lista
        scrollbar = tk.Scrollbar(frame_list)
        scrollbar.pack(fill=tk.Y, side=tk.RIGHT)
        
        # Configurar scrollbar
        self.listbox_turnos.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.listbox_turnos.yview)
        
        # Vincular evento de selección
        self.listbox_turnos.bind('<<ListboxSelect>>', self.on_turno_selected)
        
        # Frame para editar/añadir turnos
        frame_edit = tk.LabelFrame(frame, text="EDITAR / AÑADIR TURNO", 
                                 font=("Arial", 14, "bold"), padx=10, pady=10)
        frame_edit.pack(fill=tk.BOTH, expand=True, side=tk.RIGHT, padx=5, pady=5)
        
        # Variables para los campos de turno
        self.var_turno_nombre = tk.StringVar()
        self.var_turno_inicio = tk.StringVar()
        self.var_turno_fin = tk.StringVar()
        self.var_turno_precio = tk.DoubleVar()
        self.var_turno_activo = tk.BooleanVar(value=True)
        
        # Variables para los días de la semana
        self.var_dia_lunes = tk.BooleanVar(value=True)
        self.var_dia_martes = tk.BooleanVar(value=True)
        self.var_dia_miercoles = tk.BooleanVar(value=True)
        self.var_dia_jueves = tk.BooleanVar(value=True)
        self.var_dia_viernes = tk.BooleanVar(value=True)
        self.var_dia_sabado = tk.BooleanVar(value=True)
        self.var_dia_domingo = tk.BooleanVar(value=True)
        
        # Crear campos de edición
        row = 0
        
        # Nombre del turno
        tk.Label(frame_edit, text="Nombre del turno:", 
               font=("Arial", 13)).grid(row=row, column=0, sticky=tk.W, padx=10, pady=8)
        tk.Entry(frame_edit, textvariable=self.var_turno_nombre, 
               width=25, font=("Arial", 13)).grid(row=row, column=1, sticky=tk.W, padx=10, pady=8)
        row += 1
        
        # Hora de inicio
        tk.Label(frame_edit, text="Hora de inicio (HH:MM):", 
               font=("Arial", 13)).grid(row=row, column=0, sticky=tk.W, padx=10, pady=8)
        tk.Entry(frame_edit, textvariable=self.var_turno_inicio, 
               width=15, font=("Arial", 13)).grid(row=row, column=1, sticky=tk.W, padx=10, pady=8)
        row += 1
        
        # Hora de fin
        tk.Label(frame_edit, text="Hora de fin (HH:MM):", 
               font=("Arial", 13)).grid(row=row, column=0, sticky=tk.W, padx=10, pady=8)
        tk.Entry(frame_edit, textvariable=self.var_turno_fin, 
               width=15, font=("Arial", 13)).grid(row=row, column=1, sticky=tk.W, padx=10, pady=8)
        row += 1
        
        # Precio
        tk.Label(frame_edit, text="Precio del turno:", 
               font=("Arial", 13, "bold")).grid(row=row, column=0, sticky=tk.W, padx=10, pady=8)
        precio_frame = tk.Frame(frame_edit)
        precio_frame.grid(row=row, column=1, sticky=tk.W, padx=10, pady=8)
        tk.Entry(precio_frame, textvariable=self.var_turno_precio, 
               width=15, font=("Arial", 14, "bold")).pack(side=tk.LEFT)
        tk.Label(precio_frame, text="$", font=("Arial", 14, "bold")).pack(side=tk.LEFT, padx=5)
        row += 1
        
        # Días de la semana
        tk.Label(frame_edit, text="Días aplicables:", 
               font=("Arial", 13, "bold")).grid(row=row, column=0, sticky=tk.W, padx=10, pady=8)
        row += 1
        
        # Frame para los checkboxes de días
        frame_dias = tk.Frame(frame_edit)
        frame_dias.grid(row=row, column=0, columnspan=2, sticky=tk.W, padx=10, pady=5)
        
        tk.Checkbutton(frame_dias, text="Lunes", variable=self.var_dia_lunes, 
                     font=("Arial", 12)).grid(row=0, column=0, sticky=tk.W, padx=8, pady=3)
        tk.Checkbutton(frame_dias, text="Martes", variable=self.var_dia_martes, 
                     font=("Arial", 12)).grid(row=0, column=1, sticky=tk.W, padx=8, pady=3)
        tk.Checkbutton(frame_dias, text="Miércoles", variable=self.var_dia_miercoles, 
                     font=("Arial", 12)).grid(row=1, column=0, sticky=tk.W, padx=8, pady=3)
        tk.Checkbutton(frame_dias, text="Jueves", variable=self.var_dia_jueves, 
                     font=("Arial", 12)).grid(row=1, column=1, sticky=tk.W, padx=8, pady=3)
        tk.Checkbutton(frame_dias, text="Viernes", variable=self.var_dia_viernes, 
                     font=("Arial", 12)).grid(row=2, column=0, sticky=tk.W, padx=8, pady=3)
        tk.Checkbutton(frame_dias, text="Sábado", variable=self.var_dia_sabado, 
                     font=("Arial", 12)).grid(row=2, column=1, sticky=tk.W, padx=8, pady=3)
        tk.Checkbutton(frame_dias, text="Domingo", variable=self.var_dia_domingo, 
                     font=("Arial", 12)).grid(row=3, column=0, sticky=tk.W, padx=8, pady=3)
        
        row += 4  # Ajustar por los 4 rows de los días
        
        # Activo
        tk.Checkbutton(frame_edit, text="Turno activo", variable=self.var_turno_activo, 
                     font=("Arial", 12)).grid(row=row, column=0, columnspan=2, sticky=tk.W, padx=10, pady=8)
        row += 1
        
        # Instrucciones para el usuario
        tk.Label(frame_edit, text="Para editar un turno: Seleccione un turno de la lista y modifique los valores.", 
               font=("Arial", 12, "italic")).grid(row=row, column=0, columnspan=2, sticky=tk.W, padx=10, pady=8)
        row += 1
        
        # Botones de acción
        frame_buttons = tk.Frame(frame_edit)
        frame_buttons.grid(row=row, column=0, columnspan=2, sticky=tk.EW, padx=10, pady=15)
        
        self.btn_nuevo = tk.Button(frame_buttons, text="Nuevo Turno", 
                                 command=self.nuevo_turno,
                                 font=("Arial", 12, "bold"), bg='blue', fg='white',
                                 width=15)
        self.btn_nuevo.pack(side=tk.LEFT, padx=10, pady=10)
        
        self.btn_guardar_turno = tk.Button(frame_buttons, text="GUARDAR TURNO", 
                                        command=self.guardar_turno,
                                        font=("Arial", 12, "bold"), bg='green', fg='white',
                                        width=20)
        self.btn_guardar_turno.pack(side=tk.LEFT, padx=10, pady=10)
        
        self.btn_eliminar = tk.Button(frame_buttons, text="Eliminar", 
                                    command=self.eliminar_turno,
                                    state=tk.DISABLED, font=("Arial", 12),
                                    bg='red', fg='white', width=15)
        self.btn_eliminar.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Variable para controlar si estamos editando o añadiendo
        self.editando_turno = False
        self.turno_seleccionado = None
    
    def cargar_configuracion(self):
        """Carga la configuración desde el archivo"""
        try:
            with open(self.sede_paths.config_txt, 'r', encoding='utf-8') as f:
                # Leer encabezado para determinar si existe el campo precio_por_hora
                encabezado = f.readline().strip()
                tiene_precio_hora = "precio_por_hora" in encabezado
                
                # Leer la línea de configuración
                for line in f:
                    # Dividir por punto y coma
                    campos = line.strip().split(';')
                    if len(campos) >= 15:  # Asegurar que hay suficientes campos
                        self.var_nombre.set(campos[0])
                        self.var_capacidad.set(int(campos[1]))
                        self.var_gracia_min.set(int(campos[2]))
                        self.var_fraccion_min.set(int(campos[3]))
                        self.var_precio_fraccion.set(float(campos[4]))
                        self.var_aplica_diaria.set(campos[5])
                        self.var_umbral_diaria.set(int(campos[6]))
                        self.var_tarifa_diaria.set(float(campos[7]))
                        self.var_aplica_turno.set(campos[8])
                        self.var_redondeo_turno.set(campos[9])
                        self.var_exceso_turno.set(campos[10])
                        self.var_regla_eleccion.set(campos[11])
                        self.var_prioridad.set(campos[12])
                        self.var_cubre_vencimiento.set(campos[13])
                        self.var_dias_alerta.set(int(campos[14]))
                        
                        # Si existe el campo precio_por_hora, cargarlo
                        if tiene_precio_hora and len(campos) >= 16:
                            try:
                                self.var_precio_hora.set(float(campos[15]))
                            except:
                                self.var_precio_hora.set(1000.0)  # Valor por defecto
                    break  # Solo procesamos la primera línea de datos
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la configuración: {e}")
    
    def guardar_configuracion(self):
        """Guarda la configuración en el archivo"""
        try:
            # Primero leer el archivo para mantener el encabezado
            encabezado = ""
            try:
                with open(self.sede_paths.config_txt, 'r', encoding='utf-8') as f:
                    encabezado = f.readline().strip()
                    # Añadir campo precio_por_hora si no existe
                    if "precio_por_hora" not in encabezado:
                        encabezado += ";precio_por_hora"
            except:
                encabezado = "nombre;capacidad;gracia_min;fraccion_min;precio_por_fraccion;aplica_tarifa_diaria;umbral_diaria_horas;tarifa_diaria;aplica_tarifa_por_turno;redondeo_turno;exceso_turno;regla_eleccion_monto;prioridad_precio;cubre_hasta_egreso_si_vencia_durante_estadia;dias_alerta_vencimiento;precio_por_hora"
            
            # Guardar la configuración
            with open(self.sede_paths.config_txt, 'w', encoding='utf-8') as f:
                # Escribir encabezado
                f.write(encabezado + "\n")
                
                # Escribir valores
                f.write(f"{self.var_nombre.get()};")
                f.write(f"{self.var_capacidad.get()};")
                f.write(f"{self.var_gracia_min.get()};")
                f.write(f"{self.var_fraccion_min.get()};")
                f.write(f"{self.var_precio_fraccion.get()};")
                f.write(f"{self.var_aplica_diaria.get()};")
                f.write(f"{self.var_umbral_diaria.get()};")
                f.write(f"{self.var_tarifa_diaria.get()};")
                f.write(f"{self.var_aplica_turno.get()};")
                f.write(f"{self.var_redondeo_turno.get()};")
                f.write(f"{self.var_exceso_turno.get()};")
                f.write(f"{self.var_regla_eleccion.get()};")
                f.write(f"{self.var_prioridad.get()};")
                f.write(f"{self.var_cubre_vencimiento.get()};")
                f.write(f"{self.var_dias_alerta.get()};")
                f.write(f"{self.var_precio_hora.get()}\n")
            
            messagebox.showinfo("Éxito", "Configuración guardada correctamente")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar la configuración: {e}")
    
    def cargar_turnos(self):
        """Carga los turnos desde el archivo"""
        # Limpiar el listbox
        self.listbox_turnos.delete(0, tk.END)
        
        self.turnos_data = []  # Lista para almacenar los datos completos de turnos
        
        try:
            with open(self.sede_paths.turnos_txt, 'r', encoding='utf-8') as f:
                # Saltar la primera línea (encabezado)
                next(f)
                
                # Leer los turnos
                for line in f:
                    campos = line.strip().split(';')
                    if len(campos) >= 6:
                        nombre = campos[0]
                        hora_inicio = campos[1]
                        hora_fin = campos[2]
                        precio = campos[3]
                        dias = campos[4]
                        activo = "Sí" if campos[5].lower() == "si" else "No"
                        
                        # Añadir al listbox
                        self.listbox_turnos.insert(tk.END, 
                            f"{nombre} ({hora_inicio}-{hora_fin}) - ${precio} - {activo}")
                        
                        # Guardar datos completos
                        self.turnos_data.append({
                            'nombre': nombre,
                            'hora_inicio': hora_inicio,
                            'hora_fin': hora_fin,
                            'precio': precio,
                            'dias': dias,
                            'activo': campos[5].lower()
                        })
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los turnos: {e}")
    
    def on_turno_selected(self, event):
        """Maneja la selección de un turno en el listbox"""
        selection = self.listbox_turnos.curselection()
        if not selection:
            self.btn_eliminar.config(state=tk.DISABLED)
            return
        
        # Habilitar botón de eliminar
        self.btn_eliminar.config(state=tk.NORMAL)
        
        # Obtener índice del turno seleccionado
        index = selection[0]
        
        # Obtener datos del turno seleccionado
        turno = self.turnos_data[index]
        
        # Establecer variables
        self.var_turno_nombre.set(turno['nombre'])
        self.var_turno_inicio.set(turno['hora_inicio'])
        self.var_turno_fin.set(turno['hora_fin'])
        self.var_turno_precio.set(float(turno['precio']))
        self.var_turno_activo.set(turno['activo'] == "si")
        
        # Procesar días
        dias = turno['dias'].split(',')
        self.var_dia_lunes.set('lunes' in dias)
        self.var_dia_martes.set('martes' in dias)
        self.var_dia_miercoles.set('miercoles' in dias)
        self.var_dia_jueves.set('jueves' in dias)
        self.var_dia_viernes.set('viernes' in dias)
        self.var_dia_sabado.set('sabado' in dias)
        self.var_dia_domingo.set('domingo' in dias)
        
        # Establecer modo edición
        self.editando_turno = True
        self.turno_seleccionado = index
    
    def nuevo_turno(self):
        """Prepara la interfaz para un nuevo turno"""
        # Limpiar variables
        self.var_turno_nombre.set("")
        self.var_turno_inicio.set("")
        self.var_turno_fin.set("")
        self.var_turno_precio.set(0.0)
        self.var_turno_activo.set(True)
        
        # Días por defecto
        self.var_dia_lunes.set(True)
        self.var_dia_martes.set(True)
        self.var_dia_miercoles.set(True)
        self.var_dia_jueves.set(True)
        self.var_dia_viernes.set(True)
        self.var_dia_sabado.set(False)
        self.var_dia_domingo.set(False)
        
        # Desactivar modo edición
        self.editando_turno = False
        self.turno_seleccionado = None
        self.btn_eliminar.config(state=tk.DISABLED)
    
    def guardar_turno(self):
        """Guarda el turno actual (nuevo o editado)"""
        # Validar campos
        if not self.validar_turno():
            return
        
        # Preparar datos del turno
        nombre = self.var_turno_nombre.get()
        hora_inicio = self.var_turno_inicio.get()
        hora_fin = self.var_turno_fin.get()
        precio = self.var_turno_precio.get()
        
        # Preparar días
        dias = []
        if self.var_dia_lunes.get(): dias.append('lunes')
        if self.var_dia_martes.get(): dias.append('martes')
        if self.var_dia_miercoles.get(): dias.append('miercoles')
        if self.var_dia_jueves.get(): dias.append('jueves')
        if self.var_dia_viernes.get(): dias.append('viernes')
        if self.var_dia_sabado.get(): dias.append('sabado')
        if self.var_dia_domingo.get(): dias.append('domingo')
        
        dias_str = ','.join(dias)
        activo = "si" if self.var_turno_activo.get() else "no"
        
        # Preparar datos del turno
        turno_data = {
            'nombre': nombre,
            'hora_inicio': hora_inicio,
            'hora_fin': hora_fin,
            'precio': str(precio),
            'dias': dias_str,
            'activo': activo
        }
        
        # Texto para mostrar en el listbox
        turno_text = f"{nombre} ({hora_inicio}-{hora_fin}) - ${precio} - {'Sí' if activo == 'si' else 'No'}"
        
        # Si estamos editando, actualizar en el listbox y la lista de datos
        if self.editando_turno and self.turno_seleccionado is not None:
            self.listbox_turnos.delete(self.turno_seleccionado)
            self.listbox_turnos.insert(self.turno_seleccionado, turno_text)
            self.turnos_data[self.turno_seleccionado] = turno_data
        else:
            # Si es nuevo, añadir al listbox y a la lista de datos
            self.listbox_turnos.insert(tk.END, turno_text)
            self.turnos_data.append(turno_data)
        
        # Guardar todos los turnos en el archivo
        self.guardar_todos_turnos()
        
        # Resetear para un nuevo turno
        self.nuevo_turno()
    
    def validar_turno(self):
        """Valida los campos del turno actual"""
        # Validar nombre
        if not self.var_turno_nombre.get().strip():
            messagebox.showerror("Error", "Debe ingresar un nombre para el turno")
            return False
        
        # Validar hora de inicio
        try:
            hora_inicio = self.var_turno_inicio.get()
            if not hora_inicio or ":" not in hora_inicio:
                raise ValueError()
            hora, minuto = hora_inicio.split(":")
            hora = int(hora)
            minuto = int(minuto)
            if hora < 0 or hora > 23 or minuto < 0 or minuto > 59:
                raise ValueError()
        except:
            messagebox.showerror("Error", "Hora de inicio inválida. Use formato HH:MM")
            return False
        
        # Validar hora de fin
        try:
            hora_fin = self.var_turno_fin.get()
            if not hora_fin or ":" not in hora_fin:
                raise ValueError()
            hora, minuto = hora_fin.split(":")
            hora = int(hora)
            minuto = int(minuto)
            if hora < 0 or hora > 23 or minuto < 0 or minuto > 59:
                raise ValueError()
        except:
            messagebox.showerror("Error", "Hora de fin inválida. Use formato HH:MM")
            return False
        
        # Validar precio
        try:
            precio = float(self.var_turno_precio.get())
            if precio <= 0:
                raise ValueError()
        except:
            messagebox.showerror("Error", "Precio inválido. Debe ser un número mayor a cero")
            return False
        
        # Validar que al menos un día esté seleccionado
        if not (self.var_dia_lunes.get() or self.var_dia_martes.get() or 
                self.var_dia_miercoles.get() or self.var_dia_jueves.get() or 
                self.var_dia_viernes.get() or self.var_dia_sabado.get() or 
                self.var_dia_domingo.get()):
            messagebox.showerror("Error", "Debe seleccionar al menos un día de la semana")
            return False
        
        return True
    
    def eliminar_turno(self):
        """Elimina el turno seleccionado"""
        selection = self.listbox_turnos.curselection()
        if not selection:
            return
        
        # Confirmar eliminación
        if messagebox.askyesno("Confirmar", "¿Está seguro que desea eliminar este turno?"):
            # Obtener índice
            index = selection[0]
            
            # Eliminar del listbox y de la lista de datos
            self.listbox_turnos.delete(index)
            del self.turnos_data[index]
            
            # Guardar todos los turnos
            self.guardar_todos_turnos()
            
            # Resetear para un nuevo turno
            self.nuevo_turno()
    
    def guardar_todos_turnos(self):
        """Guarda todos los turnos en el archivo"""
        try:
            # Primero leer el archivo para mantener el encabezado
            encabezado = ""
            try:
                with open(self.sede_paths.turnos_txt, 'r', encoding='utf-8') as f:
                    encabezado = f.readline().strip()
            except:
                encabezado = "nombre;hora_inicio;hora_fin;precio;dias;activo"
            
            # Guardar todos los turnos
            with open(self.sede_paths.turnos_txt, 'w', encoding='utf-8') as f:
                # Escribir encabezado
                f.write(encabezado + "\n")
                
                # Escribir cada turno
                for turno in self.turnos_data:
                    f.write(f"{turno['nombre']};")
                    f.write(f"{turno['hora_inicio']};")
                    f.write(f"{turno['hora_fin']};")
                    f.write(f"{turno['precio']};")
                    f.write(f"{turno['dias']};")
                    f.write(f"{turno['activo']}\n")
            
            messagebox.showinfo("Éxito", "Turnos guardados correctamente")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron guardar los turnos: {e}")
    
    def cerrar(self):
        """Cierra la ventana"""
        self.root.destroy()

    def run(self):
        """Ejecuta la ventana principal"""
        if not self.is_toplevel:
            self.root.mainloop()

if __name__ == "__main__":
    app = ConfiguracionWindow()
    app.run()
