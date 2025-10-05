import tkinter as tk
from tkinter import ttk, messagebox
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
        self.root.geometry("1000x700")
        self.root.configure(bg='white')
        
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
        # Frame principal
        main_frame = tk.Frame(self.root, bg='white', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        titulo = tk.Label(main_frame, text="SISTEMA DE ESTACIONAMIENTO", 
                         font=("Arial", 18, "bold"), bg='white')
        titulo.pack(pady=(0, 20))
        
        # Frame de operación
        op_frame = tk.LabelFrame(main_frame, text="OPERACIÓN", font=("Arial", 12, "bold"))
        op_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Campos de entrada
        campos_frame = tk.Frame(op_frame)
        campos_frame.pack(pady=15)
        
        # Nro de Ficha
        tk.Label(campos_frame, text="Nro. Ficha:", font=("Arial", 14, "bold")).grid(row=0, column=0, padx=5)
        self.entry_ficha = tk.Entry(campos_frame, textvariable=self.ficha_var, 
                                   font=("Arial", 18, "bold"), width=12, justify='center')
        self.entry_ficha.grid(row=0, column=1, padx=10)
        
        # Estado Ficha
        self.lbl_estado_ficha = tk.Label(campos_frame, text="", font=("Arial", 12))
        self.lbl_estado_ficha.grid(row=0, column=2, padx=5)
        
        # DNI
        tk.Label(campos_frame, text="DNI:", font=("Arial", 14, "bold")).grid(row=0, column=3, padx=5)
        self.entry_dni = tk.Entry(campos_frame, textvariable=self.dni_var, 
                                 font=("Arial", 16, "bold"), width=15, justify='center')
        self.entry_dni.grid(row=0, column=4, padx=10)
        
        # Estado DNI
        self.lbl_estado_dni = tk.Label(campos_frame, text="Sin DNI", font=("Arial", 12, "bold"))
        self.lbl_estado_dni.grid(row=0, column=5, padx=10)
        
        # Botón buscar DNI
        self.btn_buscar = tk.Button(campos_frame, text="Buscar (Alt+B)", 
                                  font=("Arial", 12, "bold"), bg='blue', fg='white',
                                  command=self.buscar_persona, width=12)
        self.btn_buscar.grid(row=0, column=6, padx=10)
        
        # Botones
        botones_frame = tk.Frame(op_frame)
        botones_frame.pack(pady=15)
        
        self.btn_ingreso = tk.Button(botones_frame, text="INGRESO (Enter)", 
                                    font=("Arial", 11, "bold"), bg='green', fg='white',
                                    command=self.procesar_ingreso, width=15)
        self.btn_ingreso.pack(side=tk.LEFT, padx=5)
        
        self.btn_salida = tk.Button(botones_frame, text="SALIDA (F2)", 
                                   font=("Arial", 11, "bold"), bg='red', fg='white',
                                   command=self.procesar_salida, width=15)
        self.btn_salida.pack(side=tk.LEFT, padx=5)
        
        self.btn_validar = tk.Button(botones_frame, text="VALIDAR DNI (Alt+A)", 
                                    font=("Arial", 11, "bold"), bg='blue', fg='white',
                                    command=self.validar_dni, width=20)
        self.btn_validar.pack(side=tk.LEFT, padx=5)
        
        self.btn_gestionar_abono = tk.Button(botones_frame, text="GESTIÓN ABONOS (F3)", 
                                            font=("Arial", 11, "bold"), bg='purple', fg='white',
                                            command=self.gestionar_abonos, width=20)
        self.btn_gestionar_abono.pack(side=tk.LEFT, padx=5)
        
        self.btn_limpiar = tk.Button(botones_frame, text="LIMPIAR (Esc)", 
                                    font=("Arial", 11, "bold"), bg='gray', fg='white',
                                    command=self.limpiar_campos, width=15)
        self.btn_limpiar.pack(side=tk.LEFT, padx=5)
        
        # Frame de estado
        estado_frame = tk.LabelFrame(main_frame, text="ESTADO", font=("Arial", 12, "bold"))
        estado_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.lbl_contador = tk.Label(estado_frame, text="Ocupadas: 0/0", 
                                    font=("Arial", 16, "bold"))
        self.lbl_contador.pack(pady=10)
        
        # Frame de listas
        listas_frame = tk.Frame(main_frame)
        listas_frame.pack(fill=tk.BOTH, expand=True)
        
        # Ocupadas
        ocupadas_frame = tk.LabelFrame(listas_frame, text="FICHAS OCUPADAS", font=("Arial", 11, "bold"))
        ocupadas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.lista_ocupadas = tk.Listbox(ocupadas_frame, font=("Arial", 13))
        scroll_ocupadas = tk.Scrollbar(ocupadas_frame)
        self.lista_ocupadas.config(yscrollcommand=scroll_ocupadas.set)
        scroll_ocupadas.config(command=self.lista_ocupadas.yview)
        self.lista_ocupadas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_ocupadas.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Libres
        libres_frame = tk.LabelFrame(listas_frame, text="FICHAS LIBRES", font=("Arial", 11, "bold"))
        libres_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 5))
        
        self.lista_libres = tk.Listbox(libres_frame, font=("Arial", 13))
        scroll_libres = tk.Scrollbar(libres_frame)
        self.lista_libres.config(yscrollcommand=scroll_libres.set)
        scroll_libres.config(command=self.lista_libres.yview)
        self.lista_libres.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_libres.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Mensajes
        mensajes_frame = tk.LabelFrame(listas_frame, text="MENSAJES", font=("Arial", 11, "bold"))
        mensajes_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        self.text_mensajes = tk.Text(mensajes_frame, font=("Arial", 12), wrap=tk.WORD)
        scroll_mensajes = tk.Scrollbar(mensajes_frame)
        self.text_mensajes.config(yscrollcommand=scroll_mensajes.set)
        scroll_mensajes.config(command=self.text_mensajes.yview)
        self.text_mensajes.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_mensajes.pack(side=tk.RIGHT, fill=tk.Y)
    
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
                self.lbl_estado_ficha.config(text=f"⚠️ Fuera de rango (1-{config.capacidad})", fg='red')
                return
            
            # Verificar estado actual de la ficha (ocupada/disponible)
            movimiento = self.egreso_service.movimientos_repo.obtener_abierto_por_ficha(ficha)
            if movimiento:
                # Ficha ocupada
                self.entry_ficha.config(bg='white')
                self.lbl_estado_ficha.config(text="✅ Ocupada", fg='green')
                
                # Mostrar detalles del ingreso
                try:
                    hora_entrada = movimiento.get("hora_entrada", "")
                    dni = movimiento.get("dni", "")
                    if dni:
                        persona = self.ingreso_service.personas_repo.buscar_por_dni(dni)
                        nombre_persona = f"{persona.nombre} {persona.apellido}" if persona else "Desconocido"
                        self.lbl_estado_ficha.config(text=f"✅ Ocupada - {nombre_persona}", fg='green')
                except:
                    pass
            else:
                # Ficha libre
                self.entry_ficha.config(bg='white')
                self.lbl_estado_ficha.config(text="⚠️ Disponible", fg='orange')
        else:
            self.entry_ficha.config(bg='#ffcccc')
            self.lbl_estado_ficha.config(text="⚠️ Número inválido", fg='red')
    
    def on_dni_change(self, event):
        dni = self.dni_var.get().strip()
        if not dni:
            self.lbl_estado_dni.config(text="Sin DNI", fg='black')
            return
        
        try:
            es_valido, mensaje, abono, persona = self.ingreso_service.validar_dni(dni)
            if not es_valido:
                self.lbl_estado_dni.config(text="❌ DNI no registrado - F3 para gestionar", fg='red')
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
        
        tk.Label(ventana, text="EGRESO PROCESADO", font=("Arial", 20, "bold")).pack(pady=20)
        
        tk.Label(ventana, text=f"Ficha: {detalle['ficha']}", font=("Arial", 18, "bold")).pack(pady=5)
        tk.Label(ventana, text=f"Tiempo: {detalle['tiempo_str']}", font=("Arial", 14)).pack(pady=5)
        
        if detalle['es_abonado']:
            tk.Label(ventana, text="ABONADO - SIN COSTO", font=("Arial", 20, "bold"), fg='green').pack(pady=15)
        else:
            tk.Label(ventana, text=f"MONTO: ${detalle['monto']:.2f}", font=("Arial", 24, "bold"), fg='red').pack(pady=15)
            tk.Label(ventana, text=f"Tarifa: {detalle['motivo']}", font=("Arial", 14)).pack(pady=5)
        
        if detalle.get('persona'):
            tk.Label(ventana, text=f"Cliente: {detalle['persona']}", font=("Arial", 14)).pack(pady=5)
        
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
