# Sistema de Gestión de Estacionamiento

Sistema completo para la administración de estacionamientos con soporte para abonados, tarifas por fracción, diarias y por turno.

## Características principales

- ✅ Gestión de ingresos y egresos de vehículos
- ✅ Soporte para múltiples esquemas de tarifación
- ✅ Sistema de abonados con fechas de vencimiento
- ✅ Validación completa de operaciones
- ✅ Interfaz gráfica intuitiva con atajos de teclado
- ✅ Almacenamiento de datos persistente
- ✅ Totalmente portátil entre diferentes equipos

## Requisitos del sistema

- Python 3.8 o superior
- Tkinter (incluido con la mayoría de las instalaciones de Python)
- Bibliotecas adicionales (se instalan automáticamente durante la configuración)

## Instalación

### Paso 1: Obtener el código

Clone o descargue este repositorio a su equipo local.

### Paso 2: Configurar el entorno

Ejecute el script de configuración para preparar el sistema:

```bash
# En Windows
python configurar.py

# En Linux/macOS
python3 configurar.py
```

El script de configuración realizará las siguientes acciones:
- Verificará la versión de Python instalada
- Creará un entorno virtual para aislar las dependencias
- Instalará todas las bibliotecas necesarias
- Configurará los directorios de datos
- Creará scripts de inicio para su sistema operativo

### Paso 3: Iniciar el sistema

Una vez completada la configuración, puede iniciar el sistema:

- **En Windows:** Ejecute `iniciar_estacionamiento.bat`
- **En Linux/macOS:** Ejecute `./iniciar_estacionamiento.sh`

## Guía de uso rápido

### Operaciones básicas

- **Ingreso de vehículo:** Presione `Enter` en la pantalla principal
- **Egreso de vehículo:** Presione `F2` e ingrese el número de ticket
- **Gestión de abonos:** Presione `F3` para abrir el panel de abonados
- **Validar DNI de abonado:** Presione `Alt+A` en la pantalla principal
- **Limpiar campos:** Presione `Esc` en cualquier momento

### Gestión de abonados

- **Consultar abonado:** Ingrese el DNI y presione "Buscar"
- **Registrar nuevo abonado:** Complete los datos y presione "Guardar"
- **Renovar abono:** Seleccione un abonado existente y presione "Renovar"
- **Registrar pago:** Complete los campos de pago y presione "Guardar Pago"

## Estructura de datos

Los datos se almacenan en archivos de texto plano con formato delimitado por punto y coma (CSV):

- `config.txt`: Configuración general del estacionamiento
- `turnos.txt`: Definición de turnos y horarios especiales
- `personas.txt`: Registro de personas/clientes
- `abonos.txt`: Registro de abonos activos e históricos
- `pagos_abono.txt`: Registro de pagos de abonos
- `movimientos_abiertos.txt`: Vehículos actualmente en el estacionamiento
- `movimientos_cerrados_AAAAMM.txt`: Histórico de ingresos/egresos por mes

## Transferencia a otro equipo

Este sistema está diseñado para ser portátil. Para transferirlo a otro equipo:

1. Copie toda la carpeta del proyecto al nuevo equipo
2. Ejecute `configurar.py` en el nuevo equipo
3. Use los scripts de inicio para arrancar el sistema

## Creación de acceso directo

Para crear un acceso directo con el logo del sistema:

1. **Generar iconos** (opcional si no existen):
   ```bash
   # En Windows
   python crear_icono.py
   
   # En Linux/macOS
   ./crear_icono.py
   ```

2. **Crear el acceso directo**:
   ```bash
   # En Windows
   python crear_acceso_directo.py
   
   # En Linux/macOS
   ./crear_acceso_directo_linux.py
   ```

## Empaquetado como ejecutable

Para distribuir el sistema como un ejecutable único:

1. **Empaquetado rápido** (recomendado):
   ```bash
   # En Windows
   python empaquetar_rapido.py
   
   # En Linux/macOS
   ./empaquetar_rapido.py
   ```

2. **Empaquetado con opciones avanzadas**:
   ```bash
   # En Windows
   python empaquetar_aplicacion.py
   
   # En Linux/macOS
   ./empaquetar_aplicacion.py
   ```

El ejecutable generado estará disponible en la carpeta `dist` y podrá ser distribuido sin necesidad de instalar Python en los equipos de destino.

## Solución de problemas

### El sistema no inicia

Verifique:
- Que Python esté instalado correctamente
- Que se haya ejecutado el script de configuración
- Que los permisos de ejecución estén configurados correctamente

### Errores con Tkinter

En algunos sistemas Linux, puede ser necesario instalar Tkinter manualmente:

```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# Fedora
sudo dnf install python3-tkinter

# Arch Linux
sudo pacman -S tk
```

## Soporte

Para obtener ayuda o reportar problemas, contacte al administrador del sistema o abra un issue en este repositorio.
