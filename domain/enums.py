from enum import Enum

class DiaSemana(str, Enum):
    LUNES = "lunes"
    MARTES = "martes"
    MIERCOLES = "miercoles"
    JUEVES = "jueves"
    VIERNES = "viernes"
    SABADO = "sabado"
    DOMINGO = "domingo"

class EstadoMovimiento(str, Enum):
    DENTRO = "dentro"
    CERRADO = "cerrado"

class ReglaEleccionMonto(str, Enum):
    MAS_BARATO = "mas_barato"
    PRIORIDAD = "prioridad"

class RedondeoTurno(str, Enum):
    ENTERO = "entero"
    PROPORCIONAL = "proporcional"   # (MVP implementa ENTERO)

class ExcesoTurno(str, Enum):
    MAS_BARATO = "mas_barato"
    PRORRATEAR_FRACCION = "prorratear_por_fraccion"  # (MVP: mas_barato)
    SEGUNDO_TURNO = "segundo_turno"
    DIARIA = "diaria"

class EstadoAbono(str, Enum):
    VIGENTE = "vigente"
    POR_VENCER = "por_vencer"
    VENCIDO = "vencido"
    FUTURO = "futuro"
    INACTIVO = "inactivo"

class MedioPago(str, Enum):
    EFECTIVO = "efectivo"
    TARJETA_DEBITO = "tarjeta_debito"
    TARJETA_CREDITO = "tarjeta_credito"
    TRANSFERENCIA = "transferencia"
    MERCADO_PAGO = "mercado_pago"
    OTRO = "otro"

class TipoFicha(str, Enum):
    LIBRE = "libre"
    OCUPADA = "ocupada"
    FUERA_DE_SERVICIO = "fuera_de_servicio"
