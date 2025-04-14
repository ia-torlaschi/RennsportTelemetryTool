# RennsportTelemetryTool

Herramienta de análisis y visualización de datos de telemetría para Rennsport exportados en formato CSV.

## Propósito

Esta herramienta permite a los usuarios cargar archivos `Telemetry.csv` generados por Rennsport, procesar los datos, calcular información clave de las vueltas y visualizar diferentes aspectos del rendimiento a través de gráficos interactivos generados con Matplotlib.

## Características Principales

* **Carga y Limpieza de Datos:** Lee archivos `Telemetry.csv`, detecta automáticamente el delimitador y la fila de encabezado, extrae metadatos de la sesión (piloto, coche, pista, etc.) y limpia/renombra columnas comunes para facilitar el análisis.

* **Cálculo de Vueltas:**
    * Identifica automáticamente los límites de cada vuelta basándose en el cambio del número de vuelta (`Lap`) registrado en el archivo CSV.
    * Clasifica las vueltas como `Out Lap`, `Timed Lap` o `In Lap`.
    * Calcula el tiempo de cada vuelta completa (`LapTime`).
    * Valida las vueltas (`IsTimeValid`) considerando tanto la bandera `IsLapValid` del archivo original (verificando que sea `True` durante toda la vuelta) como un umbral mínimo de tiempo configurable para descartar vueltas anómalas.
    * Muestra un resumen con la mejor vuelta válida, la peor vuelta válida y la mediana de los tiempos válidos.

* **Menú Interactivo:** Permite al usuario seleccionar qué vuelta analizar y qué tipo de informe o gráfico generar para esa vuelta.

* **Visualizaciones (vs Distancia):**
    * **Informes Individuales:**
        * Perfil de Velocidad (`plot_lap_speed_profile`)
        * Entradas del Piloto (`plot_lap_inputs` - Acelerador, Freno, Volante)
        * Motor (`plot_lap_engine` - RPM, Marcha)
    * **Dashboard Comparativo:**
        * Compara la vuelta seleccionada con una vuelta de referencia elegida por el usuario (`plot_comparison_dashboard`).
        * Muestra 5 gráficos apilados: Velocidad, Acelerador, Freno, RPM y Marcha.

## Disclaimer: Cálculo de Tiempos de Vuelta y Comparación con MoTeC i2 Pro

Es importante entender cómo esta herramienta calcula los tiempos de vuelta y cómo pueden diferir ligeramente de otras herramientas profesionales como MoTeC i2 Pro:

* **Método de Cálculo:** Los tiempos de vuelta (`LapTime`) se calculan midiendo la diferencia de tiempo (`Time`) entre los límites de cada vuelta. Estos límites se determinan identificando la **última muestra de datos registrada para una vuelta** antes de que el número de `Lap` cambie en la siguiente muestra.

* **Precisión:** Este método identifica correctamente las vueltas Out/In y la validez (comparando con la bandera `IsLapValid` y un umbral de tiempo), logrando una clasificación consistente con herramientas como MoTeC i2 Pro.

* **Posible Diferencia Mínima:** Sin embargo, los **valores absolutos** del tiempo de vuelta calculado pueden presentar una pequeña diferencia (observada en torno a ~10ms o un intervalo de muestreo) en comparación con MoTeC i2 Pro. La razón más probable es que MoTeC puede realizar una **interpolación temporal** para estimar el instante *exacto* del cruce de la línea de meta (basándose en distancia o coordenadas), mientras que esta herramienta utiliza los timestamps *discretos* de las muestras de datos donde cambia el número de vuelta.

* **Impacto:** Para la mayoría de los análisis comparativos y la identificación de patrones, esta pequeña diferencia es generalmente insignificante. No obstante, los usuarios deben ser conscientes de ella si requieren una comparación de tiempos absolutos con precisión de milisegundos respecto a MoTeC i2 Pro.

## Prerrequisitos

Antes de instalar y ejecutar la herramienta, asegúrate de tener:

