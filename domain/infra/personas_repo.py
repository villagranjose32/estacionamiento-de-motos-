import os
import csv
import tempfile
import shutil
from typing import List, Optional
from datetime import datetime
from ..models import Persona
from .paths import SedePaths


class PersonasRepo:
    def __init__(self, paths: SedePaths):
        self.paths = paths
        self.archivo = paths.personas_txt
        self._asegurar_directorio()
    
    def _asegurar_directorio(self):
        """Crea el directorio si no existe"""
        directorio = os.path.dirname(self.archivo)
        if directorio and not os.path.exists(directorio):
            os.makedirs(directorio)
    
    def _escritura_atomica(self, personas: List[Persona]):
        """Escritura atómica usando archivo temporal"""
        directorio = os.path.dirname(self.archivo)
        
        with tempfile.NamedTemporaryFile(mode='w', dir=directorio, delete=False, 
                                       suffix='.tmp', encoding='utf-8', newline='') as tmp:
            writer = csv.writer(tmp, delimiter=';')
            # Escribir header
            writer.writerow(['dni', 'nombre', 'apellido', 'telefono', 'email', 'fecha_alta'])
            
            # Escribir datos
            for persona in personas:
                writer.writerow([
                    persona.dni,
                    persona.nombre,
                    persona.apellido,
                    persona.telefono or '',
                    persona.email or '',
                    persona.fecha_alta.isoformat() if persona.fecha_alta else ''
                ])
            tmp_path = tmp.name
        
        # Renombrar atómicamente
        shutil.move(tmp_path, self.archivo)
    
    def cargar_todas(self) -> List[Persona]:
        """Carga todas las personas desde el archivo"""
        if not os.path.exists(self.archivo):
            return []
        
        personas = []
        try:
            with open(self.archivo, 'r', encoding='utf-8', newline='') as f:
                reader = csv.reader(f, delimiter=';')
                header = next(reader, None)  # Saltar header
                
                for fila in reader:
                    try:
                        if len(fila) < 6:
                            continue  # Línea corrupta
                        
                        dni, nombre, apellido, telefono, email, fecha_alta_str = fila
                        
                        fecha_alta = None
                        if fecha_alta_str:
                            fecha_alta = datetime.fromisoformat(fecha_alta_str)
                        
                        persona = Persona(
                            dni=dni.strip(),
                            nombre=nombre.strip(),
                            apellido=apellido.strip(),
                            telefono=telefono.strip() if telefono.strip() else None,
                            email=email.strip() if email.strip() else None,
                            fecha_alta=fecha_alta
                        )
                        personas.append(persona)
                    
                    except (ValueError, IndexError) as e:
                        # Línea corrupta, continuar
                        print(f"Línea corrupta en personas.txt: {fila} - {e}")
                        continue
        
        except Exception as e:
            print(f"Error al cargar personas: {e}")
        
        return personas
    
    def buscar_por_dni(self, dni: str) -> Optional[Persona]:
        """Busca una persona por DNI"""
        personas = self.cargar_todas()
        for persona in personas:
            if persona.dni == dni:
                return persona
        return None
    
    def existe_dni(self, dni: str) -> bool:
        """Verifica si existe una persona con el DNI dado"""
        return self.buscar_por_dni(dni) is not None
    
    def agregar(self, persona: Persona) -> bool:
        """Agrega una nueva persona"""
        if self.existe_dni(persona.dni):
            return False
        
        personas = self.cargar_todas()
        personas.append(persona)
        self._escritura_atomica(personas)
        return True
    
    def actualizar(self, persona: Persona) -> bool:
        """Actualiza una persona existente"""
        personas = self.cargar_todas()
        for i, p in enumerate(personas):
            if p.dni == persona.dni:
                personas[i] = persona
                self._escritura_atomica(personas)
                return True
        return False
    
    def eliminar(self, dni: str) -> bool:
        """Elimina una persona por DNI"""
        personas = self.cargar_todas()
        personas_filtradas = [p for p in personas if p.dni != dni]
        
        if len(personas_filtradas) < len(personas):
            self._escritura_atomica(personas_filtradas)
            return True
        return False
    
    def buscar_por_texto(self, texto: str) -> List[Persona]:
        """Busca personas por nombre, apellido o DNI"""
        personas = self.cargar_todas()
        texto = texto.lower()
        
        resultado = []
        for persona in personas:
            if (texto in persona.dni.lower() or 
                texto in persona.nombre.lower() or 
                texto in persona.apellido.lower()):
                resultado.append(persona)
        
        return resultado
