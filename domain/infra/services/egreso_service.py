from datetime import datetime
from domain.models import Config
from domain.enums import ReglaEleccionMonto
from domain.infra.movimientos_repo import MovimientosRepo, TS_FMT
from .tarificador import Tarificador

class EgresoService:
    def __init__(self, cfg: Config, movs: MovimientosRepo, tarificador: Tarificador):
        self.cfg = cfg
        self.movs = movs
        self.tarificador = tarificador

    def cerrar(self, ficha_id: int, usuario: str):
        abierto = self.movs.obtener_abierto_por_ficha(ficha_id)
        if not abierto:
            raise ValueError(f"La ficha {ficha_id} no tiene movimiento abierto.")
        entrada = datetime.strptime(abierto["hora_entrada"], TS_FMT)
        salida = datetime.now()
        minutos = int((salida - entrada).total_seconds()//60)

        # abono vigente al ingreso => $0 (si política activa)
        if abierto.get("abonado_vigente_al_ingreso") and self.cfg.cubre_hasta_egreso_si_vencia_durante_estadia:
            monto = 0.0
            detalle = {"motivo":"abonado", "candidatos": {"abonado": 0.0}}
        else:
            det = self.tarificador.calcular(entrada, salida)
            monto = det.monto_final
            detalle = {"motivo": det.motivo, "candidatos": det.candidatos}

        out = self.movs.cerrar(ficha=ficha_id, monto=monto, minutos=minutos, detalle_tarifa=detalle, usuario=usuario)
        return {"ok": True, "minutos": minutos, "monto": monto, "detalle_tarifa": detalle, "registro": out}
