import tkinter as tk
from tkinter import ttk, messagebox, font
from datetime import datetime, time
import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from domain.models import Config, Turno
from domain.enums import EstadoAbono
from domain.infra.paths import SedePaths
from domain.infra.services.ingreso_service_nuevo import IngresoServiceNuevo
from domain.infra.services.egreso_service_nuevo import EgresoServiceNuevo


class VentanaPrincipalMejorada:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Gestión de Estacionamiento - Operación")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # Configurar paths
        self.paths = SedePaths(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data'))
        
        # Servicios
        self.ingreso_service = IngresoServiceNuevo(self.paths)
        self.egreso_service = EgresoServiceNuevo(self.paths)
        
        # Variables de UI
        self.ficha_var = tk.StringVar()
        self.dni_var = tk.StringVar()
        
        # Configurar interfaz
        self.crear_interfaz()
        self.configurar_atajos()
        self.actualizar_datos()
        
        # Foco inicial en campo ficha
        self.entry_ficha.focus_set()
    
    def crear_interfaz(self):
        """Crea toda la interfaz de usuario"""
        # Frame principal
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título
        titulo = tk.Label(main_frame, text="SISTEMA DE ESTACIONAMIENTO", 
                         font=("Arial", 20, "bold"), bg='#f0f0f0', fg='#2c3e50')
        titulo.pack(pady=(0, 20))
        
        # Frame superior - Operación
        self.crear_frame_operacion(main_frame)
        
        # Frame medio - Estado y validación
        self.crear_frame_estado(main_frame)
        
        # Frame inferior - Listas y mensajes
        self.crear_frame_listas(main_frame)
    
    def crear_frame_operacion(self, parent):
        """Frame principal de operación"""
        op_frame = tk.LabelFrame(parent, text="OPERACIÓN", font=("Arial", 12, "bold"),
                                bg='#f0f0f0', fg='#2c3e50', padx=10, pady=10)
        op_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Frame para campos de entrada
        entrada_frame = tk.Frame(op_frame, bg='#f0f0f0')
        entrada_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Campo Nro de Ficha (SIEMPRE CON FOCO)
        tk.Label(entrada_frame, text="Nro. Ficha:", font=("Arial", 14, "bold"),
                bg='#f0f0f0', fg='#2c3e50').grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        self.entry_ficha = tk.Entry(entrada_frame, textvariable=self.ficha_var, 
                                   font=("Arial", 16, "bold"), width=10, justify='center')
        self.entry_ficha.grid(row=0, column=1, padx=(0, 20))
        self.entry_ficha.bind('<Return>', self.procesar_ingreso)
        self.entry_ficha.bind('<KeyRelease>', self.on_ficha_change)
        
        # Campo DNI
        tk.Label(entrada_frame, text="DNI:", font=("Arial", 14),
                bg='#f0f0f0', fg='#2c3e50').grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        
        self.entry_dni = tk.Entry(entrada_frame, textvariable=self.dni_var, 
                                 font=("Arial", 14), width=15)
        self.entry_dni.grid(row=0, column=3, padx=(0, 20))
        self.entry_dni.bind('<KeyRelease>', self.on_dni_change)
        
        # Semáforo de abonado
        self.semaforo_frame = tk.Frame(entrada_frame, bg='#f0f0f0')
        self.semaforo_frame.grid(row=0, column=4, padx=(0, 20))
        
        self.semaforo_canvas = tk.Canvas(self.semaforo_frame, width=30, height=30, 
                                        bg='#f0f0f0', highlightthickness=0)
        self.semaforo_canvas.pack(side=tk.LEFT)
        
        self.lbl_estado_abono = tk.Label(self.semaforo_frame, text="Sin DNI", 
                                        font=("Arial", 10), bg='#f0f0f0')
        self.lbl_estado_abono.pack(side=tk.LEFT, padx=(5, 0))
        
        # Botones principales
        botones_frame = tk.Frame(op_frame, bg='#f0f0f0')
        botones_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.btn_ingreso = tk.Button(botones_frame, text="INGRESO\\n(Enter)", 
                                    font=("Arial", 12, "bold"), bg='#27ae60', fg='white',
                                    command=self.procesar_ingreso, width=12, height=2)
        self.btn_ingreso.pack(side=tk.LEFT, padx=(0, 10))
        
        self.btn_salida = tk.Button(botones_frame, text="SALIDA\\n(F2)", 
                                   font=("Arial", 12, "bold"), bg='#e74c3c', fg='white',
                                   command=self.procesar_salida, width=12, height=2)
        self.btn_salida.pack(side=tk.LEFT, padx=(0, 10))
        
        self.btn_validar_dni = tk.Button(botones_frame, text="VALIDAR DNI\\n(Alt+A)", 
                                        font=("Arial", 12, "bold"), bg='#3498db', fg='white',
                                        command=self.validar_dni, width=12, height=2)
        self.btn_validar_dni.pack(side=tk.LEFT, padx=(0, 10))
        
        self.btn_limpiar = tk.Button(botones_frame, text="LIMPIAR\\n(Esc)", 
                                    font=("Arial", 12, "bold"), bg='#95a5a6', fg='white',
                                    command=self.limpiar_campos, width=12, height=2)
        self.btn_limpiar.pack(side=tk.LEFT, padx=(0, 10))\n    \n    def crear_frame_estado(self, parent):\n        \"\"\"Frame de estado del estacionamiento\"\"\"\n        estado_frame = tk.LabelFrame(parent, text=\"ESTADO DEL ESTACIONAMIENTO\", \n                                    font=(\"Arial\", 12, \"bold\"), bg='#f0f0f0', fg='#2c3e50',\n                                    padx=10, pady=10)\n        estado_frame.pack(fill=tk.X, pady=(0, 10))\n        \n        # Contador ocupadas/capacidad\n        contador_frame = tk.Frame(estado_frame, bg='#f0f0f0')\n        contador_frame.pack(fill=tk.X, pady=(0, 10))\n        \n        self.lbl_contador = tk.Label(contador_frame, text=\"Ocupadas: 0/0\", \n                                    font=(\"Arial\", 18, \"bold\"), bg='#f0f0f0', fg='#2c3e50')\n        self.lbl_contador.pack(side=tk.LEFT)\n        \n        self.lbl_estado = tk.Label(contador_frame, text=\"DISPONIBLE\", \n                                  font=(\"Arial\", 18, \"bold\"), bg='#f0f0f0', fg='#27ae60')\n        self.lbl_estado.pack(side=tk.RIGHT)\n        \n        # Barra de progreso\n        self.progress = ttk.Progressbar(estado_frame, mode='determinate', length=400)\n        self.progress.pack(fill=tk.X, pady=(0, 10))\n    \n    def crear_frame_listas(self, parent):\n        \"\"\"Frame con listas de fichas y mensajes\"\"\"\n        listas_frame = tk.Frame(parent, bg='#f0f0f0')\n        listas_frame.pack(fill=tk.BOTH, expand=True)\n        \n        # Frame izquierdo - Fichas ocupadas\n        ocupadas_frame = tk.LabelFrame(listas_frame, text=\"FICHAS OCUPADAS\", \n                                      font=(\"Arial\", 11, \"bold\"), bg='#f0f0f0', fg='#e74c3c')\n        ocupadas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))\n        \n        self.lista_ocupadas = tk.Listbox(ocupadas_frame, font=(\"Arial\", 12), \n                                        bg='#fff5f5', fg='#e74c3c')\n        scroll_ocupadas = tk.Scrollbar(ocupadas_frame, orient=tk.VERTICAL)\n        self.lista_ocupadas.config(yscrollcommand=scroll_ocupadas.set)\n        scroll_ocupadas.config(command=self.lista_ocupadas.yview)\n        \n        self.lista_ocupadas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)\n        scroll_ocupadas.pack(side=tk.RIGHT, fill=tk.Y)\n        \n        # Frame central - Fichas libres\n        libres_frame = tk.LabelFrame(listas_frame, text=\"FICHAS LIBRES\", \n                                    font=(\"Arial\", 11, \"bold\"), bg='#f0f0f0', fg='#27ae60')\n        libres_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)\n        \n        self.lista_libres = tk.Listbox(libres_frame, font=(\"Arial\", 12), \n                                      bg='#f5fff5', fg='#27ae60')\n        scroll_libres = tk.Scrollbar(libres_frame, orient=tk.VERTICAL)\n        self.lista_libres.config(yscrollcommand=scroll_libres.set)\n        scroll_libres.config(command=self.lista_libres.yview)\n        \n        self.lista_libres.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)\n        scroll_libres.pack(side=tk.RIGHT, fill=tk.Y)\n        \n        # Frame derecho - Mensajes\n        mensajes_frame = tk.LabelFrame(listas_frame, text=\"MENSAJES\", \n                                      font=(\"Arial\", 11, \"bold\"), bg='#f0f0f0', fg='#2c3e50')\n        mensajes_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))\n        \n        self.text_mensajes = tk.Text(mensajes_frame, font=(\"Arial\", 11), \n                                    bg='#fffff0', fg='#2c3e50', wrap=tk.WORD)\n        scroll_mensajes = tk.Scrollbar(mensajes_frame, orient=tk.VERTICAL)\n        self.text_mensajes.config(yscrollcommand=scroll_mensajes.set)\n        scroll_mensajes.config(command=self.text_mensajes.yview)\n        \n        self.text_mensajes.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)\n        scroll_mensajes.pack(side=tk.RIGHT, fill=tk.Y)\n    \n    def configurar_atajos(self):\n        \"\"\"Configura atajos de teclado\"\"\"\n        self.root.bind('<Return>', self.procesar_ingreso)\n        self.root.bind('<F2>', self.procesar_salida)\n        self.root.bind('<Alt-a>', self.validar_dni)\n        self.root.bind('<Alt-A>', self.validar_dni)\n        self.root.bind('<Escape>', self.limpiar_campos)\n        \n        # Mantener foco en ficha\n        self.root.bind('<FocusIn>', lambda e: self.entry_ficha.focus_set())\n    \n    def actualizar_semaforo(self, estado: str, texto: str):\n        \"\"\"Actualiza el semáforo de estado del abonado\"\"\"\n        self.semaforo_canvas.delete(\"all\")\n        \n        colores = {\n            'verde': '#27ae60',\n            'amarillo': '#f39c12', \n            'rojo': '#e74c3c',\n            'gris': '#95a5a6'\n        }\n        \n        color = colores.get(estado, '#95a5a6')\n        self.semaforo_canvas.create_oval(5, 5, 25, 25, fill=color, outline=color)\n        self.lbl_estado_abono.config(text=texto)\n    \n    def agregar_mensaje(self, mensaje: str, tipo: str = 'info'):\n        \"\"\"Agrega mensaje al área de mensajes\"\"\"\n        timestamp = datetime.now().strftime(\"%H:%M:%S\")\n        \n        # Colores según tipo\n        colores = {\n            'exito': '#27ae60',\n            'error': '#e74c3c',\n            'warning': '#f39c12',\n            'info': '#2c3e50'\n        }\n        \n        self.text_mensajes.insert(tk.END, f\"[{timestamp}] {mensaje}\\n\\n\")\n        self.text_mensajes.see(tk.END)\n        \n        # Límite de mensajes\n        lines = self.text_mensajes.get(\"1.0\", tk.END).count('\\n')\n        if lines > 100:\n            self.text_mensajes.delete(\"1.0\", \"10.0\")\n    \n    def on_ficha_change(self, event):\n        \"\"\"Evento al cambiar número de ficha\"\"\"\n        ficha_str = self.ficha_var.get().strip()\n        if ficha_str.isdigit():\n            ficha = int(ficha_str)\n            # Validar rango\n            config = self.ingreso_service.config\n            if ficha < 1 or ficha > config.capacidad:\n                self.entry_ficha.config(bg='#ffebee')\n            else:\n                self.entry_ficha.config(bg='white')\n        else:\n            self.entry_ficha.config(bg='white' if not ficha_str else '#ffebee')\n    \n    def on_dni_change(self, event):\n        \"\"\"Evento al cambiar DNI\"\"\"\n        dni = self.dni_var.get().strip()\n        if not dni:\n            self.actualizar_semaforo('gris', 'Sin DNI')\n            return\n        \n        # Validar DNI en tiempo real\n        try:\n            es_valido, mensaje, abono, persona = self.ingreso_service.validar_dni(dni)\n            \n            if not es_valido:\n                self.actualizar_semaforo('rojo', 'DNI no registrado')\n            elif abono:\n                # Determinar estado del semáforo\n                estado_dict = abono if isinstance(abono, dict) else None\n                if estado_dict:\n                    estado = estado_dict.get('estado', 'desconocido')\n                    if estado == 'vigente':\n                        self.actualizar_semaforo('verde', 'Abono VIGENTE')\n                    elif 'venc' in estado.lower():\n                        self.actualizar_semaforo('amarillo', 'Por vencer')\n                    else:\n                        self.actualizar_semaforo('rojo', f'Abono {estado}')\n                else:\n                    self.actualizar_semaforo('verde', 'Abono vigente')\n            else:\n                self.actualizar_semaforo('gris', 'Sin abono')\n        except Exception as e:\n            self.actualizar_semaforo('rojo', 'Error validación')\n    \n    def procesar_ingreso(self, event=None):\n        \"\"\"Procesa el ingreso de un vehículo\"\"\"\n        ficha_str = self.ficha_var.get().strip()\n        if not ficha_str or not ficha_str.isdigit():\n            messagebox.showerror(\"Error\", \"Debe ingresar un número de ficha válido\")\n            self.entry_ficha.focus_set()\n            return\n        \n        ficha = int(ficha_str)\n        dni = self.dni_var.get().strip() if self.dni_var.get().strip() else None\n        \n        # Procesar ingreso\n        exito, mensaje, movimiento = self.ingreso_service.ingresar_vehiculo(ficha, dni)\n        \n        if exito:\n            self.agregar_mensaje(mensaje, 'exito')\n            self.limpiar_campos()\n            self.actualizar_datos()\n        else:\n            self.agregar_mensaje(f\"❌ ERROR INGRESO: {mensaje}\", 'error')\n            messagebox.showerror(\"Error de Ingreso\", mensaje)\n        \n        self.entry_ficha.focus_set()\n    \n    def procesar_salida(self, event=None):\n        \"\"\"Procesa la salida de un vehículo\"\"\"\n        ficha_str = self.ficha_var.get().strip()\n        if not ficha_str or not ficha_str.isdigit():\n            messagebox.showerror(\"Error\", \"Debe ingresar un número de ficha válido\")\n            self.entry_ficha.focus_set()\n            return\n        \n        ficha = int(ficha_str)\n        \n        # Procesar egreso\n        exito, mensaje, detalle = self.egreso_service.procesar_egreso(ficha)\n        \n        if exito:\n            self.agregar_mensaje(mensaje, 'exito')\n            \n            # Mostrar detalle en ventana grande\n            self.mostrar_detalle_egreso(detalle)\n            \n            self.limpiar_campos()\n            self.actualizar_datos()\n        else:\n            self.agregar_mensaje(f\"❌ ERROR EGRESO: {mensaje}\", 'error')\n            messagebox.showerror(\"Error de Egreso\", mensaje)\n        \n        self.entry_ficha.focus_set()\n    \n    def mostrar_detalle_egreso(self, detalle):\n        \"\"\"Muestra detalle de egreso en ventana grande\"\"\"\n        ventana = tk.Toplevel(self.root)\n        ventana.title(\"Detalle de Egreso\")\n        ventana.geometry(\"500x400\")\n        ventana.configure(bg='#f0f0f0')\n        ventana.transient(self.root)\n        ventana.grab_set()\n        \n        # Título\n        titulo = tk.Label(ventana, text=\"EGRESO PROCESADO\", \n                         font=(\"Arial\", 20, \"bold\"), bg='#f0f0f0', fg='#27ae60')\n        titulo.pack(pady=20)\n        \n        # Información principal - TEXTO GRANDE\n        info_frame = tk.Frame(ventana, bg='#f0f0f0')\n        info_frame.pack(expand=True, fill=tk.BOTH, padx=20)\n        \n        # Ficha\n        tk.Label(info_frame, text=f\"FICHA: {detalle['ficha']}\", \n                font=(\"Arial\", 24, \"bold\"), bg='#f0f0f0', fg='#2c3e50').pack(pady=10)\n        \n        # Tiempo\n        tk.Label(info_frame, text=f\"TIEMPO: {detalle['tiempo_str']}\", \n                font=(\"Arial\", 20), bg='#f0f0f0', fg='#2c3e50').pack(pady=5)\n        \n        # Monto - MUY GRANDE\n        if detalle['es_abonado']:\n            tk.Label(info_frame, text=\"💳 ABONADO\", \n                    font=(\"Arial\", 28, \"bold\"), bg='#f0f0f0', fg='#27ae60').pack(pady=10)\n            tk.Label(info_frame, text=\"SIN COSTO\", \n                    font=(\"Arial\", 24, \"bold\"), bg='#f0f0f0', fg='#27ae60').pack(pady=5)\n        else:\n            tk.Label(info_frame, text=f\"💰 ${detalle['monto']:.2f}\", \n                    font=(\"Arial\", 32, \"bold\"), bg='#f0f0f0', fg='#e74c3c').pack(pady=10)\n            tk.Label(info_frame, text=f\"Tarifa: {detalle['motivo'].upper()}\", \n                    font=(\"Arial\", 16), bg='#f0f0f0', fg='#2c3e50').pack(pady=5)\n        \n        # Persona si existe\n        if detalle.get('persona'):\n            tk.Label(info_frame, text=f\"Cliente: {detalle['persona']}\", \n                    font=(\"Arial\", 14), bg='#f0f0f0', fg='#2c3e50').pack(pady=5)\n        \n        # Botón cerrar\n        tk.Button(ventana, text=\"CERRAR\", font=(\"Arial\", 14, \"bold\"), \n                 command=ventana.destroy, bg='#3498db', fg='white',\n                 width=15, height=2).pack(pady=20)\n        \n        # Cerrar automáticamente después de 10 segundos\n        ventana.after(10000, ventana.destroy)\n    \n    def validar_dni(self, event=None):\n        \"\"\"Valida DNI y muestra información detallada\"\"\"\n        dni = self.dni_var.get().strip()\n        if not dni:\n            messagebox.showwarning(\"Validación DNI\", \"Debe ingresar un DNI\")\n            self.entry_dni.focus_set()\n            return\n        \n        try:\n            es_valido, mensaje, abono, persona = self.ingreso_service.validar_dni(dni)\n            \n            info = f\"DNI: {dni}\\n\\n\"\n            \n            if persona:\n                info += f\"Persona: {persona.nombre} {persona.apellido}\\n\"\n                if persona.telefono:\n                    info += f\"Teléfono: {persona.telefono}\\n\"\n                if persona.email:\n                    info += f\"Email: {persona.email}\\n\"\n                info += f\"Registrado: {persona.fecha_alta.strftime('%d/%m/%Y') if persona.fecha_alta else 'N/A'}\\n\\n\"\n            \n            if abono:\n                estado_dict = abono if isinstance(abono, dict) else None\n                if estado_dict:\n                    info += f\"Estado Abono: {estado_dict.get('estado', 'desconocido').upper()}\\n\"\n                    info += f\"Vigencia: {estado_dict.get('fecha_inicio', 'N/A')} a {estado_dict.get('fecha_fin', 'N/A')}\\n\"\n                else:\n                    info += \"Abono: VIGENTE\\n\"\n            else:\n                info += \"Abono: SIN ABONO VIGENTE\\n\"\n            \n            messagebox.showinfo(\"Validación DNI\", info)\n            \n        except Exception as e:\n            messagebox.showerror(\"Error\", f\"Error al validar DNI: {e}\")\n    \n    def limpiar_campos(self, event=None):\n        \"\"\"Limpia todos los campos\"\"\"\n        self.ficha_var.set(\"\")\n        self.dni_var.set(\"\")\n        self.entry_ficha.config(bg='white')\n        self.actualizar_semaforo('gris', 'Sin DNI')\n        self.entry_ficha.focus_set()\n    \n    def actualizar_datos(self):\n        \"\"\"Actualiza todos los datos de la interfaz\"\"\"\n        try:\n            # Obtener estado del estacionamiento\n            estado = self.ingreso_service.obtener_estado_estacionamiento()\n            \n            # Actualizar contador\n            self.lbl_contador.config(text=f\"Ocupadas: {estado['ocupadas']}/{estado['capacidad']}\")\n            \n            # Actualizar estado\n            if estado['estado'] == 'COMPLETO':\n                self.lbl_estado.config(text=\"COMPLETO\", fg='#e74c3c')\n            else:\n                self.lbl_estado.config(text=\"DISPONIBLE\", fg='#27ae60')\n            \n            # Actualizar barra de progreso\n            porcentaje = estado['porcentaje_ocupacion']\n            self.progress['value'] = porcentaje\n            \n            # Actualizar lista de ocupadas\n            self.lista_ocupadas.delete(0, tk.END)\n            for ficha in estado['fichas_ocupadas']:\n                self.lista_ocupadas.insert(tk.END, f\"Ficha {ficha}\")\n            \n            # Actualizar lista de libres (solo mostrar primeras 50 para performance)\n            self.lista_libres.delete(0, tk.END)\n            libres_mostrar = estado['fichas_libres'][:50]\n            for ficha in libres_mostrar:\n                self.lista_libres.insert(tk.END, f\"Ficha {ficha}\")\n            \n            if len(estado['fichas_libres']) > 50:\n                self.lista_libres.insert(tk.END, f\"... y {len(estado['fichas_libres']) - 50} más\")\n        \n        except Exception as e:\n            self.agregar_mensaje(f\"Error al actualizar datos: {e}\", 'error')\n        \n        # Programar próxima actualización\n        self.root.after(5000, self.actualizar_datos)\n\n\n# Funciones de inicialización\ndef main():\n    \"\"\"Función principal\"\"\"\n    root = tk.Tk()\n    app = VentanaPrincipalMejorada(root)\n    root.mainloop()\n\nif __name__ == \"__main__\":\n    main()
