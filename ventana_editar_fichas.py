import tkinter as tk
from tkinter import messagebox, ttk
import ttkbootstrap
from datetime import datetime
import sys
import os
import json
import tempfile

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(__file__))

from domain.infra.paths import SedePaths
from domain.infra.movimientos_repo import MovimientosRepo


class VentanaEditarFichas:
    def __init__(self, root):
        self.root = root
        self.root.title("Editar Fichas")
        self.root.geometry("1000x700")
        
        # Configurar servicios
        self.paths = SedePaths()
        self.movimientos_repo = MovimientosRepo(self.paths)
        
        # Variables
        self.ficha_seleccionada = None
        self.fichas_abiertas = []
        self.fichas_cerradas = []
        self.mes_actual = None
        
        self.crear_interfaz()
        self.cargar_fichas()
    
    def crear_interfaz(self):
        """Crea la interfaz de edición de fichas"""
        main_frame = ttk.Frame(self.root, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        titulo = ttk.Label(main_frame, text="📋 EDITAR FICHAS", 
                          font=("Arial", 18, "bold"))
        titulo.pack(pady=(0, 15))
        
        # Frame de búsqueda
        search_frame = ttk.LabelFrame(main_frame, text="Búsqueda", padding=10)
        search_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(search_frame, text="Nro. Ficha:").pack(side=tk.LEFT, padx=5)
        self.search_ficha = ttk.Entry(search_frame, width=15)
        self.search_ficha.pack(side=tk.LEFT, padx=5)
        self.search_ficha.bind('<Return>', lambda e: self.buscar_ficha())
        
        ttk.Button(search_frame, text="🔍 Buscar", 
                  command=self.buscar_ficha).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(search_frame, text="🔄 Recargar", 
                  command=self.cargar_fichas).pack(side=tk.LEFT, padx=5)
        
        # Tabs para fichas abiertas y cerradas
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Tab Fichas Abiertas
        tab_abiertas = ttk.Frame(self.notebook)
        self.notebook.add(tab_abiertas, text="Fichas Abiertas")
        self.crear_tabla_fichas(tab_abiertas, "abierta")
        
        # Tab Fichas Cerradas
        tab_cerradas = ttk.Frame(self.notebook)
        self.notebook.add(tab_cerradas, text="Fichas Cerradas")
        self.crear_tabla_fichas(tab_cerradas, "cerrada")
        
        # Frame de botones
        botones_frame = ttk.Frame(main_frame)
        botones_frame.pack(fill=tk.X)
        
        ttk.Button(botones_frame, text="✏️ Editar", 
                  command=self.editar_ficha).pack(side=tk.LEFT, padx=5)
        ttk.Button(botones_frame, text="❌ Cerrar (si está abierta)", 
                  command=self.cerrar_ficha).pack(side=tk.LEFT, padx=5)
        ttk.Button(botones_frame, text="🗑️ Eliminar", 
                  command=self.eliminar_ficha).pack(side=tk.LEFT, padx=5)
        ttk.Button(botones_frame, text="❌ Cerrar ventana", 
                  command=self.root.destroy).pack(side=tk.RIGHT, padx=5)
    
    def crear_tabla_fichas(self, parent, tipo):
        """Crea una tabla de fichas (abierta o cerrada)"""
        # Crear Treeview
        columns = ("Ficha", "DNI", "Entrada", "Salida", "Monto", "Duración")
        
        if tipo == "abierta":
            self.tree_abiertas = ttk.Treeview(parent, columns=columns, height=20)
            tree = self.tree_abiertas
            tree.bind('<Double-1>', lambda e: self.editar_ficha())
            tree.bind('<Delete>', lambda e: self.eliminar_ficha())
        else:
            self.tree_cerradas = ttk.Treeview(parent, columns=columns, height=20)
            tree = self.tree_cerradas
            tree.bind('<Double-1>', lambda e: self.editar_ficha())
        
        # Configurar columnas
        tree.column("#0", width=0, stretch=tk.NO)
        for col in columns:
            tree.column(col, anchor=tk.CENTER, width=150)
            tree.heading(col, text=col)
        
        # Añadir scrollbar
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        
        tree.pack(fill=tk.BOTH, expand=True, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def cargar_fichas(self):
        """Carga todas las fichas desde el repositorio"""
        try:
            # Cargar fichas abiertas
            self.fichas_abiertas = self.movimientos_repo.listar_abiertos()
            self.actualizar_tabla_abiertas()
            
            # Cargar fichas cerradas del mes actual
            from datetime import datetime
            ahora = datetime.now()
            self.mes_actual = ahora
            path_cerrados = self.paths.mov_cerrados_mes(ahora)
            
            self.fichas_cerradas = []
            if os.path.exists(path_cerrados):
                with open(path_cerrados, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            try:
                                self.fichas_cerradas.append(json.loads(line))
                            except:
                                pass
            
            # Ordenar por entrada descendente
            self.fichas_cerradas.sort(key=lambda x: x.get('entrada', ''), reverse=True)
            self.actualizar_tabla_cerradas()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar fichas: {e}")
    
    def actualizar_tabla_abiertas(self):
        """Actualiza la tabla de fichas abiertas"""
        # Limpiar tabla
        for item in self.tree_abiertas.get_children():
            self.tree_abiertas.delete(item)
        
        # Insertar fichas
        for ficha in self.fichas_abiertas:
            entrada = ficha.get('hora_entrada', '')
            dni = ficha.get('dni') or "---"
            
            self.tree_abiertas.insert("", tk.END, values=(
                ficha.get('ficha'),
                dni,
                entrada,
                "",
                "",
                ""
            ))
    
    def actualizar_tabla_cerradas(self):
        """Actualiza la tabla de fichas cerradas"""
        # Limpiar tabla
        for item in self.tree_cerradas.get_children():
            self.tree_cerradas.delete(item)
        
        # Insertar fichas
        for ficha in self.fichas_cerradas:
            entrada = ficha.get('entrada', '')
            salida = ficha.get('salida', '')
            monto = f"${ficha.get('monto', 0):.2f}" if ficha.get('monto') else "---"
            duracion = f"{ficha.get('minutos', 0)}min" if ficha.get('minutos') else "---"
            dni = ficha.get('dni') or "---"
            
            self.tree_cerradas.insert("", tk.END, values=(
                ficha.get('ficha'),
                dni,
                entrada,
                salida,
                monto,
                duracion
            ))
    
    def buscar_ficha(self):
        """Busca una ficha por número"""
        nro_ficha = self.search_ficha.get().strip()
        if not nro_ficha:
            messagebox.showwarning("Aviso", "Ingrese un número de ficha")
            return
        
        try:
            nro_ficha = int(nro_ficha)
            
            # Buscar en abiertas
            for i, ficha in enumerate(self.fichas_abiertas):
                if int(ficha.get('ficha')) == nro_ficha:
                    self.notebook.select(0)
                    items = self.tree_abiertas.get_children()
                    if i < len(items):
                        self.tree_abiertas.selection_set(items[i])
                        self.tree_abiertas.see(items[i])
                    return
            
            # Buscar en cerradas
            for i, ficha in enumerate(self.fichas_cerradas):
                if int(ficha.get('ficha')) == nro_ficha:
                    self.notebook.select(1)
                    items = self.tree_cerradas.get_children()
                    if i < len(items):
                        self.tree_cerradas.selection_set(items[i])
                        self.tree_cerradas.see(items[i])
                    return
            
            messagebox.showinfo("No encontrado", f"La ficha #{nro_ficha} no existe")
        
        except ValueError:
            messagebox.showerror("Error", "Ingrese un número válido")
    
    def obtener_ficha_seleccionada(self):
        """Obtiene la ficha seleccionada actualmente"""
        tab_actual = self.notebook.index(self.notebook.select())
        
        if tab_actual == 0:  # Abiertas
            seleccion = self.tree_abiertas.selection()
            if not seleccion:
                messagebox.showwarning("Aviso", "Seleccione una ficha")
                return None
            
            valores = self.tree_abiertas.item(seleccion[0])['values']
            nro_ficha = int(valores[0])
            
            for ficha in self.fichas_abiertas:
                if int(ficha.get('ficha')) == nro_ficha:
                    return ficha, "abierta"
        
        else:  # Cerradas
            seleccion = self.tree_cerradas.selection()
            if not seleccion:
                messagebox.showwarning("Aviso", "Seleccione una ficha")
                return None
            
            valores = self.tree_cerradas.item(seleccion[0])['values']
            nro_ficha = int(valores[0])
            
            for ficha in self.fichas_cerradas:
                if int(ficha.get('ficha')) == nro_ficha:
                    return ficha, "cerrada"
        
        return None
    
    def editar_ficha(self):
        """Abre el diálogo de edición de ficha"""
        resultado = self.obtener_ficha_seleccionada()
        if not resultado:
            return
        
        ficha, tipo = resultado
        nro_ficha = ficha.get('ficha')
        
        # Crear ventana de edición
        ventana_edit = tk.Toplevel(self.root)
        ventana_edit.title(f"Editar Ficha #{nro_ficha}")
        ventana_edit.geometry("500x450")
        ventana_edit.transient(self.root)
        ventana_edit.grab_set()
        
        # Título
        ttk.Label(ventana_edit, text=f"Editar Ficha #{nro_ficha}", 
                 font=("Arial", 14, "bold")).pack(pady=10)
        
        # Frame de datos
        frame_datos = ttk.LabelFrame(ventana_edit, text="Datos de la Ficha", padding=15)
        frame_datos.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # DNI
        ttk.Label(frame_datos, text="DNI:").grid(row=0, column=0, sticky=tk.W, pady=5)
        var_dni = tk.StringVar(value=ficha.get('dni') or "")
        ttk.Entry(frame_datos, textvariable=var_dni, width=20).grid(row=0, column=1, sticky=tk.W)
        
        # Entrada
        ttk.Label(frame_datos, text="Fecha Entrada:").grid(row=1, column=0, sticky=tk.W, pady=5)
        var_entrada = tk.StringVar(value=ficha.get('hora_entrada') or ficha.get('entrada', ''))
        ttk.Entry(frame_datos, textvariable=var_entrada, width=20).grid(row=1, column=1, sticky=tk.W)
        
        # Salida
        ttk.Label(frame_datos, text="Fecha Salida:").grid(row=2, column=0, sticky=tk.W, pady=5)
        var_salida = tk.StringVar(value=ficha.get('salida', ''))
        ttk.Entry(frame_datos, textvariable=var_salida, width=20).grid(row=2, column=1, sticky=tk.W)
        
        # Monto
        ttk.Label(frame_datos, text="Monto Cobrado:").grid(row=3, column=0, sticky=tk.W, pady=5)
        var_monto = tk.StringVar(value=str(ficha.get('monto', '')))
        ttk.Entry(frame_datos, textvariable=var_monto, width=20).grid(row=3, column=1, sticky=tk.W)
        
        # Motivo
        ttk.Label(frame_datos, text="Motivo:").grid(row=4, column=0, sticky=tk.W, pady=5)
        var_motivo = tk.StringVar(value=ficha.get('motivo', ''))
        ttk.Entry(frame_datos, textvariable=var_motivo, width=20).grid(row=4, column=1, sticky=tk.W)
        
        # Frame de botones
        frame_botones = ttk.Frame(ventana_edit)
        frame_botones.pack(fill=tk.X, padx=15, pady=15)
        
        def guardar_cambios():
            try:
                # Actualizar ficha
                ficha['dni'] = var_dni.get() or None
                ficha['hora_entrada'] = var_entrada.get()
                ficha['entrada'] = var_entrada.get()
                ficha['salida'] = var_salida.get()
                if var_monto.get():
                    ficha['monto'] = float(var_monto.get())
                ficha['motivo'] = var_motivo.get()
                
                # Guardar en archivo
                if tipo == "cerrada":
                    path_cerrados = self.paths.mov_cerrados_mes(self.mes_actual)
                    all_fichas = []
                    if os.path.exists(path_cerrados):
                        with open(path_cerrados, 'r', encoding='utf-8') as f:
                            for line in f:
                                line = line.strip()
                                if line:
                                    try:
                                        all_fichas.append(json.loads(line))
                                    except:
                                        pass
                    
                    # Reemplazar la ficha
                    all_fichas = [f if int(f.get('ficha')) != nro_ficha else ficha for f in all_fichas]
                    
                    # Escribir atomáticamente
                    fd, tmp = tempfile.mkstemp(prefix="tmp_", dir=os.path.dirname(path_cerrados))
                    os.close(fd)
                    try:
                        with open(tmp, "w", encoding="utf-8") as f:
                            for r in all_fichas:
                                f.write(json.dumps(r, ensure_ascii=False) + "\n")
                        os.replace(tmp, path_cerrados)
                    finally:
                        try:
                            if os.path.exists(tmp): os.remove(tmp)
                        except:
                            pass
                
                else:  # abierta
                    abiertos = self.movimientos_repo.listar_abiertos()
                    abiertos = [f if int(f.get('ficha')) != nro_ficha else ficha for f in abiertos]
                    
                    fd, tmp = tempfile.mkstemp(prefix="tmp_", dir=os.path.dirname(self.paths.mov_abiertos))
                    os.close(fd)
                    try:
                        with open(tmp, "w", encoding="utf-8") as f:
                            for r in abiertos:
                                f.write(json.dumps(r, ensure_ascii=False) + "\n")
                        os.replace(tmp, self.paths.mov_abiertos)
                    finally:
                        try:
                            if os.path.exists(tmp): os.remove(tmp)
                        except:
                            pass
                
                messagebox.showinfo("Éxito", "Ficha actualizada correctamente")
                ventana_edit.destroy()
                self.cargar_fichas()
                
            except ValueError as e:
                messagebox.showerror("Error", f"Verifique los datos: {e}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar: {e}")
        
        ttk.Button(frame_botones, text="💾 Guardar", 
                  command=guardar_cambios, bootstyle="success").pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botones, text="❌ Cancelar", 
                  command=ventana_edit.destroy).pack(side=tk.LEFT, padx=5)
    
    def cerrar_ficha(self):
        """Cierra una ficha abierta"""
        resultado = self.obtener_ficha_seleccionada()
        if not resultado:
            return
        
        ficha, tipo = resultado
        
        if tipo != "abierta":
            messagebox.showwarning("Aviso", "Esta ficha ya está cerrada")
            return
        
        # Diálogo para ingresar monto
        ventana_cierre = tk.Toplevel(self.root)
        ventana_cierre.title("Cerrar Ficha")
        ventana_cierre.geometry("350x200")
        ventana_cierre.transient(self.root)
        ventana_cierre.grab_set()
        
        ttk.Label(ventana_cierre, text=f"Cerrar Ficha #{ficha.get('ficha')}", 
                 font=("Arial", 12, "bold")).pack(pady=10)
        
        frame = ttk.Frame(ventana_cierre, padding=15)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Monto a cobrar:").pack(anchor=tk.W, pady=5)
        var_monto = tk.StringVar()
        ttk.Entry(frame, textvariable=var_monto, width=20, 
                 font=("Arial", 14)).pack(anchor=tk.W, pady=5)
        
        def confirmar_cierre():
            try:
                monto = float(var_monto.get())
                # Llamar al método cerrar del repositorio
                nro_ficha = int(ficha.get('ficha'))
                minutos = 0  # Se calcularía correctamente en el servicio
                detalle = {"motivo": "manual"}
                
                self.movimientos_repo.cerrar(nro_ficha, monto, minutos, detalle, "admin")
                messagebox.showinfo("Éxito", "Ficha cerrada correctamente")
                ventana_cierre.destroy()
                self.cargar_fichas()
            except ValueError:
                messagebox.showerror("Error", "Ingrese un monto válido")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cerrar: {e}")
        
        botones = ttk.Frame(frame)
        botones.pack(fill=tk.X, pady=10)
        ttk.Button(botones, text="✅ Cerrar", command=confirmar_cierre, 
                  bootstyle="success").pack(side=tk.LEFT, padx=5)
        ttk.Button(botones, text="❌ Cancelar", command=ventana_cierre.destroy).pack(side=tk.LEFT, padx=5)
    
    def eliminar_ficha(self):
        """Elimina una ficha"""
        resultado = self.obtener_ficha_seleccionada()
        if not resultado:
            return
        
        ficha, tipo = resultado
        nro_ficha = int(ficha.get('ficha'))
        
        respuesta = messagebox.askyesno("Confirmar", 
                                        f"¿Está seguro que desea eliminar la ficha #{nro_ficha}?")
        if not respuesta:
            return
        
        try:
            if tipo == "abierta":
                # Eliminar de abiertos
                abiertos = self.movimientos_repo.listar_abiertos()
                abiertos = [f for f in abiertos if int(f.get('ficha')) != nro_ficha]
                
                fd, tmp = tempfile.mkstemp(prefix="tmp_", dir=os.path.dirname(self.paths.mov_abiertos))
                os.close(fd)
                try:
                    with open(tmp, "w", encoding="utf-8") as f:
                        for r in abiertos:
                            f.write(json.dumps(r, ensure_ascii=False) + "\n")
                    os.replace(tmp, self.paths.mov_abiertos)
                finally:
                    try:
                        if os.path.exists(tmp): os.remove(tmp)
                    except:
                        pass
            else:
                # Eliminar de cerrados
                path_cerrados = self.paths.mov_cerrados_mes(self.mes_actual)
                all_fichas = []
                if os.path.exists(path_cerrados):
                    with open(path_cerrados, 'r', encoding='utf-8') as f:
                        for line in f:
                            line = line.strip()
                            if line:
                                try:
                                    all_fichas.append(json.loads(line))
                                except:
                                    pass
                
                all_fichas = [f for f in all_fichas if int(f.get('ficha')) != nro_ficha]
                
                fd, tmp = tempfile.mkstemp(prefix="tmp_", dir=os.path.dirname(path_cerrados))
                os.close(fd)
                try:
                    with open(tmp, "w", encoding="utf-8") as f:
                        for r in all_fichas:
                            f.write(json.dumps(r, ensure_ascii=False) + "\n")
                    os.replace(tmp, path_cerrados)
                finally:
                    try:
                        if os.path.exists(tmp): os.remove(tmp)
                    except:
                        pass
            
            messagebox.showinfo("Éxito", "Ficha eliminada correctamente")
            self.cargar_fichas()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar: {e}")


def mostrar_gestion_fichas(root):
    """Función auxiliar para mostrar la ventana de edición de fichas"""
    ventana = tk.Toplevel(root)
    app = VentanaEditarFichas(ventana)


if __name__ == "__main__":
    root = ttkbootstrap.Window(themename="superhero")
    app = VentanaEditarFichas(root)
    root.mainloop()
