import os
import csv
import tempfile
import shutil
from typing import List, Optional, Dict
from datetime import datetime, date
from ..models import Abono, PagoAbono
from ..enums import EstadoAbono, MedioPago
from .paths import SedePaths


class AbonosRepo:
    """
    Repositorio para abonos y pagos con persistencia CSV
    """
    def __init__(self, paths: SedePaths):
        self.paths = paths
        self.archivo_abonos = paths.abonos_txt
        self.archivo_pagos = getattr(paths, 'pagos_abono_txt', paths.abonos_txt.replace('.txt', '_pagos.txt'))
        self._init_files()
    
    def _init_files(self):
        """Inicializa archivos CSV si no existen"""
        if not os.path.exists(self.archivo_abonos):
            os.makedirs(os.path.dirname(self.archivo_abonos), exist_ok=True)
            with open(self.archivo_abonos, "w", encoding="utf-8", newline="") as f:
                w = csv.writer(f, delimiter=";")
                w.writerow(["id", "dni_persona", "fecha_inicio", "fecha_fin", "precio", "fecha_alta", "activo"])
        
        if not os.path.exists(self.archivo_pagos):
            os.makedirs(os.path.dirname(self.archivo_pagos), exist_ok=True)
            with open(self.archivo_pagos, "w", encoding="utf-8", newline="") as f:
                w = csv.writer(f, delimiter=";")
                w.writerow(["id", "abono_id", "monto", "medio_pago", "comprobante", "fecha_pago", "observaciones"])
    
    def _escritura_atomica_abonos(self, abonos: List[Abono]):
        """Escritura atómica para abonos"""
        directorio = os.path.dirname(self.archivo_abonos)
        
        with tempfile.NamedTemporaryFile(mode='w', dir=directorio, delete=False, 
                                       suffix='.tmp', encoding='utf-8', newline='') as tmp:
            writer = csv.writer(tmp, delimiter=';')
            writer.writerow(['id', 'dni_persona', 'fecha_inicio', 'fecha_fin', 'precio', 'fecha_alta', 'activo'])
            
            for abono in abonos:
                writer.writerow([
                    abono.id,
                    abono.dni_persona,
                    abono.fecha_inicio.isoformat(),
                    abono.fecha_fin.isoformat(),
                    str(abono.precio),
                    abono.fecha_alta.isoformat() if abono.fecha_alta else '',
                    'si' if abono.activo else 'no'
                ])
            tmp_path = tmp.name
        
        shutil.move(tmp_path, self.archivo_abonos)
    
    def cargar_abonos(self) -> List[Abono]:
        """Carga todos los abonos"""
        abonos = []
        try:
            with open(self.archivo_abonos, 'r', encoding='utf-8', newline='') as f:
                reader = csv.reader(f, delimiter=';')
                header = next(reader, None)
                
                for fila in reader:
                    try:
                        if len(fila) < 7:
                            continue
                        
                        id_abono, dni, fecha_inicio_str, fecha_fin_str, precio_str, fecha_alta_str, activo_str = fila
                        
                        fecha_inicio = date.fromisoformat(fecha_inicio_str)
                        fecha_fin = date.fromisoformat(fecha_fin_str)
                        precio = float(precio_str)
                        
                        fecha_alta = None
                        if fecha_alta_str:
                            fecha_alta = datetime.fromisoformat(fecha_alta_str)
                        
                        activo = activo_str.lower() in ['si', 'true', '1']
                        
                        abono = Abono(
                            id=id_abono,
                            dni_persona=_canon_dni(dni),
                            fecha_inicio=fecha_inicio,
                            fecha_fin=fecha_fin,
                            precio=precio,
                            fecha_alta=fecha_alta,
                            activo=activo
                        )
                        abonos.append(abono)
                    
                    except (ValueError, IndexError) as e:
                        print(f"Línea corrupta en abonos.txt: {fila} - {e}")
                        continue
        
        except Exception as e:
            print(f"Error al cargar abonos: {e}")
        
        return abonos
    
    def get_vigente_by_dni(self, dni: str) -> Optional[Dict]:
        """Método de compatibilidad - retorna diccionario"""
        dni = _canon_dni(dni)
        abonos = self.cargar_abonos()
        today = date.today()
        
        for abono in abonos:
            if abono.dni_persona == dni and abono.activo:
                estado = abono.estado()
                if estado in [EstadoAbono.VIGENTE, EstadoAbono.POR_VENCER]:
                    return {
                        "dni": abono.dni_persona,
                        "fecha_inicio": abono.fecha_inicio.isoformat(),
                        "fecha_fin": abono.fecha_fin.isoformat(),
                        "estado": estado.value,
                        "observaciones": ""
                    }
        return None
    
    def abono_vigente_por_dni(self, dni: str, dias_alerta: int = 7) -> Optional[Abono]:
        """Busca un abono vigente para un DNI"""
        dni = _canon_dni(dni)
        abonos = self.cargar_abonos()
        
        for abono in abonos:
            if abono.dni_persona == dni and abono.activo:
                estado = abono.estado(dias_alerta)
                if estado in [EstadoAbono.VIGENTE, EstadoAbono.POR_VENCER]:
                    return abono
        return None
    
    def buscar_abonos_por_dni(self, dni: str) -> List[Abono]:
        """Busca todos los abonos de un DNI"""
        dni = _canon_dni(dni)
        abonos = self.cargar_abonos()
        return [abono for abono in abonos if abono.dni_persona == dni]
    
    def generar_id_abono(self) -> str:
        """Genera ID único para abono"""
        abonos = self.cargar_abonos()
        if not abonos:
            return "ABN001"
        
        max_num = 0
        for abono in abonos:
            if abono.id.startswith("ABN"):
                try:
                    num = int(abono.id[3:])
                    max_num = max(max_num, num)
                except ValueError:
                    continue
        
        return f"ABN{max_num + 1:03d}"
    
    def agregar_abono(self, abono: Abono) -> bool:
        """Agrega un nuevo abono"""
        abonos = self.cargar_abonos()
        abonos.append(abono)
        self._escritura_atomica_abonos(abonos)
        return True
    
    def listar_por_vencer(self, dias: int = 7) -> List[Abono]:
        """Lista abonos que vencen en X días"""
        abonos = self.cargar_abonos()
        return [abono for abono in abonos if abono.estado(dias) == EstadoAbono.POR_VENCER]
    
    def listar_vencidos(self) -> List[Abono]:
        """Lista abonos vencidos"""
        abonos = self.cargar_abonos()
        return [abono for abono in abonos if abono.estado() == EstadoAbono.VENCIDO]


def _canon_dni(s: str) -> str:
    """Canonicaliza DNI removiendo caracteres no numéricos"""
    return "".join(ch for ch in s if ch.isdigit())

def _parse_date(s: str):
    """Parsea fecha desde string"""
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except Exception:
        return None
