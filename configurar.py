#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de configuración para el Sistema de Gestión de Estacionamiento
Este script configura el entorno necesario para ejecutar el sistema
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

def print_header(texto):
    """Imprime un encabezado con formato"""
    print("\n" + "=" * 80)
    print(f" {texto} ".center(80, "="))
    print("=" * 80 + "\n")

def check_python_version():
    """Verifica que la versión de Python sea compatible"""
    print_header("VERIFICANDO VERSIÓN DE PYTHON")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Versión de Python detectada: {version.major}.{version.minor}")
        print("❌ Se requiere Python 3.8 o superior")
        return False
    
    print(f"✅ Versión de Python compatible: {version.major}.{version.minor}.{version.micro}")
    return True

def create_venv():
    """Crea un entorno virtual para el proyecto"""
    print_header("CREANDO ENTORNO VIRTUAL")
    
    # Determinar la ruta del proyecto
    project_dir = os.path.dirname(os.path.abspath(__file__))
    venv_dir = os.path.join(project_dir, ".venv")
    
    # Verificar si el entorno virtual ya existe
    if os.path.exists(venv_dir):
        print(f"ℹ️ El entorno virtual ya existe en: {venv_dir}")
        respuesta = input("¿Desea recrearlo? (s/N): ").strip().lower()
        if respuesta == 's':
            print("Eliminando entorno virtual existente...")
            shutil.rmtree(venv_dir)
        else:
            print("Usando entorno virtual existente.")
            return venv_dir
    
    print(f"Creando entorno virtual en: {venv_dir}")
    
    try:
        # Crear entorno virtual
        subprocess.run([sys.executable, "-m", "venv", venv_dir], check=True)
        print("✅ Entorno virtual creado exitosamente")
        return venv_dir
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al crear entorno virtual: {e}")
        print("Intente ejecutar manualmente: python -m venv .venv")
        return None
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return None

def install_dependencies(venv_dir):
    """Instala las dependencias necesarias"""
    print_header("INSTALANDO DEPENDENCIAS")
    
    if not venv_dir or not os.path.exists(venv_dir):
        print("❌ El entorno virtual no existe")
        return False
    
    # Determinar el ejecutable de pip
    if platform.system() == "Windows":
        pip_path = os.path.join(venv_dir, "Scripts", "pip.exe")
    else:
        pip_path = os.path.join(venv_dir, "bin", "pip")
    
    if not os.path.exists(pip_path):
        print(f"❌ No se encontró pip en el entorno virtual: {pip_path}")
        return False
    
    try:
        # Instalar dependencias
        print("Instalando dependencias...")
        subprocess.run([pip_path, "install", "--upgrade", "pip"], check=True)
        subprocess.run([pip_path, "install", "tk"], check=True)
        
        try:
            print("Instalando appdirs (para portabilidad entre sistemas)...")
            subprocess.run([pip_path, "install", "appdirs"], check=True)
        except subprocess.CalledProcessError as e:
            print(f"⚠️ No se pudo instalar appdirs: {e}")
            print("El sistema seguirá funcionando, pero usará rutas relativas.")
        
        print("✅ Dependencias instaladas correctamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al instalar dependencias: {e}")
        return False

def create_data_directory():
    """Crea la estructura de directorios para los datos"""
    print_header("CONFIGURANDO DIRECTORIO DE DATOS")
    
    # Determinar la ruta del proyecto
    project_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(project_dir, "data")
    default_dir = os.path.join(data_dir, "default")
    
    # Crear directorio de datos si no existe
    os.makedirs(default_dir, exist_ok=True)
    
    # Verificar si existen los archivos de datos necesarios
    required_files = [
        "config.txt", "turnos.txt", "personas.txt", 
        "abonos.txt", "pagos_abono.txt", "movimientos_abiertos.txt"
    ]
    
    for file in required_files:
        file_path = os.path.join(default_dir, file)
        if not os.path.exists(file_path):
            # Crear archivo vacío
            with open(file_path, "w", encoding="utf-8") as f:
                if file == "config.txt":
                    f.write("nombre;capacidad;gracia_min;fraccion_min;precio_por_fraccion;aplica_tarifa_diaria;umbral_diaria_horas;tarifa_diaria;aplica_tarifa_por_turno;redondeo_turno;exceso_turno;regla_eleccion_monto;prioridad_precio;cubre_hasta_egreso_si_vencia_durante_estadia;dias_alerta_vencimiento\n")
                    f.write("Estacionamiento;120;10;30;500.0;si;12;6000.0;si;entero;mas_barato;mas_barato;turno>diaria>fraccion;si;7\n")
                elif file == "turnos.txt":
                    f.write("nombre;hora_inicio;hora_fin;precio;dias;activo\n")
                elif file == "personas.txt":
                    f.write("dni;nombre;apellido;telefono;email;fecha_alta\n")
                elif file == "abonos.txt":
                    f.write("id;dni_persona;fecha_inicio;fecha_fin;precio;fecha_alta;activo\n")
                elif file == "pagos_abono.txt":
                    f.write("id;abono_id;monto;medio_pago;comprobante;fecha_pago;observaciones\n")
    
    print(f"✅ Directorio de datos configurado en: {data_dir}")
    return True

