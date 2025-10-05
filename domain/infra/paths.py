import os
import sys
from datetime import datetime
from pathlib import Path
try:
    from appdirs import user_data_dir
except ImportError:
    # Fallback si appdirs no está instalado
    user_data_dir = None

def get_default_data_path():
    """Obtiene la ruta de datos predeterminada, con soporte para portabilidad"""
    # Primero intentamos usar appdirs para ubicaciones específicas del sistema operativo
    if user_data_dir:
        app_name = "SistemaEstacionamiento"
        app_author = "Parking"
        return os.path.join(user_data_dir(app_name, app_author))
    
    # Fallback a la ubicación tradicional
    if getattr(sys, 'frozen', False):
        # Si es un ejecutable congelado (PyInstaller)
        app_path = os.path.dirname(sys.executable)
    else:
        # Si es un script Python normal
        app_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    
    # Usar subdirectorio 'data' en la carpeta del ejecutable/script
    return os.path.join(app_path, "data")

class SedePaths:
    def __init__(self, data_root: str = None, sede: str = "default"):
        # Si no se proporciona una ruta, usar la ruta predeterminada
        if data_root is None:
            data_root = get_default_data_path()
        
        self.root = os.path.abspath(data_root)
        self.sede = sede
        self.sede_dir = os.path.join(self.root, sede)
        os.makedirs(self.sede_dir, exist_ok=True)

    @property
    def config_txt(self): return os.path.join(self.sede_dir, "config.txt")
    @property
    def turnos_txt(self): return os.path.join(self.sede_dir, "turnos.txt")
    @property
    def personas_txt(self): return os.path.join(self.sede_dir, "personas.txt")
    @property
    def abonos_txt(self): return os.path.join(self.sede_dir, "abonos.txt")
    @property
    def pagos_abono_txt(self): return os.path.join(self.sede_dir, "pagos_abono.txt")
    @property
    def mov_abiertos(self): return os.path.join(self.sede_dir, "movimientos_abiertos.txt")
    @property
    def movimientos_abiertos_txt(self): return self.mov_abiertos

    def mov_cerrados_mes(self, dt=None):
        dt = dt or datetime.now()
        fname = f"movimientos_cerrados_{dt:%Y%m}.txt"
        return os.path.join(self.sede_dir, fname)
