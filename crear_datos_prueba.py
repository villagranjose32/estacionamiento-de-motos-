#!/usr/bin/env python3
"""Script para crear datos de prueba del sistema"""

import sys
import os
from datetime import date, datetime, timedelta

# Agregar path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from domain.infra.paths import SedePaths
from domain.infra.personas_repo import PersonasRepo
from domain.infra.abonos_repo import AbonosRepo
from domain.models import Persona, Abono

def crear_datos_prueba():
    # Configurar paths (usando detección automática)
    paths = SedePaths()
    print(f"Usando directorio de datos: {paths.root}")
    
    # Repositorios
    personas_repo = PersonasRepo(paths)
    abonos_repo = AbonosRepo(paths)
    
    print("Creando datos de prueba...")
    
    # Personas de prueba
    personas = [
        Persona(dni="12345678", nombre="Juan", apellido="Pérez", telefono="555-0001", email="juan@email.com"),
        Persona(dni="87654321", nombre="María", apellido="González", telefono="555-0002", email="maria@email.com"),
        Persona(dni="11111111", nombre="Carlos", apellido="López", telefono="555-0003"),
        Persona(dni="22222222", nombre="Ana", apellido="Martínez", telefono="555-0004"),
        Persona(dni="33333333", nombre="Luis", apellido="Rodríguez"),
    ]
    
    # Agregar personas
    for persona in personas:
        if personas_repo.agregar(persona):
            print(f"✓ Persona agregada: {persona.nombre} {persona.apellido} (DNI: {persona.dni})")
        else:
            print(f"⚠ Persona ya existe: {persona.dni}")
    
    # Crear abonos de prueba
    hoy = date.today()
    
    abonos = [
        # Abono vigente
        Abono(
            id=abonos_repo.generar_id_abono(),
            dni_persona="12345678",
            fecha_inicio=hoy - timedelta(days=10),
            fecha_fin=hoy + timedelta(days=20),
            precio=15000.0
        ),
        # Abono por vencer
        Abono(
            id=abonos_repo.generar_id_abono(),
            dni_persona="87654321",
            fecha_inicio=hoy - timedelta(days=20),
            fecha_fin=hoy + timedelta(days=3),
            precio=15000.0
        ),
        # Abono vencido
        Abono(
            id=abonos_repo.generar_id_abono(),
            dni_persona="11111111",
            fecha_inicio=hoy - timedelta(days=40),
            fecha_fin=hoy - timedelta(days=5),
            precio=15000.0
        ),
    ]
    
    # Agregar abonos
    for abono in abonos:
        if abonos_repo.agregar_abono(abono):
            estado = abono.estado()
            print(f"✓ Abono agregado: {abono.dni_persona} - Estado: {estado.value}")
    
    print("\n¡Datos de prueba creados exitosamente!")
    print("\nPuedes probar el sistema con:")
    print("- DNI 12345678 (Juan Pérez) - Abono VIGENTE")
    print("- DNI 87654321 (María González) - Abono POR VENCER")
    print("- DNI 11111111 (Carlos López) - Abono VENCIDO")
    print("- DNI 22222222 (Ana Martínez) - Sin abono")
    print("- DNI 33333333 (Luis Rodríguez) - Sin abono")

if __name__ == "__main__":
    crear_datos_prueba()
