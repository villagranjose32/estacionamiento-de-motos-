import os, csv
from datetime import time
from typing import List, Optional
from domain.models import Turno
from .paths import SedePaths

DEFAULT_TURNOS = [
    ("Mañana", "06:00", "12:00", "2500.00", "L,M,X,J,V,S,D", "1"),
    ("Tarde",  "12:00", "18:00", "2500.00", "L,M,X,J,V,S,D", "1"),
    ("Noche",  "18:00", "06:00", "3000.00", "L,M,X,J,V,S,D", "1"),
]

class TurnosRepo:
    def __init__(self, paths: SedePaths):
        self.paths = paths

    def load_or_create_defaults(self) -> List[Turno]:
        if not os.path.exists(self.paths.turnos_txt):
            self._write_defaults()
        return self._read()
    
    def load_all(self) -> List[Turno]:
        """Alias para compatibilidad"""
        return self.load_or_create_defaults()

    def _write_defaults(self):
        os.makedirs(os.path.dirname(self.paths.turnos_txt), exist_ok=True)
        with open(self.paths.turnos_txt, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f, delimiter=";")
            w.writerow(["nombre","hora_inicio","hora_fin","precio","dias","activo"])
            for row in DEFAULT_TURNOS:
                w.writerow(row)

    def _read(self) -> List[Turno]:
        out = []
        try:
            with open(self.paths.turnos_txt, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f, delimiter=";")
                for r in reader:
                    try:
                        dias = r["dias"].strip()
                        dias_list: Optional[List[str]] = None if not dias else [d.strip() for d in dias.split(",")]
                        out.append(Turno(
                            nombre=r["nombre"].strip(),
                            hora_inicio=_parse_time(r["hora_inicio"].strip()),
                            hora_fin=_parse_time(r["hora_fin"].strip()),
                            precio=float(r["precio"]),
                            dias=dias_list,
                            activo=(r.get("activo","1").strip() in ("1","true","si","sí"))
                        ))
                    except Exception as e:
                        print(f"Error procesando turno: {r} - {e}")
                        continue
        except Exception as e:
            print(f"Error leyendo turnos: {e}")
        return out

def _parse_time(hhmm: str) -> time:
    h, m = hhmm.split(":")
    return time(int(h), int(m))
