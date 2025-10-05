import os, json, tempfile
from datetime import datetime
from typing import List, Dict, Optional
from .paths import SedePaths

TS_FMT = "%Y-%m-%d %H:%M"

class MovimientosRepo:
    def __init__(self, paths: SedePaths):
        self.paths = paths
        if not os.path.exists(paths.mov_abiertos):
            open(paths.mov_abiertos, "a", encoding="utf-8").close()

    def listar_abiertos(self) -> List[Dict]:
        out = []
        with open(self.paths.mov_abiertos, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line: continue
                try:
                    out.append(json.loads(line))
                except Exception:
                    # ignorar líneas corruptas
                    pass
        return out

    def obtener_abierto_por_ficha(self, ficha: int) -> Optional[Dict]:
        for m in self.listar_abiertos():
            if int(m.get("ficha")) == ficha:
                return m
        return None

    def abrir(self, ficha: int, dni: Optional[str], abonado_vigente: bool, usuario: str):
        rec = {
            "ficha": int(ficha),
            "hora_entrada": datetime.now().strftime(TS_FMT),
            "dni": dni or None,
            "abonado_vigente_al_ingreso": bool(abonado_vigente),
            "usuario": usuario
        }
        with open(self.paths.mov_abiertos, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        return rec

    def cerrar(self, ficha: int, monto: float, minutos: int, detalle_tarifa: Dict, usuario: str) -> Dict:
        # Obtener los movimientos abiertos
        abiertos = self.listar_abiertos()
        # Encontrar el movimiento específico que se está cerrando
        cerrado = next((m for m in abiertos if int(m["ficha"]) == int(ficha)), None)
        
        # Verificar que el movimiento existe
        if not cerrado:
            raise ValueError(f"No se puede cerrar la ficha {ficha} porque no tiene un registro de ingreso")
        
        # Filtrar la lista de abiertos para quitar el que se cierra
        nuevo_abiertos = [m for m in abiertos if int(m["ficha"]) != int(ficha)]
        self._rewrite_atomic(self.paths.mov_abiertos, nuevo_abiertos)
        
        # Agregar a cerrados YYYYMM
        ahora = datetime.now()
        out = {
            "ficha": int(ficha),
            "entrada": cerrado.get("hora_entrada"),
            "salida": ahora.strftime(TS_FMT),
            "minutos": int(minutos),
            "monto": float(monto),
            "motivo": detalle_tarifa.get("motivo"),
            "dni": cerrado.get("dni"),
            "abonado": bool(cerrado.get("abonado_vigente_al_ingreso")),
            "usuario_cierre": usuario
        }
        path_cerrados = self.paths.mov_cerrados_mes(ahora)
        with open(path_cerrados, "a", encoding="utf-8") as f:
            f.write(json.dumps(out, ensure_ascii=False) + "\n")
        return out

    def _rewrite_atomic(self, path: str, records: List[Dict]):
        fd, tmp = tempfile.mkstemp(prefix="tmp_", dir=os.path.dirname(path))
        os.close(fd)
        try:
            with open(tmp, "w", encoding="utf-8") as f:
                for r in records:
                    f.write(json.dumps(r, ensure_ascii=False) + "\n")
            os.replace(tmp, path)
        finally:
            try:
                if os.path.exists(tmp): os.remove(tmp)
            except Exception:
                pass
