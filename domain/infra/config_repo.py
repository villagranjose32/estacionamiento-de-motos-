import os
import tempfile
import shutil
from typing import Dict
from ..models import Config
from ..enums import ReglaEleccionMonto, RedondeoTurno, ExcesoTurno
from .paths import SedePaths

BOOL = {"si": True, "sí": True, "true": True, "1": True, "no": False, "false": False, "0": False}

DEFAULTS = {
    "nombre": "Estacionamiento Centro",
    "capacidad": "120",
    "gracia_min": "10",
    "fraccion_min": "30",
    "precio_por_fraccion": "500.00",
    "aplica_tarifa_diaria": "si",
    "umbral_diaria_horas": "12",
    "tarifa_diaria": "6000.00",
    "aplica_tarifa_por_turno": "si",
    "redondeo_turno": "entero",
    "exceso_turno": "mas_barato",
    "regla_eleccion_monto": "mas_barato",
    "prioridad_precio": "turno>diaria>fraccion",
    "cubre_hasta_egreso_si_vencia_durante_estadia": "si",
    "dias_alerta_vencimiento": "7",
}

class ConfigRepo:
    def __init__(self, paths: SedePaths):
        self.paths = paths

    def load_or_create_defaults(self) -> Config:
        if not os.path.exists(self.paths.config_txt):
            self._write_atomic(DEFAULTS)
        raw = self._read()
        return self._to_model(raw)

    def save(self, config: Config):
        """Guarda configuración usando escritura atómica"""
        kv = self._from_model(config)
        self._write_atomic(kv)

    def _read(self) -> Dict[str, str]:
        out = {}
        try:
            with open(self.paths.config_txt, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    try:
                        k, v = line.split("=", 1)
                        out[k.strip()] = v.strip()
                    except ValueError:
                        # Línea corrupta, continuar
                        continue
        except Exception as e:
            print(f"Error al leer configuración: {e}")
        
        return {**DEFAULTS, **out}

    def _write_atomic(self, kv: Dict[str, str]):
        """Escritura atómica usando archivo temporal"""
        directorio = os.path.dirname(self.paths.config_txt)
        os.makedirs(directorio, exist_ok=True)
        
        with tempfile.NamedTemporaryFile(mode='w', dir=directorio, delete=False, 
                                       suffix='.tmp', encoding='utf-8') as tmp:
            tmp.write("# Configuración del Sistema de Estacionamiento\n")
            tmp.write("# Archivo generado automáticamente\n\n")
            for k, v in kv.items():
                tmp.write(f"{k}={v}\n")
            tmp_path = tmp.name
        
        # Renombrar atómicamente
        shutil.move(tmp_path, self.paths.config_txt)

    def _to_bool(self, s: str) -> bool:
        return BOOL.get(s.lower(), False)

    def _to_model(self, raw: Dict[str, str]) -> Config:
        return Config(
            nombre=raw["nombre"],
            capacidad=int(raw["capacidad"]),
            gracia_min=int(raw["gracia_min"]),
            fraccion_min=int(raw["fraccion_min"]),
            precio_por_fraccion=float(raw["precio_por_fraccion"]),
            aplica_tarifa_diaria=self._to_bool(raw["aplica_tarifa_diaria"]),
            umbral_diaria_horas=int(raw["umbral_diaria_horas"]),
            tarifa_diaria=float(raw["tarifa_diaria"]),
            aplica_tarifa_por_turno=self._to_bool(raw["aplica_tarifa_por_turno"]),
            redondeo_turno=RedondeoTurno(raw["redondeo_turno"]),
            exceso_turno=ExcesoTurno(raw["exceso_turno"]),
            regla_eleccion_monto=ReglaEleccionMonto(raw["regla_eleccion_monto"]),
            prioridad_precio=raw["prioridad_precio"],
            cubre_hasta_egreso_si_vencia_durante_estadia=self._to_bool(
                raw["cubre_hasta_egreso_si_vencia_durante_estadia"]
            ),
            dias_alerta_vencimiento=int(raw.get("dias_alerta_vencimiento", "7")),
        )

    def _from_model(self, config: Config) -> Dict[str, str]:
        """Convierte modelo a diccionario para persistencia"""
        return {
            "nombre": config.nombre,
            "capacidad": str(config.capacidad),
            "gracia_min": str(config.gracia_min),
            "fraccion_min": str(config.fraccion_min),
            "precio_por_fraccion": str(config.precio_por_fraccion),
            "aplica_tarifa_diaria": "si" if config.aplica_tarifa_diaria else "no",
            "umbral_diaria_horas": str(config.umbral_diaria_horas),
            "tarifa_diaria": str(config.tarifa_diaria),
            "aplica_tarifa_por_turno": "si" if config.aplica_tarifa_por_turno else "no",
            "redondeo_turno": config.redondeo_turno.value,
            "exceso_turno": config.exceso_turno.value,
            "regla_eleccion_monto": config.regla_eleccion_monto.value,
            "prioridad_precio": config.prioridad_precio,
            "cubre_hasta_egreso_si_vencia_durante_estadia": "si" if config.cubre_hasta_egreso_si_vencia_durante_estadia else "no",
            "dias_alerta_vencimiento": str(config.dias_alerta_vencimiento),
        }
