from datetime import datetime
from typing import Optional, Tuple, Dict
import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from domain.models import Config, Abono
from domain.enums import EstadoAbono
from domain.infra.config_repo import ConfigRepo
from domain.infra.abonos_repo import AbonosRepo
from domain.infra.personas_repo import PersonasRepo
from domain.infra.movimientos_repo import MovimientosRepo
from domain.infra.turnos_repo import TurnosRepo
from domain.infra.paths import SedePaths
from .tarificador import Tarificador


class EgresoServiceNuevo:
    def __init__(self, paths: SedePaths):
        self.config_repo = ConfigRepo(paths)
        self.abonos_repo = AbonosRepo(paths)
        self.personas_repo = PersonasRepo(paths)
        self.movimientos_repo = MovimientosRepo(paths)
        self.turnos_repo = TurnosRepo(paths)
        self.config = self.config_repo.load_or_create_defaults()
    
    def validar_ficha_ocupada(self, nro_ficha: int) -> Tuple[bool, str, Optional[dict]]:
        """
        Valida que la ficha esté ocupada y obtiene los datos del movimiento
        Returns: (es_valida, mensaje, movimiento)
        """
        # Validar rango
        if nro_ficha < 1 or nro_ficha > self.config.capacidad:
            return False, f"Ficha debe estar entre 1 y {self.config.capacidad}", None
        
        # Buscar movimiento abierto
        movimiento = self.movimientos_repo.obtener_abierto_por_ficha(nro_ficha)
        if not movimiento:
            return False, f"Ficha {nro_ficha} no está ocupada", None
        
        return True, "Ficha ocupada", movimiento
    
    def calcular_tarifa(self, movimiento: dict, fecha_salida: Optional[datetime] = None) -> Dict:
        """
        Calcula la tarifa usando el tarificador
        """
        if fecha_salida is None:
            fecha_salida = datetime.now()
        
        # Parsear fecha de entrada
        fecha_entrada_str = movimiento.get('hora_entrada', '')
        try:
            fecha_entrada = datetime.strptime(fecha_entrada_str, "%Y-%m-%d %H:%M")
        except ValueError:
            return {
                "error": f"Formato de fecha de entrada inválido: {fecha_entrada_str}",
                "monto": 0.0,
                "motivo": "error",
                "candidatos": {},
                "duracion_minutos": 0
            }
        
        # Calcular duración
        duracion = fecha_salida - fecha_entrada
        minutos = int(duracion.total_seconds() // 60)
        
        # Verificar si hay abono vigente
        dni = movimiento.get('dni')
        abonado_vigente_al_ingreso = movimiento.get('abonado_vigente_al_ingreso', False)
        
        # Si era abonado al ingreso y la política cubre hasta egreso
        if dni and abonado_vigente_al_ingreso and self.config.cubre_hasta_egreso_si_vencia_durante_estadia:
            return {
                "monto": 0.0,
                "motivo": "abonado",
                "candidatos": {"abonado": 0.0},
                "duracion_minutos": minutos,
                "es_abonado": True,
                "dni_abonado": dni,
                "estado_abono": "vigente_al_ingreso"
            }
        
        # Obtener turnos activos
        turnos = self.turnos_repo.load_all()
        
        # Crear tarificador
        tarificador = Tarificador(self.config, turnos)
        
        # Calcular tarifa
        try:
            detalle = tarificador.calcular(fecha_entrada, fecha_salida)
            
            return {
                "monto": detalle.monto_final,
                "motivo": detalle.motivo,
                "candidatos": detalle.candidatos,
                "duracion_minutos": minutos,
                "es_abonado": False,
                "dni_abonado": dni
            }
        except Exception as e:
            return {
                "error": f"Error al calcular tarifa: {e}",
                "monto": 0.0,
                "motivo": "error",
                "candidatos": {},
                "duracion_minutos": minutos
            }
    
    def procesar_egreso(self, nro_ficha: int, fecha_salida: Optional[datetime] = None, 
                       usuario: str = "Sistema") -> Tuple[bool, str, Optional[Dict]]:
        """
        Procesa el egreso de un vehículo
        Returns: (exito, mensaje, detalle_egreso)
        """
        try:
            # Validar ficha
            ficha_valida, msg_ficha, movimiento = self.validar_ficha_ocupada(nro_ficha)
            if not ficha_valida:
                return False, msg_ficha, None
            
            # Verificación adicional para asegurarse de que el movimiento existe
            if not movimiento:
                return False, f"No hay registro de ingreso para la ficha {nro_ficha}", None
            
            if fecha_salida is None:
                fecha_salida = datetime.now()
            
            # Calcular tarifa
            detalle_tarifa = self.calcular_tarifa(movimiento, fecha_salida)
            
            if "error" in detalle_tarifa:
                return False, detalle_tarifa["error"], None
            
            monto = detalle_tarifa["monto"]
            motivo = detalle_tarifa["motivo"]
            minutos = detalle_tarifa["duracion_minutos"]
            
            # Usar el servicio existente para cerrar
            resultado = self.movimientos_repo.cerrar(
                ficha=nro_ficha,
                monto=monto,
                minutos=minutos,
                detalle_tarifa=detalle_tarifa,
                usuario=usuario
            )
            
            # Formatear tiempo de estadía
            horas = minutos // 60
            mins_restantes = minutos % 60
            tiempo_str = f"{horas}h {mins_restantes}min" if horas > 0 else f"{mins_restantes}min"
            
            # Generar mensaje de éxito
            msg_exito = f"✅ EGRESO PROCESADO\nFicha: {nro_ficha}\nTiempo: {tiempo_str}"
            
            if detalle_tarifa.get("es_abonado"):
                msg_exito += f"\n💳 ABONADO - Sin costo"
                estado_abono = detalle_tarifa.get("estado_abono")
                if estado_abono:
                    msg_exito += f"\nEstado: {estado_abono.upper()}"
            else:
                msg_exito += f"\n💰 MONTO: ${monto:.2f}"
                msg_exito += f"\nTarifa: {motivo.upper()}"
            
            # Información del abonado si existe
            dni = movimiento.get('dni')
            if dni:
                persona = self.personas_repo.buscar_por_dni(dni)
                if persona:
                    msg_exito += f"\nPersona: {persona.nombre} {persona.apellido}"
            
            # Actualizar contador
            abiertos = self.movimientos_repo.listar_abiertos()
            ocupadas = len(abiertos)
            msg_exito += f"\nOcupadas: {ocupadas}/{self.config.capacidad}"
            
            detalle_egreso = {
                "ficha": nro_ficha,
                "entrada": movimiento.get('hora_entrada'),
                "salida": fecha_salida.strftime("%Y-%m-%d %H:%M"),
                "duracion_minutos": minutos,
                "tiempo_str": tiempo_str,
                "monto": monto,
                "motivo": motivo,
                "candidatos": detalle_tarifa.get("candidatos", {}),
                "es_abonado": detalle_tarifa.get("es_abonado", False),
                "dni": dni,
                "persona": persona.nombre + " " + persona.apellido if dni and persona else None
            }
            
            return True, msg_exito, detalle_egreso
            
        except Exception as e:
            return False, f"Error al procesar egreso: {e}", None
    
    def simular_tarifa(self, nro_ficha: int, fecha_salida: Optional[datetime] = None) -> Dict:
        """
        Simula el cálculo de tarifa sin procesar el egreso
        """
        # Validar ficha
        ficha_valida, msg_ficha, movimiento = self.validar_ficha_ocupada(nro_ficha)
        if not ficha_valida:
            return {"error": msg_ficha}
        
        if fecha_salida is None:
            fecha_salida = datetime.now()
        
        # Calcular tarifa
        detalle_tarifa = self.calcular_tarifa(movimiento, fecha_salida)
        
        # Agregar información adicional
        fecha_entrada_str = movimiento.get('hora_entrada', '')
        try:
            fecha_entrada = datetime.strptime(fecha_entrada_str, "%Y-%m-%d %H:%M")
            duracion = fecha_salida - fecha_entrada
            minutos = int(duracion.total_seconds() // 60)
            horas = minutos // 60
            mins_restantes = minutos % 60
            
            detalle_tarifa.update({
                "fecha_entrada": fecha_entrada_str,
                "fecha_salida": fecha_salida.strftime("%Y-%m-%d %H:%M"),
                "tiempo_str": f"{horas}h {mins_restantes}min" if horas > 0 else f"{mins_restantes}min",
                "ficha": nro_ficha
            })
        except:
            pass
        
        return detalle_tarifa
    
    def obtener_detalle_movimiento(self, nro_ficha: int) -> Optional[Dict]:
        """
        Obtiene el detalle completo de un movimiento abierto
        """
        movimiento = self.movimientos_repo.obtener_abierto_por_ficha(nro_ficha)
        if not movimiento:
            return None
        
        # Agregar información adicional
        dni = movimiento.get('dni')
        persona = None
        abono_estado = None
        
        if dni:
            persona = self.personas_repo.buscar_por_dni(dni)
            abono_dict = self.abonos_repo.get_vigente_by_dni(dni)
            if abono_dict:
                abono_estado = abono_dict.get('estado', 'desconocido')
        
        return {
            **movimiento,
            "persona": persona,
            "abono_estado": abono_estado
        }
