import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, datetime, timedelta
import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from domain.models import Persona, Abono
from domain.enums import MedioPago
from domain.infra.paths import SedePaths
from domain.infra.personas_repo import PersonasRepo
from domain.infra.abonos_repo import AbonosRepo


class VentanaGestionAbonos:
    def __init__(self, parent, paths: SedePaths, dni_inicial: str = ""):
        self.parent = parent
        self.paths = paths
        self.personas_repo = PersonasRepo(paths)
        self.abonos_repo = AbonosRepo(paths)
        self.dni_inicial = dni_inicial
        self.resultado = None
        
        self.crear_ventana()
        
        if dni_inicial:
            self.dni_var.set(dni_inicial)
            self.buscar_persona()
    
    def crear_ventana(self):
        self.ventana = tk.Toplevel(self.parent)
        self.ventana.title("Gestión de Abonos")
        self.ventana.geometry("600x700")
        self.ventana.transient(self.parent)
        self.ventana.grab_set()
        self.ventana.configure(bg='white')
        
        # Variables
        self.dni_var = tk.StringVar()
        self.nombre_var = tk.StringVar()
        self.apellido_var = tk.StringVar()
        self.telefono_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.precio_var = tk.StringVar(value="15000")
        self.meses_var = tk.StringVar(value="1")
        
        main_frame = tk.Frame(self.ventana, bg='white', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        titulo = tk.Label(main_frame, text="GESTIÓN DE ABONOS",
                         font=("Segoe UI", 16, "bold"), bg='white')
        titulo.pack(pady=(0, 20))
        
        # Frame de búsqueda
        self.crear_frame_busqueda(main_frame)
        
        # Frame de datos personales
        self.crear_frame_persona(main_frame)
        
        # Frame de abono
        self.crear_frame_abono(main_frame)
        
        # Frame de botones
        self.crear_frame_botones(main_frame)
        
        # Estado inicial
        self.actualizar_estado()
    
    def crear_frame_busqueda(self, parent):
        busqueda_frame = tk.LabelFrame(parent, text="BUSCAR PERSONA", font=("Segoe UI", 12, "bold"))
        busqueda_frame.pack(fill=tk.X, pady=(0, 15))
        
        inner_frame = tk.Frame(busqueda_frame)
        inner_frame.pack(pady=10)
        
        tk.Label(inner_frame, text="DNI:", font=("Segoe UI", 12, "bold")).grid(row=0, column=0, padx=5)
        
        self.entry_dni = tk.Entry(inner_frame, textvariable=self.dni_var, 
                                 font=("Segoe UI", 12), width=15)
        self.entry_dni.grid(row=0, column=1, padx=10)
        self.entry_dni.bind('<KeyRelease>', self.on_dni_change)
        
        # Vincular cambios en el StringVar directamente
        self.dni_var.trace_add("write", lambda *args: self.actualizar_estado())
        self.nombre_var.trace_add("write", lambda *args: self.actualizar_estado())
        self.apellido_var.trace_add("write", lambda *args: self.actualizar_estado())
        
        self.btn_buscar = tk.Button(inner_frame, text="BUSCAR", 
                                   command=self.buscar_persona, bg='blue', fg='white')
        self.btn_buscar.grid(row=0, column=2, padx=10)
        
        # Estado de búsqueda
        self.lbl_estado_busqueda = tk.Label(inner_frame, text="Ingrese DNI para buscar", 
                                           font=("Segoe UI", 10))
        self.lbl_estado_busqueda.grid(row=1, column=0, columnspan=3, pady=5)
    
    def crear_frame_persona(self, parent):
        self.persona_frame = tk.LabelFrame(parent, text="DATOS PERSONALES", font=("Segoe UI", 12, "bold"))
        self.persona_frame.pack(fill=tk.X, pady=(0, 15))
        
        inner_frame = tk.Frame(self.persona_frame)
        inner_frame.pack(pady=10)
        
        # Nombre
        tk.Label(inner_frame, text="Nombre:*", font=("Segoe UI", 11)).grid(row=0, column=0, sticky=tk.W, padx=5)
        self.entry_nombre = tk.Entry(inner_frame, textvariable=self.nombre_var, 
                                    font=("Arial", 11), width=25)
        self.entry_nombre.grid(row=0, column=1, padx=10, pady=2)
        self.entry_nombre.bind('<KeyRelease>', lambda e: self.actualizar_estado())
        
        # Apellido
        tk.Label(inner_frame, text="Apellido:*", font=("Segoe UI", 11)).grid(row=1, column=0, sticky=tk.W, padx=5)
        self.entry_apellido = tk.Entry(inner_frame, textvariable=self.apellido_var, 
                                      font=("Arial", 11), width=25)
        self.entry_apellido.grid(row=1, column=1, padx=10, pady=2)
        self.entry_apellido.bind('<KeyRelease>', lambda e: self.actualizar_estado())
        
        # Teléfono
        tk.Label(inner_frame, text="Teléfono:", font=("Segoe UI", 11)).grid(row=2, column=0, sticky=tk.W, padx=5)
        self.entry_telefono = tk.Entry(inner_frame, textvariable=self.telefono_var, 
                                      font=("Arial", 11), width=25)
        self.entry_telefono.grid(row=2, column=1, padx=10, pady=2)
        
        # Email
        tk.Label(inner_frame, text="Email:", font=("Segoe UI", 11)).grid(row=3, column=0, sticky=tk.W, padx=5)
        self.entry_email = tk.Entry(inner_frame, textvariable=self.email_var, 
                                   font=("Arial", 11), width=25)
        self.entry_email.grid(row=3, column=1, padx=10, pady=2)
        
        # Estado de la persona
        self.lbl_estado_persona = tk.Label(inner_frame, text="", font=("Segoe UI", 10, "bold"))
        self.lbl_estado_persona.grid(row=4, column=0, columnspan=2, pady=10)
    
    def crear_frame_abono(self, parent):
        self.abono_frame = tk.LabelFrame(parent, text="CREAR/RENOVAR ABONO", font=("Segoe UI", 12, "bold"))
        self.abono_frame.pack(fill=tk.X, pady=(0, 15))
        
        inner_frame = tk.Frame(self.abono_frame)
        inner_frame.pack(pady=10)
        
        # Duración en meses
        tk.Label(inner_frame, text="Duración (meses):", font=("Segoe UI", 11)).grid(row=0, column=0, sticky=tk.W, padx=5)
        self.combo_meses = ttk.Combobox(inner_frame, textvariable=self.meses_var, 
                                       values=["1", "2", "3", "6", "12"], width=10)
        self.combo_meses.grid(row=0, column=1, padx=10, pady=2)
        self.combo_meses.bind('<<ComboboxSelected>>', self.calcular_fechas)
        
        # Precio
        tk.Label(inner_frame, text="Precio:", font=("Segoe UI", 11)).grid(row=1, column=0, sticky=tk.W, padx=5)
        self.entry_precio = tk.Entry(inner_frame, textvariable=self.precio_var, 
                                    font=("Segoe UI", 11), width=15)
        self.entry_precio.grid(row=1, column=1, padx=10, pady=2)
        self.entry_precio.bind('<KeyRelease>', self.calcular_fechas)
        
        # Fechas calculadas
        self.lbl_fechas = tk.Label(inner_frame, text="", font=("Segoe UI", 10))
        self.lbl_fechas.grid(row=2, column=0, columnspan=2, pady=10)
        
        # Estado del abono actual
        self.lbl_estado_abono = tk.Label(inner_frame, text="", font=("Segoe UI", 10, "bold"))
        self.lbl_estado_abono.grid(row=3, column=0, columnspan=2, pady=5)
    
    def crear_frame_botones(self, parent):
        botones_frame = tk.Frame(parent, bg='white')
        botones_frame.pack(fill=tk.X, pady=20)
        
        # Frame verde para el botón Guardar
        frame_guardar = tk.Frame(botones_frame, bg='#2ecc71', highlightthickness=2, highlightcolor='#27ae60')
        frame_guardar.pack(side=tk.LEFT, padx=10, pady=5)
        
        self.btn_guardar = tk.Button(frame_guardar, text="💾 GUARDAR", 
                                    font=("Segoe UI", 12, "bold"), bg='#27ae60', fg='white',
                                    command=self.guardar_y_crear_abono, width=20,
                                    relief=tk.FLAT, bd=0, activebackground='#229954', activeforeground='white',
                                    padx=10, pady=8)
        self.btn_guardar.pack(padx=3, pady=3)
        
        self.btn_cancelar = tk.Button(botones_frame, text="❌ CANCELAR", 
                                     font=("Segoe UI", 12, "bold"), bg='#95a5a6', fg='white',
                                     command=self.cancelar, width=15,
                                     relief=tk.RAISED, bd=2, activebackground='#7f8c8d',
                                     padx=10, pady=8)
        self.btn_cancelar.pack(side=tk.RIGHT, padx=10)
    
    def on_dni_change(self, event):
        dni = self.dni_var.get().strip()
        if len(dni) >= 7:  # Buscar automáticamente cuando hay suficientes dígitos
            self.buscar_persona()
        self.actualizar_estado()
    
    def buscar_persona(self):
        dni = self.dni_var.get().strip()
        if not dni:
            self.lbl_estado_busqueda.config(text="Ingrese DNI para buscar", fg='black')
            return
        
        # Buscar persona
        persona = self.personas_repo.buscar_por_dni(dni)
        
        if persona:
            # Cargar datos de la persona
            self.nombre_var.set(persona.nombre)
            self.apellido_var.set(persona.apellido)
            self.telefono_var.set(persona.telefono or "")
            self.email_var.set(persona.email or "")
            
            self.lbl_estado_busqueda.config(text="✓ Persona encontrada", fg='green')
            self.lbl_estado_persona.config(text="PERSONA REGISTRADA", fg='green')
            
            # Buscar abono vigente
            abono = self.abonos_repo.abono_vigente_por_dni(dni)
            if abono:
                estado = abono.estado()
                self.lbl_estado_abono.config(
                    text=f"Abono actual: {estado.value.upper()} (vence: {abono.fecha_fin})", 
                    fg='orange' if estado.value == 'por_vencer' else 'red' if estado.value == 'vencido' else 'green'
                )
            else:
                self.lbl_estado_abono.config(text="Sin abono vigente", fg='red')
        else:
            # Persona no existe - limpiar campos
            self.nombre_var.set("")
            self.apellido_var.set("")
            self.telefono_var.set("")
            self.email_var.set("")
            
            self.lbl_estado_busqueda.config(text="⚠ Persona no registrada", fg='orange')
            self.lbl_estado_persona.config(text="NUEVA PERSONA", fg='blue')
            self.lbl_estado_abono.config(text="Sin abono", fg='red')
        
        self.calcular_fechas()
        self.actualizar_estado()
    
    def calcular_fechas(self, event=None):
        try:
            meses = int(self.meses_var.get())
            precio_total = float(self.precio_var.get()) * meses
            
            hoy = date.today()
            fecha_fin = hoy + timedelta(days=meses * 30)  # Aproximado
            
            self.lbl_fechas.config(
                text=f"Período: {hoy} a {fecha_fin}\nPrecio total: ${precio_total:,.2f}"
            )
        except:
            self.lbl_fechas.config(text="")
    
    def actualizar_estado(self):
        dni = self.dni_var.get().strip()
        nombre = self.nombre_var.get().strip()
        apellido = self.apellido_var.get().strip()
        
        # Habilitar/deshabilitar campos y botones
        puede_guardar = dni and nombre and apellido
        self.btn_guardar.config(state='normal' if puede_guardar else 'disabled')
        
        # Verificar si los datos cambiaron para mostrar un mensaje informativo
        if puede_guardar:
            print(f"Botón guardar habilitado. DNI: {dni}, Nombre: {nombre}, Apellido: {apellido}")
        else:
            print(f"Botón guardar deshabilitado. Faltan datos obligatorios: DNI: {'✓' if dni else '❌'}, Nombre: {'✓' if nombre else '❌'}, Apellido: {'✓' if apellido else '❌'}")
    
    def guardar_y_crear_abono(self):
        try:
            print("Iniciando proceso de guardar abono")
            
            # Validaciones
            dni = self.dni_var.get().strip()
            nombre = self.nombre_var.get().strip()
            apellido = self.apellido_var.get().strip()
            
            print(f"Valores capturados - DNI: {dni}, Nombre: {nombre}, Apellido: {apellido}")
            
            if not dni or not nombre or not apellido:
                messagebox.showerror("Error", "DNI, nombre y apellido son obligatorios")
                print(f"Falta información - DNI: {'✓' if dni else '❌'}, Nombre: {'✓' if nombre else '❌'}, Apellido: {'✓' if apellido else '❌'}")
                return
            
            if len(dni) < 7:
                messagebox.showerror("Error", "DNI debe tener al menos 7 dígitos")
                print(f"DNI inválido: {dni} (debe tener al menos 7 dígitos)")
                return
            
            try:
                meses = int(self.meses_var.get())
                precio_mensual = float(self.precio_var.get())
                print(f"Duración: {meses} meses, Precio mensual: ${precio_mensual}")
            except ValueError as e:
                messagebox.showerror("Error", "Duración y precio deben ser números válidos")
                print(f"Error en duración o precio: {e}")
                return
            
            # Crear o actualizar persona
            persona = Persona(
                dni=dni,
                nombre=nombre,
                apellido=apellido,
                telefono=self.telefono_var.get().strip() or None,
                email=self.email_var.get().strip() or None
            )
            
            print(f"Objeto Persona creado: {persona.__dict__}")
            print(f"Ruta de archivo personas: {self.personas_repo.archivo}")
            
            # Verificar si la persona ya existe
            persona_existente = self.personas_repo.buscar_por_dni(dni)
            if persona_existente:
                print(f"Actualizando persona existente: {persona_existente.__dict__}")
                resultado_persona = self.personas_repo.actualizar(persona)
                print(f"Resultado actualización: {resultado_persona}")
            else:
                print(f"Agregando nueva persona")
                resultado_persona = self.personas_repo.agregar(persona)
                print(f"Resultado agregar: {resultado_persona}")
            
            # Crear abono
            hoy = date.today()
            fecha_fin = hoy + timedelta(days=meses * 30)
            precio_total = precio_mensual * meses
            
            print(f"Fecha actual: {hoy}, Fecha fin calculada: {fecha_fin}")
            print(f"Precio total calculado: ${precio_total}")
            
            # Verificar si hay abono vigente para determinar fecha de inicio
            abono_actual = self.abonos_repo.abono_vigente_por_dni(dni)
            if abono_actual and abono_actual.estado().value in ['vigente', 'por_vencer']:
                # Si tiene abono vigente, el nuevo comienza al día siguiente del fin del actual
                fecha_inicio = abono_actual.fecha_fin + timedelta(days=1)
                fecha_fin = fecha_inicio + timedelta(days=meses * 30)
                mensaje_tipo = "RENOVACIÓN"
                print(f"Renovando abono existente. ID: {abono_actual.id}")
                print(f"Nueva fecha inicio: {fecha_inicio}, Nueva fecha fin: {fecha_fin}")
            else:
                # Si no tiene abono vigente, comienza hoy
                fecha_inicio = hoy
                mensaje_tipo = "NUEVO ABONO"
                print("Creando nuevo abono (no hay vigente)")
            
            # Generar ID único para el abono
            id_abono = self.abonos_repo.generar_id_abono()
            print(f"ID de abono generado: {id_abono}")
            
            nuevo_abono = Abono(
                id=id_abono,
                dni_persona=dni,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                precio=precio_total
            )
            
            print(f"Objeto Abono creado: {nuevo_abono.__dict__}")
            print(f"Ruta de archivo abonos: {self.abonos_repo.archivo_abonos}")
            
            # Guardar abono
            try:
                print("Intentando guardar abono...")
                
                # Verificar que el directorio existe
                directorio = os.path.dirname(self.abonos_repo.archivo_abonos)
                print(f"Directorio de abonos: {directorio}")
                print(f"¿Directorio existe? {os.path.exists(directorio)}")
                
                if not os.path.exists(directorio):
                    print(f"Creando directorio: {directorio}")
                    os.makedirs(directorio, exist_ok=True)
                
                # Verificar permisos
                if os.path.exists(directorio):
                    print(f"Permiso de escritura en directorio: {os.access(directorio, os.W_OK)}")
                    if os.path.exists(self.abonos_repo.archivo_abonos):
                        print(f"Permiso de escritura en archivo: {os.access(self.abonos_repo.archivo_abonos, os.W_OK)}")
                
                resultado = self.abonos_repo.agregar_abono(nuevo_abono)
                print(f"Resultado de agregar_abono: {resultado}")
                
                mensaje = f"✅ {mensaje_tipo} CREADO EXITOSAMENTE\n\n"
                mensaje += f"Persona: {nombre} {apellido}\n"
                mensaje += f"DNI: {dni}\n"
                mensaje += f"Período: {fecha_inicio} a {fecha_fin}\n"
                mensaje += f"Duración: {meses} mes(es)\n"
                mensaje += f"Precio total: ${precio_total:,.2f}\n"
                mensaje += f"ID Abono: {nuevo_abono.id}"
                
                print("Mostrando mensaje de éxito")
                messagebox.showinfo("Éxito", mensaje)
                
                # Guardar resultado para el retorno
                self.resultado = {
                    'persona': persona,
                    'abono': nuevo_abono,
                    'tipo': mensaje_tipo
                }
                
                print("Cerrando ventana")
                self.ventana.destroy()
            except Exception as e:
                import traceback
                traceback.print_exc()
                messagebox.showerror("Error", f"Error al guardar abono: {str(e)}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {e}")
    
    def cancelar(self):
        self.ventana.destroy()


def mostrar_gestion_abonos(parent, paths: SedePaths, dni_inicial: str = ""):
    """
    Función para mostrar la ventana de gestión de abonos
    Retorna los datos del abono creado o None si se canceló
    """
    try:
        ventana = VentanaGestionAbonos(parent, paths, dni_inicial)
        parent.wait_window(ventana.ventana)
        return ventana.resultado
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error al mostrar ventana de gestión de abonos: {e}")
        return None


# Función de prueba
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Ocultar ventana principal
    
    # Usar SedePaths con detección automática
    paths = SedePaths()
    print(f"Usando directorio de datos: {paths.root}")
    
    resultado = mostrar_gestion_abonos(root, paths)
    if resultado:
        print("Abono creado:", resultado)
    else:
        print("Operación cancelada")
    
    root.destroy()