1.  **Python:** Versión 3.9 o superior instalada. Puedes verificar tu versión abriendo una terminal o símbolo del sistema y ejecutando:
    ```bash
    python --version
    # o en algunos sistemas:
    python3 --version
    ```
    Si no tienes Python, descárgalo desde [python.org](https://www.python.org/).

2.  **pip:** El instalador de paquetes de Python. Normalmente se incluye con las instalaciones modernas de Python. Puedes verificarlo con:
    ```bash
    pip --version
    # o
    pip3 --version
    ```

3.  **Bibliotecas Requeridas:** Las siguientes bibliotecas de Python son necesarias y se instalarán usando el archivo `requirements.txt`:
    * `pandas`
    * `numpy`
    * `matplotlib`

## Instalación

1.  **Clonar o Descargar:** Obtén los archivos del proyecto en tu máquina local.
    ```bash
    # Si usas git
    git clone https://github.com/ia-torlaschi/RennsportTelemetryTool
    cd RennsportTelemetryTool
    ```


2.  **Crear Entorno Virtual (Muy Recomendado):** Esto aísla las dependencias del proyecto. Dentro del directorio del proyecto (`RennsportTelemetryTool`):
    ```bash
    python -m venv venv
    ```

3.  **Activar el Entorno Virtual:**
    * **Windows (cmd/powershell):** `venv\Scripts\activate`
    * **MacOS/Linux (bash/zsh):** `source venv/bin/activate`
    Verás `(venv)` al principio de la línea de comandos si está activo.

4.  **Instalar Dependencias:** Con el entorno virtual activo, instala las bibliotecas necesarias:
    ```bash
    pip install -r requirements.txt
    ```

## Datos de Ejemplo

Este proyecto incluye un archivo de datos de ejemplo para que puedas probar la herramienta inmediatamente:

* **Ubicación:** `/sata_sample/csv/Telemetry.csv` (Relativo a la raíz del proyecto).
* **Contenido:** Datos de una sesión de carrera con un Mercedes-AMG GT3 2020 en Hockenheimring (GP).
* **Uso:** Cuando el script te pida la ruta al archivo CSV, puedes proporcionar la ruta completa a este archivo de ejemplo.

## Uso

1.  **Activar Entorno Virtual:** Asegúrate de que el entorno virtual esté activado (si lo creaste).
2.  **Ejecutar el Script Principal:** Desde la terminal, dentro del directorio raíz del proyecto, ejecuta:
    ```bash
    python main.py
    ```
3.  **Proporcionar Ruta al CSV:** Pega la ruta completa al archivo `Telemetry.csv` que deseas analizar (puedes usar el archivo de ejemplo) y presiona Enter.
    ```
    Por favor, pega la ruta completa al archivo Telemetry.csv y presiona Enter:
    Ruta al archivo (o deja vacío para salir): sata_sample/csv/Telemetry.csv
    ```
4.  **Seleccionar Vuelta:** Se mostrará un resumen de los tiempos de vuelta. Introduce el número de la vuelta a visualizar.
5.  **Seleccionar Informe:** Elige el tipo de gráfico o dashboard del menú.
6.  **Seleccionar Vuelta de Referencia (si aplica):** Si eliges el Dashboard Comparativo (opción 4), introduce el número de una vuelta válida como referencia.
7.  **Visualizar/Continuar:** Se mostrará el gráfico/dashboard. Ciérralo para volver al menú anterior. Usa 'Q' para retroceder o salir.

## Salida

* **Consola:** Muestra información del proceso, metadatos, resumen de vueltas y menús.
* **Gráficos:** Ventanas interactivas de Matplotlib mostrando los gráficos seleccionados.

## Estructura del Código

* `main.py`: Script principal, flujo e interacción.
* `data_loader.py`: Carga y preparación de datos CSV.
* `plotter.py`: Funciones de visualización (gráficos individuales y dashboard).
* `requirements.txt`: Dependencias de Python.
* `/sata_sample/csv/Telemetry.csv`: Archivo de datos de ejemplo.

## Licencia

[MIT License](https://opensource.org/licenses/MIT).

## Créditos

* **Desarrollador Principal:** Jorge Torlaschi

* **Dataset:** Carrera de prueba de Rennsport