def create_launcher():
    """Crea scripts de inicio para diferentes sistemas operativos"""
    print_header("CREANDO LANZADORES")
    
    # Determinar la ruta del proyecto
    project_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Crear script de inicio para Windows
    if platform.system() == "Windows":
        launcher_path = os.path.join(project_dir, "iniciar_estacionamiento.bat")
        with open(launcher_path, "w") as f:
            f.write("@echo off\n")
            f.write("echo Iniciando Sistema de Gestion de Estacionamiento...\n")
            f.write("echo.\n")
            f.write(f'cd /d "{project_dir}"\n')
            f.write('.venv\\Scripts\\python.exe main.py\n')
            f.write("if %ERRORLEVEL% neq 0 pause\n")
        
        print(f"✅ Lanzador para Windows creado: {launcher_path}")
    
    # Crear script de inicio para Linux/Mac
    else:
        launcher_path = os.path.join(project_dir, "iniciar_estacionamiento.sh")
        with open(launcher_path, "w") as f:
            f.write("#!/bin/bash\n")
            f.write('echo "Iniciando Sistema de Gestión de Estacionamiento..."\n')
            f.write("echo\n")
            f.write(f'cd "{project_dir}"\n')
            f.write('./.venv/bin/python main.py\n')
        
        # Hacer ejecutable el script
        os.chmod(launcher_path, 0o755)
        
        print(f"✅ Lanzador para Unix/Linux creado: {launcher_path}")
    
    return True

def create_readme():
    """Crea un archivo README con instrucciones"""
    print_header("CREANDO DOCUMENTACIÓN")
    
    # Determinar la ruta del proyecto
    project_dir = os.path.dirname(os.path.abspath(__file__))
    readme_path = os.path.join(project_dir, "README.md")
    
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write("# Sistema de Gestión de Estacionamiento\n\n")
        f.write("## Requisitos\n\n")
        f.write("- Python 3.8 o superior\n")
        f.write("- Bibliotecas incluidas en el entorno virtual\n\n")
        f.write("## Instalación\n\n")
        f.write("1. Ejecute el script `configurar.py` para configurar el entorno:\n\n")
        f.write("   ```\n")
        f.write("   python configurar.py\n")
        f.write("   ```\n\n")
        f.write("   Este script verificará la versión de Python, creará un entorno virtual,\n")
        f.write("   instalará las dependencias necesarias y configurará los directorios de datos.\n\n")
        f.write("2. Una vez completada la configuración, puede iniciar el sistema usando el lanzador creado:\n\n")
        f.write("   - En Windows: Ejecute `iniciar_estacionamiento.bat`\n")
        f.write("   - En Linux/Mac: Ejecute `./iniciar_estacionamiento.sh`\n\n")
        f.write("## Estructura de directorios\n\n")
        f.write("- `main.py`: Punto de entrada principal del sistema\n")
        f.write("- `domain/`: Módulos del dominio de la aplicación\n")
        f.write("  - `models.py`: Definición de las clases del modelo\n")
        f.write("  - `enums.py`: Definición de enumeraciones\n")
        f.write("  - `infra/`: Infraestructura y persistencia\n")
        f.write("    - `services/`: Servicios de negocio\n")
        f.write("- `ventana_operacion.py`: Interfaz principal de operación\n")
        f.write("- `ventana_abonos.py`: Gestión de abonados\n")
        f.write("- `data/`: Directorio de datos persistentes\n")
        f.write("  - `default/`: Sede predeterminada\n\n")
        f.write("## Funcionalidades principales\n\n")
        f.write("- **Enter**: Registrar ingreso de vehículo\n")
        f.write("- **F2**: Procesar salida de vehículo\n")
        f.write("- **F3**: Abrir gestión de abonos\n")
        f.write("- **Alt+A**: Validar DNI\n")
        f.write("- **Esc**: Limpiar campos\n\n")
        f.write("## Soporte\n\n")
        f.write("Para obtener ayuda o reportar problemas, contacte al administrador del sistema.\n")
    
    print(f"✅ Documentación creada: {readme_path}")
    return True

def main():
    print_header("CONFIGURACIÓN DEL SISTEMA DE GESTIÓN DE ESTACIONAMIENTO")
    
    # Verificar versión de Python
    if not check_python_version():
        print("\n❌ La versión de Python no es compatible. Se requiere Python 3.8 o superior.")
        sys.exit(1)
    
    # Crear entorno virtual
    venv_dir = create_venv()
    if not venv_dir:
        print("\n❌ No se pudo crear el entorno virtual.")
        sys.exit(1)
    
    # Instalar dependencias
    if not install_dependencies(venv_dir):
        print("\n❌ No se pudieron instalar las dependencias.")
        sys.exit(1)
    
    # Configurar directorio de datos
    if not create_data_directory():
        print("\n❌ No se pudo configurar el directorio de datos.")
        sys.exit(1)
    
    # Crear lanzadores
    if not create_launcher():
        print("\n❌ No se pudieron crear los lanzadores.")
        sys.exit(1)
    
    # Crear README
    if not create_readme():
        print("\n❌ No se pudo crear la documentación.")
        sys.exit(1)
    
    print_header("CONFIGURACIÓN COMPLETADA EXITOSAMENTE")
    print("Para iniciar el sistema:")
    
    if platform.system() == "Windows":
        print("  Ejecute: iniciar_estacionamiento.bat")
    else:
        print("  Ejecute: ./iniciar_estacionamiento.sh")
    
    print("\n¡Gracias por usar el Sistema de Gestión de Estacionamiento!")

if __name__ == "__main__":
    main()
