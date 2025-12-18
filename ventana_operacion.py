import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from datetime import datetime
import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from domain.infra.paths import SedePaths
from domain.infra.services.ingreso_service_nuevo import IngresoServiceNuevo
from domain.infra.services.egreso_service_nuevo import EgresoServiceNuevo
from ventana_abonos import mostrar_gestion_abonos


class VentanaOperacion:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Estacionamiento - Operación")
        self.root.geometry("1200x750")
        
        # Configurar servicios
        # Usar SedePaths con ruta predeterminada (detectará automáticamente)
        self.paths = SedePaths()
        print(f"Ruta de datos: {self.paths.root}")
        self.ingreso_service = IngresoServiceNuevo(self.paths)
        self.egreso_service = EgresoServiceNuevo(self.paths)
        
        # Variables
        self.ficha_var = tk.StringVar()
        self.dni_var = tk.StringVar()
        
        self.crear_interfaz()
        self.configurar_eventos()
        self.actualizar_estado()
        
        # Foco inicial
        self.entry_ficha.focus_set()
    
    def crear_interfaz(self):
        # Frame principal con padding
        main_frame = ttk.Frame(self.root, padding=15)
        main_frame.pack(fill=BOTH, expand=True)
        
        # Título con estilo
        titulo = ttk.Label(main_frame, text="🏍️ SISTEMA DE ESTACIONAMIENTO", 
                          font=("Segoe UI", 20, "bold"))
        titulo.pack(pady=(0, 20))
        
        # Frame de operación con LabelFrame
        op_frame = ttk.Labelframe(main_frame, text="⚙️  OPERACIÓN", padding=15)
        op_frame.pack(fill=X, pady=(0, 15))
        
        # Campos de entrada en grid
        campos_frame = ttk.Frame(op_frame)
        campos_frame.pack(fill=X, pady=(0, 15))
        
        # Nro de Ficha
        ttk.Label(campos_frame, text="Nro. Ficha:", font=("Segoe UI", 12, "bold")).grid(row=0, column=0, sticky=W, padx=5)
        self.entry_ficha = ttk.Entry(campos_frame, textvariable=self.ficha_var, 
                                     font=("Segoe UI", 16, "bold"), width=10, justify='center')
        self.entry_ficha.grid(row=0, column=1, padx=10)
        
        # Estado Ficha
        self.lbl_estado_ficha = tk.Label(campos_frame, text="", font=("Segoe UI", 11), bg="#1e1e1e", fg="white")
        self.lbl_estado_ficha.grid(row=0, column=2, padx=5)
        
        # DNI
        ttk.Label(campos_frame, text="DNI:", font=("Segoe UI", 12, "bold")).grid(row=0, column=3, padx=5)
        self.entry_dni = ttk.Entry(campos_frame, textvariable=self.dni_var, 
                                  font=("Segoe UI", 14, "bold"), width=15, justify='center')
        self.entry_dni.grid(row=0, column=4, padx=10)
        
        # Estado DNI
        self.lbl_estado_dni = tk.Label(campos_frame, text="Sin DNI", font=("Segoe UI", 11), bg="#1e1e1e", fg="white")
        self.lbl_estado_dni.grid(row=0, column=5, padx=10)
        
        # Botón buscar DNI
        self.btn_buscar = ttk.Button(campos_frame, text="🔍 Buscar (Alt+B)", 
                                     command=self.buscar_persona)
        self.btn_buscar.grid(row=0, column=6, padx=10)
        
        # Frame de botones principales
        botones_frame = ttk.Frame(op_frame)
        botones_frame.pack(fill=X, pady=(0, 10))
        
        self.btn_ingreso = ttk.Button(botones_frame, text="✅ INGRESO (Enter)", 
                                     command=self.procesar_ingreso, bootstyle="success-lg")
        self.btn_ingreso.pack(side=LEFT, padx=5, ipady=8, ipadx=10)
        
        self.btn_salida = ttk.Button(botones_frame, text="❌ SALIDA (F2)", 
                                    command=self.procesar_salida, bootstyle="danger-lg")
        self.btn_salida.pack(side=LEFT, padx=5, ipady=8, ipadx=10)
        
        self.btn_validar = ttk.Button(botones_frame, text="✔ VALIDAR (Alt+A)", 
                                     command=self.validar_dni, bootstyle="info-lg")
        self.btn_validar.pack(side=LEFT, padx=5, ipady=8, ipadx=10)
        
        self.btn_gestionar_abono = ttk.Button(botones_frame, text="💳 ABONOS (F3)", 
                                             command=self.gestionar_abonos, bootstyle="warning-lg")
        self.btn_gestionar_abono.pack(side=LEFT, padx=5, ipady=8, ipadx=10)
        
        self.btn_limpiar = ttk.Button(botones_frame, text="🗑️ LIMPIAR (Esc)", 
                                     command=self.limpiar_campos, bootstyle="secondary")
        self.btn_limpiar.pack(side=LEFT, padx=5, ipady=8, ipadx=10)
        
        # Frame de estado
        estado_frame = ttk.Labelframe(main_frame, text="📊 ESTADO EN TIEMPO REAL", padding=15)
        estado_frame.pack(fill=X, pady=(0, 15))
        
        # Contador principal
        contador_frame = ttk.Frame(estado_frame)
        contador_frame.pack(fill=X, pady=(0, 15))
        
        self.lbl_contador = ttk.Label(contador_frame, text="Ocupadas: 0/0", 
                                     font=("Arial", 16, "bold"))
        self.lbl_contador.pack(side=LEFT, padx=10)
        
        # Porcentaje ocupación
        self.lbl_porcentaje = tk.Label(contador_frame, text="0%", 
                                       font=("Arial", 14, "bold"), fg="green", bg="#1e1e1e")
        self.lbl_porcentaje.pack(side=RIGHT, padx=10)
        
        # Barra de progreso visual con Canvas
        barra_frame = ttk.Frame(estado_frame)
        barra_frame.pack(fill=X, pady=(0, 10))
        
        # Canvas para la barra personalizada
        self.canvas_barra = tk.Canvas(barra_frame, height=30, 
                                      bg="#2a2a2a", highlightthickness=0,
                                      relief=FLAT, bd=0)
        self.canvas_barra.pack(fill=X, padx=5, pady=5)
        
        # Variables para la barra
        self.barra_ocupacion = 0
        self.barra_capacidad = 100
        self.dibujar_barra()
        
        # Texto debajo de la barra
        self.lbl_estado_barra = tk.Label(estado_frame, 
                                         text="Disponibles: 100 - Ocupadas: 0", 
                                         font=("Segoe UI", 10), bg="#1e1e1e", fg="white")
        self.lbl_estado_barra.pack(pady=(0, 5))
        
        # Frame de listas (3 columnas)
        listas_frame = ttk.Frame(main_frame)
        listas_frame.pack(fill=BOTH, expand=True)
        
        # Ocupadas
        ocupadas_frame = ttk.Labelframe(listas_frame, text="🔴 FICHAS OCUPADAS", padding=5)
        ocupadas_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 5))
        
        self.lista_ocupadas = tk.Listbox(ocupadas_frame, font=("Segoe UI", 11), height=15)
        scroll_ocupadas = ttk.Scrollbar(ocupadas_frame, command=self.lista_ocupadas.yview)
        self.lista_ocupadas.config(yscrollcommand=scroll_ocupadas.set)
        self.lista_ocupadas.pack(side=LEFT, fill=BOTH, expand=True)
        scroll_ocupadas.pack(side=RIGHT, fill=Y)
        
        # Libres
        libres_frame = ttk.Labelframe(listas_frame, text="🟢 FICHAS LIBRES", padding=5)
        libres_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=(5, 5))
        
        self.lista_libres = tk.Listbox(libres_frame, font=("Segoe UI", 11), height=15)
        scroll_libres = ttk.Scrollbar(libres_frame, command=self.lista_libres.yview)
        self.lista_libres.config(yscrollcommand=scroll_libres.set)
        self.lista_libres.pack(side=LEFT, fill=BOTH, expand=True)
        scroll_libres.pack(side=RIGHT, fill=Y)
        
        # Mensajes
        mensajes_frame = ttk.Labelframe(listas_frame, text="💬 MENSAJES", padding=5)
        mensajes_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=(5, 0))
        
        self.text_mensajes = tk.Text(mensajes_frame, font=("Segoe UI", 10), wrap=WORD, height=15)
        scroll_mensajes = ttk.Scrollbar(mensajes_frame, command=self.text_mensajes.yview)
        self.text_mensajes.config(yscrollcommand=scroll_mensajes.set)
        self.text_mensajes.pack(side=LEFT, fill=BOTH, expand=True)
        scroll_mensajes.pack(side=RIGHT, fill=Y)
    
    def configurar_eventos(self):
        # Atajos de teclado
        self.root.bind('<Return>', self.procesar_ingreso)
        self.root.bind('<F2>', self.procesar_salida)
        self.root.bind('<F3>', self.gestionar_abonos)
        self.root.bind('<Alt-a>', self.validar_dni)
        self.root.bind('<Alt-b>', self.buscar_persona)  # Nuevo atajo para buscar
        self.root.bind('<Escape>', self.limpiar_campos)
        
        # Eventos de cambio
        self.entry_ficha.bind('<KeyRelease>', self.on_ficha_change)
        self.entry_dni.bind('<KeyRelease>', self.on_dni_change)
    
    def dibujar_barra(self):
        """Dibuja la barra de ocupación con colores dinámicos"""
        self.canvas_barra.delete("all")
        
        # Calcular porcentaje
        if self.barra_capacidad > 0:
            porcentaje = (self.barra_ocupacion / self.barra_capacidad) * 100
        else:
            porcentaje = 0
        
        # Obtener ancho del canvas
        ancho_canvas = self.canvas_barra.winfo_width()
        if ancho_canvas <= 1:
            ancho_canvas = 400
        
        # Calcular ancho de la barra ocupada
        ancho_ocupado = int((porcentaje / 100) * (ancho_canvas - 10))
        
        # Elegir color según ocupación
        if porcentaje <= 50:
            color = "#28a745"  # Verde
        elif porcentaje <= 80:
            color = "#ffc107"  # Amarillo/Naranja
        else:
            color = "#dc3545"  # Rojo
        
        # Fondo de la barra (gris)
        self.canvas_barra.create_rectangle(5, 5, ancho_canvas - 5, 25,
                                          fill="#444444", outline="#666666", width=1)
        
        # Barra ocupada
        if ancho_ocupado > 0:
            self.canvas_barra.create_rectangle(5, 5, 5 + ancho_ocupado, 25,
                                              fill=color, outline="", width=0)
        
        # Porcentaje en el centro
        self.canvas_barra.create_text(ancho_canvas // 2, 15,
                                     text=f"{porcentaje:.0f}%",
                                     font=("Segoe UI", 10, "bold"),
                                     fill="white")
    
    def actualizar_barra(self, ocupadas, capacidad):
        """Actualiza la barra de ocupación"""
        self.barra_ocupacion = ocupadas
        self.barra_capacidad = capacidad
        self.dibujar_barra()
        
        # Actualizar porcentaje
        if capacidad > 0:
            porcentaje = (ocupadas / capacidad) * 100
            if porcentaje <= 50:
                color_texto = "green"
            elif porcentaje <= 80:
                color_texto = "orange"
            else:
                color_texto = "red"
        else:
            porcentaje = 0
            color_texto = "green"
        
        self.lbl_porcentaje.config(text=f"{porcentaje:.1f}%", foreground=color_texto)
        
        # Actualizar texto de disponibles
        disponibles = capacidad - ocupadas
        self.lbl_estado_barra.config(text=f"Disponibles: {disponibles} - Ocupadas: {ocupadas}")
    
    def configurar_eventos(self):
        # Atajos de teclado
        self.root.bind('<Return>', self.procesar_ingreso)
        self.root.bind('<F2>', self.procesar_salida)
        self.root.bind('<F3>', self.gestionar_abonos)
        self.root.bind('<Alt-a>', self.validar_dni)
        self.root.bind('<Alt-b>', self.buscar_persona)
        self.root.bind('<Escape>', self.limpiar_campos)
        
        # Eventos de cambio
        self.entry_ficha.bind('<KeyRelease>', self.on_ficha_change)
        self.entry_dni.bind('<KeyRelease>', self.on_dni_change)
    
    def agregar_mensaje(self, mensaje):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.text_mensajes.insert(tk.END, f"[{timestamp}] {mensaje}\n")
        self.text_mensajes.see(tk.END)
    
    def on_ficha_change(self, event):
        ficha_str = self.ficha_var.get().strip()
        if not ficha_str:
            self.entry_ficha.config(bg='white')
            self.lbl_estado_ficha.config(text="")
            return
        
        if ficha_str.isdigit():
            config = self.ingreso_service.config
            ficha = int(ficha_str)
            
            # Verificar rango válido
            if ficha < 1 or ficha > config.capacidad:
                self.entry_ficha.config(bg='#ffcccc')
                self.lbl_estado_ficha.config(text=f"⚠️ Fuera de rango (1-{config.capacidad})", foreground='red')
                return
            
            # Verificar estado actual de la ficha (ocupada/disponible)
            movimiento = self.egreso_service.movimientos_repo.obtener_abierto_por_ficha(ficha)
            if movimiento:
                # Ficha ocupada
                self.entry_ficha.config(bg='white')
                self.lbl_estado_ficha.config(text="✅ Ocupada", foreground='green')
                
                # Mostrar detalles del ingreso
                try:
                    hora_entrada = movimiento.get("hora_entrada", "")
                    dni = movimiento.get("dni", "")
                    if dni:
                        persona = self.ingreso_service.personas_repo.buscar_por_dni(dni)
                        nombre_persona = f"{persona.nombre} {persona.apellido}" if persona else "Desconocido"
                        self.lbl_estado_ficha.config(text=f"✅ Ocupada - {nombre_persona}", foreground='green')
                except:
                    pass
            else:
                # Ficha libre
                self.entry_ficha.config(bg='white')
                self.lbl_estado_ficha.config(text="⚠️ Disponible", foreground='orange')
        else:
            self.entry_ficha.config(bg='#ffcccc')
            self.lbl_estado_ficha.config(text="⚠️ Número inválido", foreground='red')
    
    def on_dni_change(self, event):
        dni = self.dni_var.get().strip()
        if not dni:
            self.lbl_estado_dni.config(text="Sin DNI", foreground='black')
            return
        
        try:
            es_valido, mensaje, abono, persona = self.ingreso_service.validar_dni(dni)
            if not es_valido:
                self.lbl_estado_dni.config(text="❌ DNI no registrado - F3 para gestionar", foreground='red')
            elif abono:
                estado = abono.estado()
                if estado.value == 'vigente':
                    self.lbl_estado_dni.config(text="✅ Abono VIGENTE", fg='green')
                elif estado.value == 'por_vencer':
                    self.lbl_estado_dni.config(text="⚠ Abono POR VENCER - F3 para renovar", fg='orange')
                else:  # vencido
                    self.lbl_estado_dni.config(text="❌ Abono VENCIDO - F3 para renovar", fg='red')
            else:
                self.lbl_estado_dni.config(text="⚠ Sin abono - F3 para crear", fg='orange')
        except:
            self.lbl_estado_dni.config(text="Error validación", fg='red')
    
    def procesar_ingreso(self, event=None):
        ficha_str = self.ficha_var.get().strip()
        if not ficha_str or not ficha_str.isdigit():
            messagebox.showerror("Error", "Debe ingresar un número de ficha válido")
            self.entry_ficha.focus_set()
            return
        
        ficha = int(ficha_str)
        dni = self.dni_var.get().strip() if self.dni_var.get().strip() else None
        
        exito, mensaje, resultado = self.ingreso_service.ingresar_vehiculo(ficha, dni)
        
        if exito:
            self.agregar_mensaje(f"INGRESO: {mensaje}")
            self.limpiar_campos()
            self.actualizar_estado()
        else:
            self.agregar_mensaje(f"ERROR INGRESO: {mensaje}")
            messagebox.showerror("Error", mensaje)
        
        self.entry_ficha.focus_set()
    
    def procesar_salida(self, event=None):
        ficha_str = self.ficha_var.get().strip()
        if not ficha_str or not ficha_str.isdigit():
            messagebox.showerror("Error", "Debe ingresar un número de ficha válido")
            self.entry_ficha.focus_set()
            return
        
        ficha = int(ficha_str)
        
        # Verificar primero si la ficha está ocupada
        movimiento = self.egreso_service.movimientos_repo.obtener_abierto_por_ficha(ficha)
        if not movimiento:
            error_msg = f"⚠️ La ficha {ficha} no tiene registro de entrada en el sistema"
            self.agregar_mensaje(f"ERROR EGRESO: {error_msg}")
            messagebox.showerror("Error", error_msg)
            self.entry_ficha.focus_set()
            return
        
        # Procesar el egreso
        exito, mensaje, detalle = self.egreso_service.procesar_egreso(ficha)
        
        if exito:
            self.agregar_mensaje(f"EGRESO: {mensaje}")
            self.mostrar_detalle_egreso(detalle)
            self.limpiar_campos()
            self.actualizar_estado()
        else:
            self.agregar_mensaje(f"ERROR EGRESO: {mensaje}")
            messagebox.showerror("Error", mensaje)
        
        self.entry_ficha.focus_set()
    
    def mostrar_detalle_egreso(self, detalle):
        ventana = tk.Toplevel(self.root)
        ventana.title("Detalle de Egreso")
        ventana.geometry("500x350")
        ventana.transient(self.root)
        ventana.grab_set()
        
        tk.Label(ventana, text="EGRESO PROCESADO", font=("Segoe UI", 20, "bold")).pack(pady=20)
        
        tk.Label(ventana, text=f"Ficha: {detalle['ficha']}", font=("Segoe UI", 18, "bold")).pack(pady=5)
        tk.Label(ventana, text=f"Tiempo: {detalle['tiempo_str']}", font=("Segoe UI", 14)).pack(pady=5)
        
        if detalle['es_abonado']:
            tk.Label(ventana, text="ABONADO - SIN COSTO", font=("Segoe UI", 20, "bold"), fg='green').pack(pady=15)
        else:
            tk.Label(ventana, text=f"MONTO: ${detalle['monto']:.2f}", font=("Segoe UI", 24, "bold"), fg='red').pack(pady=15)
            tk.Label(ventana, text=f"Tarifa: {detalle['motivo']}", font=("Segoe UI", 14)).pack(pady=5)
        
        if detalle.get('persona'):
            tk.Label(ventana, text=f"Cliente: {detalle['persona']}", font=("Segoe UI", 14)).pack(pady=5)
        
        tk.Button(ventana, text="CERRAR", command=ventana.destroy, 
                 font=("Arial", 16, "bold"), width=15).pack(pady=20)
        
        # Auto cerrar en 10 segundos
        ventana.after(10000, ventana.destroy)
    
    def validar_dni(self, event=None):
        dni = self.dni_var.get().strip()
        if not dni:
            messagebox.showwarning("Validación", "Debe ingresar un DNI")
            return
        
        try:
            es_valido, mensaje, abono, persona = self.ingreso_service.validar_dni(dni)
            
            info = f"DNI: {dni}\n\n"
            
            if persona:
                info += f"Persona: {persona.nombre} {persona.apellido}\n"
                if persona.telefono:
                    info += f"Teléfono: {persona.telefono}\n"
                if persona.email:
                    info += f"Email: {persona.email}\n"
            else:
                info += "Persona: NO REGISTRADA\n"
            
            if abono:
                estado = abono.estado()
                info += f"\nAbono: {estado.value.upper()}\n"
                info += f"Válido desde: {abono.fecha_inicio}\n"
                info += f"Válido hasta: {abono.fecha_fin}\n"
                info += f"Precio: ${abono.precio:.2f}\n"
                
                if estado.value != 'vigente':
                    info += f"\n⚠ ABONO {estado.value.upper()}"
                    if estado.value == 'vencido':
                        info += "\n❌ NECESITA RENOVACIÓN"
            else:
                info += "\nAbono: SIN ABONO VIGENTE\n"
                info += "❌ NECESITA CREAR ABONO"
            
            # Ofrecer gestión de abonos si es necesario
            if not es_valido or (abono and abono.estado().value != 'vigente'):
                info += "\n\n¿Desea gestionar el abono?"
                respuesta = messagebox.askyesno("Validación DNI", info)
                if respuesta:
                    self.gestionar_abonos()
            else:
                messagebox.showinfo("Validación DNI", info)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al validar DNI: {e}")
    
    def gestionar_abonos(self, event=None):
        """Abrir ventana de gestión de abonos"""
        dni_inicial = self.dni_var.get().strip()
        
        try:
            resultado = mostrar_gestion_abonos(self.root, self.paths, dni_inicial)
            
            if resultado:
                # Si se creó un abono, actualizar la interfaz
                self.agregar_mensaje(f"✅ {resultado['tipo']}: {resultado['persona'].nombre} {resultado['persona'].apellido}")
                
                # Si el DNI actual coincide, actualizar el estado
                if dni_inicial == resultado['persona'].dni:
                    self.on_dni_change(None)
                
                # Mostrar confirmación
                mensaje = f"✅ {resultado['tipo']} EXITOSO\n\n"
                mensaje += f"Cliente: {resultado['persona'].nombre} {resultado['persona'].apellido}\n"
                mensaje += f"DNI: {resultado['persona'].dni}\n"
                mensaje += f"Período: {resultado['abono'].fecha_inicio} a {resultado['abono'].fecha_fin}\n"
                mensaje += f"Precio: ${resultado['abono'].precio:.2f}"
                
                messagebox.showinfo("Gestión de Abonos", mensaje)
        
        except Exception as e:
            messagebox.showerror("Error", f"Error en gestión de abonos: {e}")
    
    def limpiar_campos(self, event=None):
        self.ficha_var.set("")
        self.dni_var.set("")
        self.entry_ficha.config(bg='white')
        self.lbl_estado_ficha.config(text="")
        self.lbl_estado_dni.config(text="Sin DNI", fg='black')
        self.entry_ficha.focus_set()
    
    def buscar_persona(self):
        """Buscar persona por DNI y mostrar información"""
        dni = self.dni_var.get().strip()
        if not dni:
            messagebox.showwarning("Búsqueda", "Ingrese un DNI para buscar")
            self.entry_dni.focus_set()
            return
            
        persona = self.ingreso_service.personas_repo.buscar_por_dni(dni)
        if persona:
            # Verificar abono
            abono = self.ingreso_service.abonos_repo.obtener_abono_por_dni(dni)
            
            info = f"✓ PERSONA ENCONTRADA\n\n"
            info += f"Nombre: {persona.nombre} {persona.apellido}\n"
            info += f"DNI: {persona.dni}\n"
            
            if persona.telefono:
                info += f"Teléfono: {persona.telefono}\n"
            if persona.email:
                info += f"Email: {persona.email}\n"
            
            if abono:
                estado = abono.estado()
                info += f"\nEstado del abono: {estado.value.upper()}\n"
                info += f"Válido desde: {abono.fecha_inicio}\n"
                info += f"Válido hasta: {abono.fecha_fin}\n"
                
                if estado.value == 'vigente':
                    info += "\n✓ ABONO VIGENTE"
                elif estado.value == 'por_vencer':
                    info += "\n⚠ ABONO POR VENCER"
                else:
                    info += "\n❌ ABONO VENCIDO"
            else:
                info += "\n❌ NO TIENE ABONO"
                
            messagebox.showinfo("Información del Cliente", info)
            self.on_dni_change(None)
        else:
            if messagebox.askyesno("Búsqueda", "Persona no encontrada. ¿Desea registrarla?"):
                self.gestionar_abonos()
            else:
                messagebox.showinfo("Búsqueda", "Puede continuar como cliente sin abono")
                
    def actualizar_estado(self):
        try:
            estado = self.ingreso_service.obtener_estado_estacionamiento()
            
            # Actualizar contador
            self.lbl_contador.config(text=f"Ocupadas: {estado['ocupadas']}/{estado['capacidad']}")
            
            # Actualizar barra de ocupación
            self.actualizar_barra(estado['ocupadas'], estado['capacidad'])
            
            # Actualizar listas
            self.lista_ocupadas.delete(0, tk.END)
            for ficha in estado['fichas_ocupadas']:
                self.lista_ocupadas.insert(tk.END, f"Ficha {ficha}")
            
            self.lista_libres.delete(0, tk.END)
            # Mostrar solo primeras 50 fichas libres
            libres_mostrar = estado['fichas_libres'][:50]
            for ficha in libres_mostrar:
                self.lista_libres.insert(tk.END, f"Ficha {ficha}")
            
            if len(estado['fichas_libres']) > 50:
                self.lista_libres.insert(tk.END, f"... y {len(estado['fichas_libres']) - 50} más")
        
        except Exception as e:
            self.agregar_mensaje(f"Error al actualizar estado: {e}")
        
        # Actualizar cada 5 segundos
        self.root.after(5000, self.actualizar_estado)


def main():
    root = tk.Tk()
    app = VentanaOperacion(root)
    root.mainloop()


if __name__ == "__main__":
    main()
