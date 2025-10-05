from dataclasses import dataclass
from datetime import datetime, time, date
from typing import Optional, List, Dict
from .enums import ReglaEleccionMonto, RedondeoTurno, ExcesoTurno, EstadoAbono, MedioPago

@dataclass
class Config:
    nombre: str = "Estacionamiento"
    capacidad: int = 120
    gracia_min: int = 10
    fraccion_min: int = 30
    precio_por_fraccion: float = 500.0
    aplica_tarifa_diaria: bool = True
    umbral_diaria_horas: int = 12
    tarifa_diaria: float = 6000.0
    aplica_tarifa_por_turno: bool = True
    redondeo_turno: RedondeoTurno = RedondeoTurno.ENTERO
    exceso_turno: ExcesoTurno = ExcesoTurno.MAS_BARATO
    regla_eleccion_monto: ReglaEleccionMonto = ReglaEleccionMonto.MAS_BARATO
    prioridad_precio: str = "turno>diaria>fraccion"
    cubre_hasta_egreso_si_vencia_durante_estadia: bool = True
    dias_alerta_vencimiento: int = 7

@dataclass(frozen=True)
class Turno:
    nombre: str
    hora_inicio: time
    hora_fin: time
    precio: float
    dias: Optional[List[str]]  # ['L','M','X','J','V','S','D'] o None= todos
    activo: bool = True

@dataclass
class Persona:
    dni: str
    nombre: str
    apellido: str
    telefono: Optional[str] = None
    email: Optional[str] = None
    fecha_alta: Optional[datetime] = None
    
    def __post_init__(self):
        if self.fecha_alta is None:
            self.fecha_alta = datetime.now()

@dataclass
class Abono:
    id: str  # Único
    dni_persona: str
    fecha_inicio: date
    fecha_fin: date
    precio: float
    fecha_alta: Optional[datetime] = None
    activo: bool = True
    
    def __post_init__(self):
        if self.fecha_alta is None:
            self.fecha_alta = datetime.now()
    
    def estado(self, dias_alerta: int = 7) -> EstadoAbono:
        hoy = date.today()
        if not self.activo:
            return EstadoAbono.INACTIVO
        if hoy < self.fecha_inicio:
            return EstadoAbono.FUTURO
        if hoy > self.fecha_fin:
            return EstadoAbono.VENCIDO
        # Verificar si está por vencer
        dias_restantes = (self.fecha_fin - hoy).days
        if dias_restantes <= dias_alerta:
            return EstadoAbono.POR_VENCER
        return EstadoAbono.VIGENTE

@dataclass
class PagoAbono:
    id: str
    abono_id: str
    monto: float
    medio_pago: MedioPago
    comprobante: Optional[str] = None
    fecha_pago: Optional[datetime] = None
    observaciones: Optional[str] = None
    
    def __post_init__(self):
        if self.fecha_pago is None:
            self.fecha_pago = datetime.now()

@dataclass
class Movimiento:
    nro_ficha: int
    fecha_entrada: datetime
    dni_abonado: Optional[str] = None
    fecha_salida: Optional[datetime] = None
    monto_cobrado: Optional[float] = None
    detalle_tarifa: Optional[str] = None
    observaciones: Optional[str] = None
    
    @property
    def esta_abierto(self) -> bool:
        return self.fecha_salida is None
    
    @property
    def duracion_minutos(self) -> Optional[int]:
        if self.fecha_salida is None:
            return None
        return int((self.fecha_salida - self.fecha_entrada).total_seconds() // 60)

@dataclass
class DetalleTarifa:
    monto_final: float
    motivo: str  # 'fraccion' | 'diaria' | 'turno'
    candidatos: dict
    es_abonado: bool = False
    dni_abonado: Optional[str] = None
    estado_abono: Optional[EstadoAbono] = None
