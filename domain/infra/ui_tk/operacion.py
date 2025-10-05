import tkinter as tk
from tkinter import ttk, messagebox
from dataclasses import asdict
from math import ceil
from datetime import datetime, timedelta, time
from typing import Dict, List, Tuple
import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from domain.models import Config, Turno, DetalleTarifa
from domain.enums import ReglaEleccionMonto, RedondeoTurno, ExcesoTurno

DOW = ["L","M","X","J","V","S","D"]  # Monday..Sunday mapping: 0..6 -> L..D

class Tarificador:
    def __init__(self, cfg: Config, turnos: List[Turno]):
        self.cfg = cfg
        self.turnos = [t for t in turnos if t.activo]

    def _candidato_fraccion(self, minutos_total: int) -> float:
        m_ef = max(0, minutos_total - self.cfg.gracia_min)
        fracciones = 0 if m_ef == 0 else ceil(m_ef / self.cfg.fraccion_min)
        return fracciones * self.cfg.precio_por_fraccion

    def _candidato_diaria(self, minutos_total: int) -> float:
        if not self.cfg.aplica_tarifa_diaria:
            return float("inf")
        if minutos_total >= self.cfg.umbral_diaria_horas * 60:
            return self.cfg.tarifa_diaria
        return float("inf")

    def _periodos_turno_en_rango(self, entrada: datetime, salida: datetime) -> List[Tuple[Turno, datetime, datetime]]:
        """
        Genera períodos (inicio, fin absoluto) de cada turno que interseca [entrada, salida).
        Maneja turnos que cruzan medianoche.
        """
        out = []
        # iterar días desde día entrada-1 hasta salida+1 por seguridad
        dia = entrada.date() - timedelta(days=1)
        fin_lim = salida.date() + timedelta(days=1)
        while dia <= fin_lim:
            for t in self.turnos:
                if t.dias:
                    dow = DOW[(dia.weekday())]  # Monday=0 -> L
                    if dow not in t.dias:
                        continue
                start = datetime.combine(dia, t.hora_inicio)
                # fin puede ser mismo día o día siguiente
                if t.hora_fin > t.hora_inicio:
                    end = datetime.combine(dia, t.hora_fin)
                else:
                    end = datetime.combine(dia + timedelta(days=1), t.hora_fin)
                # intersección
                s = max(start, entrada)
                e = min(end, salida)
                if s < e:  # hay solape
                    out.append((t, start, end))
            dia += timedelta(days=1)
        return out

    def _candidato_turno(self, entrada: datetime, salida: datetime) -> float:
        if not self.cfg.aplica_tarifa_por_turno:
            return float("inf")
        # Implementación MVP: redondeo ENTERO y exceso MAS_BARATO => cobrar turno completo por cada turno tocado.
        if self.cfg.redondeo_turno != RedondeoTurno.ENTERO:
            # para v1, limitar a ENTERO
            return float("inf")
        periodos = self._periodos_turno_en_rango(entrada, salida)
        if not periodos:
            return float("inf")
        # agrupar por (nombre, inicio absoluto) para no duplicar
        tocados = {}
        for t, abs_ini, abs_fin in periodos:
            key = (t.nombre, abs_ini)
            tocados[key] = t
        total = sum(t.precio for t in tocados.values())
        return total

    def calcular(self, entrada: datetime, salida: datetime) -> DetalleTarifa:
        minutos = int((salida - entrada).total_seconds() // 60)
        cand: Dict[str, float] = {}
        # fracción
        cand["fraccion"] = self._candidato_fraccion(minutos)
        # diaria
        d = self._candidato_diaria(minutos)
        if d != float("inf"):
            cand["diaria"] = d
        # turno
        t = self._candidato_turno(entrada, salida)
        if t != float("inf"):
            cand["turno"] = t

        # elección
        if self.cfg.regla_eleccion_monto == ReglaEleccionMonto.MAS_BARATO:
            motivo, monto = min(cand.items(), key=lambda kv: kv[1])
        else:
            # prioridad_precio p.ej. "turno>diaria>fraccion"
            orden = [x.strip() for x in self.cfg.prioridad_precio.split(">")]
            monto = float("inf")
            motivo = "fraccion"
            for m in orden:
                if m in cand:
                    motivo, monto = m, cand[m]
                    break

        return DetalleTarifa(monto_final=monto, motivo=motivo, candidatos=cand)


class VentanaPrincipal:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Gestión de Estacionamiento")
        
        # Configuración de ejemplo
        self.config = Config(
            gracia_min=15,
            fraccion_min=30,
            precio_por_fraccion=5.0,
            aplica_tarifa_diaria=True,
            tarifa_diaria=50.0,
            umbral_diaria_horas=8,
            aplica_tarifa_por_turno=True,
            regla_eleccion_monto=ReglaEleccionMonto.MAS_BARATO,
            redondeo_turno=RedondeoTurno.ENTERO,
            exceso_turno=ExcesoTurno.MAS_BARATO,
            prioridad_precio="turno>diaria>fraccion"
        )
        
        # Turnos de ejemplo
        self.turnos = [
            Turno(
                nombre="Mañana",
                hora_inicio=time(8, 0),
                hora_fin=time(14, 0),
                precio=20.0,
                dias=["L", "M", "X", "J", "V"],
                activo=True
            ),
            Turno(
                nombre="Tarde",
                hora_inicio=time(14, 0),
                hora_fin=time(20, 0),
                precio=25.0,
                dias=["L", "M", "X", "J", "V"],
                activo=True
            )
        ]
        
        self.tarificador = Tarificador(self.config, self.turnos)
        self.crear_interfaz()
    
    def crear_interfaz(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Título
        titulo = ttk.Label(main_frame, text="Sistema de Estacionamiento", 
                          font=("Arial", 16, "bold"))
        titulo.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Frame para entrada
        entrada_frame = ttk.LabelFrame(main_frame, text="Hora de Entrada", padding="10")
        entrada_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(entrada_frame, text="Fecha y Hora:").grid(row=0, column=0, sticky=tk.W)
        self.entrada_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d %H:%M"))
        ttk.Entry(entrada_frame, textvariable=self.entrada_var, width=20).grid(row=0, column=1, padx=(10, 0))
        
        # Frame para salida
        salida_frame = ttk.LabelFrame(main_frame, text="Hora de Salida", padding="10")
        salida_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(salida_frame, text="Fecha y Hora:").grid(row=0, column=0, sticky=tk.W)
        self.salida_var = tk.StringVar(value=(datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%d %H:%M"))
        ttk.Entry(salida_frame, textvariable=self.salida_var, width=20).grid(row=0, column=1, padx=(10, 0))
        
        # Botón calcular
        ttk.Button(main_frame, text="Calcular Tarifa", command=self.calcular_tarifa).grid(row=3, column=0, columnspan=2, pady=20)
        
        # Frame para resultado
        resultado_frame = ttk.LabelFrame(main_frame, text="Resultado", padding="10")
        resultado_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        self.resultado_text = tk.Text(resultado_frame, height=10, width=60)
        self.resultado_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar para el texto
        scrollbar = ttk.Scrollbar(resultado_frame, orient="vertical", command=self.resultado_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.resultado_text.configure(yscrollcommand=scrollbar.set)
        
        # Configurar peso de columnas y filas
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        resultado_frame.columnconfigure(0, weight=1)
        resultado_frame.rowconfigure(0, weight=1)
    
    def calcular_tarifa(self):
        try:
            # Parsear fechas
            entrada_str = self.entrada_var.get()
            salida_str = self.salida_var.get()
            
            entrada = datetime.strptime(entrada_str, "%Y-%m-%d %H:%M")
            salida = datetime.strptime(salida_str, "%Y-%m-%d %H:%M")
            
            if salida <= entrada:
                messagebox.showerror("Error", "La hora de salida debe ser posterior a la de entrada")
                return
            
            # Calcular tarifa
            detalle = self.tarificador.calcular(entrada, salida)
            
            # Mostrar resultado
            duracion = salida - entrada
            horas = duracion.total_seconds() / 3600
            
            resultado = f"""CÁLCULO DE TARIFA DE ESTACIONAMIENTO
===========================================

Entrada: {entrada.strftime('%d/%m/%Y %H:%M')}
Salida:  {salida.strftime('%d/%m/%Y %H:%M')}
Duración: {int(horas)}h {int((horas % 1) * 60)}min

TARIFA APLICADA: {detalle.motivo.upper()}
MONTO A PAGAR: ${detalle.monto_final:.2f}

CANDIDATOS EVALUADOS:
"""
            
            for metodo, monto in detalle.candidatos.items():
                if monto != float("inf"):
                    resultado += f"- {metodo.capitalize()}: ${monto:.2f}\n"
            
            resultado += f"""
CONFIGURACIÓN ACTUAL:
- Gracia: {self.config.gracia_min} minutos
- Fracción: {self.config.fraccion_min} minutos (${self.config.precio_por_fraccion})
- Tarifa diaria: ${self.config.tarifa_diaria} (umbral: {self.config.umbral_diaria_horas}h)
- Regla de elección: {self.config.regla_eleccion_monto.value}

TURNOS CONFIGURADOS:
"""
            
            for turno in self.turnos:
                if turno.activo:
                    resultado += f"- {turno.nombre}: {turno.hora_inicio.strftime('%H:%M')}-{turno.hora_fin.strftime('%H:%M')} (${turno.precio}) - Días: {', '.join(turno.dias)}\n"
            
            self.resultado_text.delete(1.0, tk.END)
            self.resultado_text.insert(1.0, resultado)
            
        except ValueError as e:
            messagebox.showerror("Error", f"Formato de fecha incorrecto. Use: YYYY-MM-DD HH:MM\nError: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al calcular tarifa: {e}")
