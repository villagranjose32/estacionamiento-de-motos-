from typing import Optional
from domain.models import Config
from domain.infra.abonos_repo import AbonosRepo
from domain.infra.movimientos_repo import MovimientosRepo

class IngresoService:
    def __init__(self, cfg: Config, abonos: AbonosRepo, movs: MovimientosRepo):
        self.cfg = cfg
        self.abonos = abonos
        self.movs = movs

    def abrir(self, ficha_id: int, dni: Optional[str], usuario: str):
        if ficha_id < 1 or ficha_id > self.cfg.capacidad:
            raise ValueError(f"Ficha fuera de rango (1..{self.cfg.capacidad})")
        if self.movs.obtener_abierto_por_ficha(ficha_id):
            raise ValueError(f"La ficha {ficha_id} ya está adentro.")
        abonado_vigente = False
        if dni:
            ab = self.abonos.get_vigente_by_dni(dni)
            abonado_vigente = bool(ab)
        rec = self.movs.abrir(ficha=ficha_id, dni=dni, abonado_vigente=abonado_vigente, usuario=usuario)
        return {"ok": True, "mensaje": f"Ficha {ficha_id} ingresada {rec['hora_entrada']}"}
