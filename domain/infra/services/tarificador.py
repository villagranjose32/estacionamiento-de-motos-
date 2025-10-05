from dataclasses import asdict
from math import ceil
from datetime import datetime, timedelta, time
from typing import Dict, List, Tuple, Optional
import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from domain.models import Config, Turno, DetalleTarifa, Abono
from domain.enums import ReglaEleccionMonto, RedondeoTurno, ExcesoTurno, EstadoAbono

DOW = ["L","M","X","J","V","S","D"]  # Monday..Sunday mapping: 0..6 -> L..D

class Tarificador:
    def __init__(self, cfg: Config, turnos: List[Turno], abono_vigente: Optional[Abono] = None):
        self.cfg = cfg
        self.turnos = [t for t in turnos if t.activo]
        self.abono_vigente = abono_vigente

    def _candidato_fraccion(self, minutos_total: int) -> float:
        """Calcula tarifa por fracción con gracia configurable"""
        m_ef = max(0, minutos_total - self.cfg.gracia_min)
        fracciones = 0 if m_ef == 0 else ceil(m_ef / self.cfg.fraccion_min)
        return fracciones * self.cfg.precio_por_fraccion

    def _candidato_diaria(self, minutos_total: int) -> float:
        """Calcula tarifa diaria si aplica"""
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
        """Calcula tarifa por turno - implementación ENTERO"""
        if not self.cfg.aplica_tarifa_por_turno:
            return float("inf")
        
        # Solo implementamos redondeo ENTERO para MVP
        if self.cfg.redondeo_turno != RedondeoTurno.ENTERO:
            return float("inf")
        
        periodos = self._periodos_turno_en_rango(entrada, salida)
        if not periodos:
            return float("inf")
        
        # Agrupar por (nombre, inicio absoluto) para no duplicar
        tocados = {}
        for t, abs_ini, abs_fin in periodos:
            key = (t.nombre, abs_ini)
            tocados[key] = t
        
        total = sum(t.precio for t in tocados.values())
        return total

    def _validar_abono(self, entrada: datetime, salida: datetime) -> Tuple[bool, EstadoAbono, str]:
        """
        Valida si hay abono vigente y si cubre el período completo
        Política: si ingresó vigente, cubre hasta egreso (= $0)
        """
        if not self.abono_vigente:
            return False, EstadoAbono.VENCIDO, "Sin abono"
        
        estado_entrada = self.abono_vigente.estado(self.cfg.dias_alerta_vencimiento)
        estado_salida = self.abono_vigente.estado(self.cfg.dias_alerta_vencimiento)
        
        # Verificar estado al momento de entrada
        if estado_entrada in [EstadoAbono.VIGENTE, EstadoAbono.POR_VENCER]:
            # Si ingresó vigente/por vencer, aplicar política de cobertura
            if self.cfg.cubre_hasta_egreso_si_vencia_durante_estadia:
                # Cubre hasta egreso incluso si vence durante estadía
                mensaje = f"Abono {estado_entrada.value} al ingreso - Cubre hasta egreso"
                return True, estado_entrada, mensaje
            else:
                # Solo cubre si sigue vigente al egreso
                fecha_salida = salida.date()
                if fecha_salida <= self.abono_vigente.fecha_fin:
                    mensaje = f"Abono {estado_entrada.value} - Vigente hasta egreso"
                    return True, estado_entrada, mensaje
                else:
                    mensaje = f"Abono venció durante estadía"
                    return False, EstadoAbono.VENCIDO, mensaje
        
        mensaje = f"Abono {estado_entrada.value} al ingreso"
        return False, estado_entrada, mensaje

    def calcular(self, entrada: datetime, salida: datetime, dni_abonado: Optional[str] = None) -> DetalleTarifa:
        """
        Calcula tarifa considerando abonos y todas las reglas de negocio
        """
        minutos = int((salida - entrada).total_seconds() // 60)
        
        # Verificar abono primero
        es_abonado, estado_abono, mensaje_abono = self._validar_abono(entrada, salida)
        
        if es_abonado:
            # Abonado vigente = $0
            return DetalleTarifa(
                monto_final=0.0,
                motivo="abono",
                candidatos={"abono": 0.0},
                es_abonado=True,
                dni_abonado=dni_abonado,
                estado_abono=estado_abono
            )
        
        # Calcular candidatos de pago
        cand: Dict[str, float] = {}
        
        # Tarifa por fracción
        cand["fraccion"] = self._candidato_fraccion(minutos)
        
        # Tarifa diaria
        d = self._candidato_diaria(minutos)
        if d != float("inf"):
            cand["diaria"] = d
        
        # Tarifa por turno
        t = self._candidato_turno(entrada, salida)
        if t != float("inf"):
            cand["turno"] = t

        # Aplicar regla de elección
        if self.cfg.regla_eleccion_monto == ReglaEleccionMonto.MAS_BARATO:
            motivo, monto = min(cand.items(), key=lambda kv: kv[1])
        else:
            # Prioridad según configuración: "turno>diaria>fraccion"
            orden = [x.strip() for x in self.cfg.prioridad_precio.split(">")]
            monto = float("inf")
            motivo = "fraccion"  # fallback
            for m in orden:
                if m in cand:
                    motivo, monto = m, cand[m]
                    break

        return DetalleTarifa(
            monto_final=monto,
            motivo=motivo,
            candidatos=cand,
            es_abonado=False,
            dni_abonado=dni_abonado,
            estado_abono=estado_abono if self.abono_vigente else None
        )

    def calcular_con_contexto(self, entrada: datetime, salida: datetime, 
                            dni_abonado: Optional[str] = None, 
                            abono_vigente: Optional[Abono] = None) -> DetalleTarifa:
        """
        Calcula tarifa con contexto específico de abono
        Útil para simular diferentes escenarios
        """
        # Crear una instancia temporal con el abono específico
        tarificador_temp = Tarificador(self.cfg, self.turnos, abono_vigente)
        return tarificador_temp.calcular(entrada, salida, dni_abonado)

    def simular_tarifas(self, entrada: datetime, salida: datetime) -> Dict[str, float]:
        """
        Simula todas las tarifas posibles para mostrar al usuario
        """
        minutos = int((salida - entrada).total_seconds() // 60)
        
        simulacion = {}
        
        # Siempre calcular fracción
        simulacion["fraccion"] = self._candidato_fraccion(minutos)
        
        # Tarifa diaria si aplica
        if self.cfg.aplica_tarifa_diaria:
            diaria = self._candidato_diaria(minutos)
            if diaria != float("inf"):
                simulacion["diaria"] = diaria
        
        # Tarifa por turno si aplica
        if self.cfg.aplica_tarifa_por_turno:
            turno = self._candidato_turno(entrada, salida)
            if turno != float("inf"):
                simulacion["turno"] = turno
        
        return simulacion

    def validar_configuracion(self) -> List[str]:
        """
        Valida la configuración del tarificador
        Retorna lista de errores/advertencias
        """
        errores = []
        
        if self.cfg.gracia_min < 0:
            errores.append("Gracia no puede ser negativa")
        
        if self.cfg.fraccion_min <= 0:
            errores.append("Fracción debe ser mayor a 0")
        
        if self.cfg.precio_por_fraccion <= 0:
            errores.append("Precio por fracción debe ser mayor a 0")
        
        if self.cfg.aplica_tarifa_diaria:
            if self.cfg.tarifa_diaria <= 0:
                errores.append("Tarifa diaria debe ser mayor a 0")
            if self.cfg.umbral_diaria_horas <= 0:
                errores.append("Umbral diaria debe ser mayor a 0")
        
        if self.cfg.aplica_tarifa_por_turno:
            if not self.turnos:
                errores.append("No hay turnos activos configurados")
            
            for turno in self.turnos:
                if turno.precio <= 0:
                    errores.append(f"Turno '{turno.nombre}' tiene precio inválido")
        
        return errores
