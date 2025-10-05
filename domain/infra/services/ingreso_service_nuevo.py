from datetime import datetime
from typing import Optional, Tuple
import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from domain.models import Config, Movimiento, Abono, Persona
from domain.enums import EstadoAbono
from domain.infra.config_repo import ConfigRepo
from domain.infra.abonos_repo import AbonosRepo
from domain.infra.personas_repo import PersonasRepo
from domain.infra.movimientos_repo import MovimientosRepo
from domain.infra.paths import SedePaths


class IngresoServiceNuevo:
    def __init__(self, paths: SedePaths):
        self.config_repo = ConfigRepo(paths)
        self.abonos_repo = AbonosRepo(paths)
        self.personas_repo = PersonasRepo(paths)
        self.movimientos_repo = MovimientosRepo(paths)
        self.config = self.config_repo.load_or_create_defaults()
    
    def validar_ficha(self, nro_ficha: int) -> Tuple[bool, str]:
        """
        Valida que el número de ficha sea válido para ingreso
        Returns: (es_valida, mensaje)
        """
        # Validar rango
        if nro_ficha < 1 or nro_ficha > self.config.capacidad:
            return False, f"Ficha debe estar entre 1 y {self.config.capacidad}"
        
        # Validar que esté libre
        movimiento_existente = self.movimientos_repo.obtener_abierto_por_ficha(nro_ficha)
        if movimiento_existente:
            return False, f"Ficha {nro_ficha} ya está ocupada"
        
        return True, "Ficha disponible"
    
    def validar_capacidad(self) -> Tuple[bool, str]:
        """
        Valida que haya capacidad disponible
        Returns: (hay_capacidad, mensaje)
        """
        abiertos = self.movimientos_repo.listar_abiertos()
        ocupadas = len(abiertos)
        
        if ocupadas >= self.config.capacidad:
            return False, f"Estacionamiento COMPLETO ({ocupadas}/{self.config.capacidad})"
        
        disponibles = self.config.capacidad - ocupadas
        return True, f"Disponibles: {disponibles}/{self.config.capacidad}"
    
    def validar_dni(self, dni: str) -> Tuple[bool, str, Optional['Abono'], Optional[Persona]]:
        """
        Valida DNI y estado de abono
        Returns: (es_valido, mensaje, abono_vigente, persona)
        """
        if not dni or not dni.strip():
            return True, "Sin DNI", None, None
        
        dni = dni.strip()
        
        # Buscar persona
        persona = self.personas_repo.buscar_por_dni(dni)
        if not persona:
            return False, f"DNI {dni} no registrado", None, None
        
        # Buscar abono más reciente (incluyendo vencidos)
        abono = self.abonos_repo.abono_vigente_por_dni(dni)
        
        if not abono:
            return True, f"Sin abono registrado", None, persona
        
        estado = abono.estado()
        
        if estado.value == 'vigente':
            return True, f"Abono VIGENTE hasta {abono.fecha_fin}", abono, persona
        elif estado.value == 'por_vencer':
            return True, f"Abono POR VENCER (hasta {abono.fecha_fin})", abono, persona
        else:  # vencido
            return True, f"Abono VENCIDO (venció {abono.fecha_fin})", abono, persona
    
    def ingresar_vehiculo(self, nro_ficha: int, dni: Optional[str] = None, 
                         usuario: str = "Sistema") -> Tuple[bool, str, Optional[dict]]:
        """
        Registra el ingreso de un vehículo usando el servicio existente
        Returns: (exito, mensaje, resultado)
        """
        try:
            # Validar ficha
            ficha_valida, msg_ficha = self.validar_ficha(nro_ficha)
            if not ficha_valida:
                return False, msg_ficha, None
            
            # Validar capacidad
            hay_capacidad, msg_capacidad = self.validar_capacidad()
            if not hay_capacidad:
                return False, msg_capacidad, None
            
            # Validar DNI si se proporciona
            abono_vigente = None
            persona = None
            if dni:
                dni_valido, msg_dni, abono_vigente, persona = self.validar_dni(dni)
                if not dni_valido:
                    return False, msg_dni, None
            
            # Determinar si el abono está vigente para efectos de facturación
            es_abonado_vigente = bool(abono_vigente and abono_vigente.estado().value == 'vigente')
            
            # Usar el servicio existente para abrir
            resultado = self.movimientos_repo.abrir(
                ficha=nro_ficha,
                dni=dni,
                abonado_vigente=es_abonado_vigente,
                usuario=usuario
            )
            
            # Generar mensaje de éxito
            msg_exito = f"✅ INGRESO REGISTRADO\nFicha: {nro_ficha}\nHora: {resultado['hora_entrada']}"
            
            if dni and persona:
                msg_exito += f"\nPersona: {persona.nombre} {persona.apellido}"
                if abono_vigente:
                    estado = abono_vigente.estado()
                    msg_exito += f"\nAbono: {estado.value.upper()}"
                    if estado.value == 'vigente':
                        msg_exito += " ✅"
                    elif estado.value == 'por_vencer':
                        msg_exito += " ⚠"
                    else:
                        msg_exito += " ❌"
            
            # Actualizar contador
            abiertos = self.movimientos_repo.listar_abiertos()
            ocupadas = len(abiertos)
            msg_exito += f"\nOcupadas: {ocupadas}/{self.config.capacidad}"
            
            return True, msg_exito, resultado
            
        except Exception as e:
            return False, f"Error al registrar ingreso: {e}", None
    
    def obtener_estado_estacionamiento(self) -> dict:
        """
        Obtiene el estado actual del estacionamiento
        """
        abiertos = self.movimientos_repo.listar_abiertos()
        fichas_ocupadas = [int(mov.get('ficha', 0)) for mov in abiertos]
        ocupadas = len(fichas_ocupadas)
        disponibles = self.config.capacidad - ocupadas
        porcentaje_ocupacion = (ocupadas / self.config.capacidad) * 100 if self.config.capacidad > 0 else 0
        
        fichas_libres = [i for i in range(1, self.config.capacidad + 1) if i not in fichas_ocupadas]
        
        return {
            "capacidad": self.config.capacidad,
            "ocupadas": ocupadas,
            "disponibles": disponibles,
            "fichas_ocupadas": sorted(fichas_ocupadas),
            "fichas_libres": fichas_libres,
            "porcentaje_ocupacion": porcentaje_ocupacion,
            "estado": "COMPLETO" if disponibles == 0 else "DISPONIBLE"
        }
    
    def buscar_movimiento_por_ficha(self, nro_ficha: int) -> Optional[dict]:
        """
        Busca movimiento abierto por número de ficha
        """
        return self.movimientos_repo.obtener_abierto_por_ficha(nro_ficha)
