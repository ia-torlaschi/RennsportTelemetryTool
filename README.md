# RennsportTelemetryTool

Herramienta de análisis, visualización y coaching asistido por IA para datos de telemetría de Rennsport exportados en formato CSV.

## Propósito

Esta herramienta permite a los usuarios cargar archivos `Telemetry.csv` generados por Rennsport, procesar los datos, calcular información clave de las vueltas y visualizar diferentes aspectos del rendimiento. Además, integra Inteligencia Artificial local (a través de LM Studio) para realizar un análisis comparativo detallado entre dos vueltas y ofrecer recomendaciones de coaching personalizadas.

## Características Principales

* **Carga y Limpieza de Datos:**
    * Lee archivos `Telemetry.csv` de Rennsport.
    * Detecta automáticamente el delimitador y la fila de encabezado.
    * Extrae metadatos clave de la sesión (piloto, coche, pista, fecha, etc.).
    * Limpia y renombra columnas comunes para facilitar el análisis (`Speed`, `Throttle`, `Brake`, etc.).
    * Calcula la velocidad en Kmh si no está presente.

* **Cálculo Detallado de Vueltas:**
    * Identifica automáticamente los límites de cada vuelta.
    * Clasifica las vueltas (`Out Lap`, `Timed Lap`, `In Lap`).
    * Calcula el tiempo de cada vuelta (`LapTime`).
    * Valida las vueltas (`IsTimeValid`) basado en la bandera `IsLapValid` original y un umbral de tiempo mínimo (calculado o fijo) para descartar vueltas inválidas o incompletas.
    * Muestra un resumen con la mejor y peor vuelta válida, y la mediana.

* **Visualizaciones Comparativas y Análisis Original (Opción 1):**
    * Permite seleccionar una vuelta específica para analizar.
    * **Gráficos Individuales (vs Distancia):**
        * Perfil de Velocidad (`plot_lap_speed_profile`).
        * Entradas del Piloto (`plot_lap_inputs` - Acelerador, Freno, Volante).
        * Motor (`plot_lap_engine` - RPM, Marcha).
    * **Dashboard Comparativo (Gráfico):**
        * Compara la vuelta seleccionada con una vuelta de referencia elegida (`plot_comparison_dashboard`).
        * Muestra 5 gráficos apilados: Velocidad, Acelerador, Freno, RPM y Marcha.

* **Análisis Comparativo con IA (Opción 2 - NUEVO):**
    * Utiliza modelos de lenguaje grandes (LLM) y modelos de lenguaje visual (VLM) ejecutándose **localmente** a través de **LM Studio**.
    * **Contexto Inicial:** Intenta extraer información básica (pista, nombre piloto) mediante OCR (Tesseract) desde una imagen de "Tiempos por Vuelta" proporcionada por el usuario.
    * **Entrada Manual:** Solicita al usuario confirmar/introducir los nombres de los pilotos (destino y referencia) y sus **mejores tiempos de vuelta válidos** para establecer una comparación precisa.
    * **Regla de Color:** Asume que el piloto "destino" (el que recibe el coaching) es la **traza AZUL** en los gráficos comparativos.
    * **Análisis VLM por Gráfico:** Analiza 5 imágenes de gráficos comparativos separadas (proporcionadas por el usuario) correspondientes a:
        * Freno (Brake)
        * Acelerador (Throttle)
        * Marcha (Gear)
        * Velocidad (Speed)
        * Trazada (TrackMap)
        * Utiliza prompts detallados estilo "Race Coach Pro" para guiar al VLM en la identificación de diferencias clave y áreas de mejora.
    * **Síntesis con LLM:** Un LLM de texto (ej. Llama 3) recibe los análisis individuales del VLM y el contexto, generando un **resumen final con 4-5 consejos de coaching accionables** dirigidos al piloto destino.
    * **Output:** Muestra tanto los análisis individuales del VLM como el resumen final de coaching en la consola.

## Prerrequisitos

Antes de instalar y ejecutar la herramienta, asegúrate de tener:

1.  **Python:** Versión 3.9 o superior. Verifica con `python --version` o `python3 --version`. Descarga desde [python.org](https://www.python.org/).
2.  **pip:** Instalador de paquetes de Python (normalmente incluido). Verifica con `pip --version`.
3.  **Tesseract OCR Engine:** **Necesario para la función de IA (Opción 2).**
    * Esto **NO** se instala con `pip`. Debes instalarlo por separado en tu sistema operativo.
    * **Windows (Recomendado):** Descarga e instala desde [UB Mannheim Tesseract releases](https://github.com/UB-Mannheim/tesseract/wiki). Durante la instalación, incluye los paquetes de idioma (`English`, `Spanish`).
    * **Importante:** Después de instalar, **añade la carpeta de instalación de Tesseract** (ej. `C:\Program Files\Tesseract-OCR`) a la **variable de entorno PATH** de tu sistema y **reinicia tu terminal/IDE**. Alternativamente, puedes especificar la ruta completa a `tesseract.exe` en la variable `TESSERACT_CMD_PATH` dentro del archivo `llm_integration.py`.
    * Verifica la instalación abriendo una **nueva** terminal y ejecutando `tesseract --version`.
4.  **LM Studio:** **Necesario para la función de IA (Opción 2).**
    * Descarga e instala LM Studio desde [lmstudio.ai](https://lmstudio.ai/).
    * Dentro de LM Studio, descarga los modelos necesarios:
        * Un **VLM** compatible (probado con **`llava-v1.6-mistral-7b`** en formato GGUF).
        * Un **LLM de Texto** compatible (probado con **`meta-llama-3-8b-instruct`** en formato GGUF).
    * Asegúrate de **cargar ambos modelos** en LM Studio y **activar el Servidor API** (`Start Server`) antes de ejecutar la opción 2 del script.
5.  **Bibliotecas Python Requeridas:** Se instalarán con `pip`. (Ver sección de Instalación).

## Instalación

1.  **Clonar o Descargar:**
    ```bash
    # Si usas git
    git clone [https://github.com/ia-torlaschi/RennsportTelemetryTool](https://github.com/ia-torlaschi/RennsportTelemetryTool)
    cd RennsportTelemetryTool
    ```
    (O descarga y extrae el ZIP).

2.  **Crear Entorno Virtual (Recomendado):**
    ```bash
    python -m venv venv
    ```

3.  **Activar Entorno Virtual:**
    * Windows: `venv\Scripts\activate`
    * macOS/Linux: `source venv/bin/activate`

4.  **Instalar Dependencias:**
    * Asegúrate de tener un archivo `requirements.txt` con el siguiente contenido (o añádelo):
        ```txt
        pandas>=1.3
        numpy>=1.20
        matplotlib>=3.4
        requests>=2.25
        pytesseract>=0.3.8
        Pillow>=9.0
        ```
    * Ejecuta (con el entorno virtual activo):
        ```bash
        pip install -r requirements.txt
        ```

## Configuración (Opcional - Para IA)

* **Nombres de Modelo:** Si usas modelos diferentes a los predeterminados en LM Studio, edita las constantes `DEFAULT_VLM_MODEL` y `DEFAULT_TEXT_MODEL` al principio del archivo `llm_integration.py`.
* **Puerto LM Studio:** Si tu servidor API de LM Studio usa un puerto diferente al 1234, cambia `DEFAULT_PORT` en `llm_integration.py`.
* **Ruta Tesseract:** Si no añadiste Tesseract al PATH, descomenta y edita `TESSERACT_CMD_PATH` en `llm_integration.py`.

## Datos de Ejemplo

* **Telemetría CSV:** `/data_sample/csv/Telemetry.csv` (Hockenheimring GP - Mercedes-AMG GT3). Úsalo para probar la carga y los gráficos originales (Opción 1).
* **Imágenes para IA:** Se requieren imágenes generadas por el usuario desde i2Pro (o similar) para la Opción 2:
    * Una imagen tipo "Lap Times" (como `image_fa49c3.png` del hilo) para el OCR inicial.
    * Cinco imágenes separadas de gráficos comparativos (vs Distancia) entre el piloto destino y el de referencia para: Brake, Throttle, Gear, Speed, TrackMap.

## Uso

1.  **Activar Entorno Virtual** (si creaste uno).
2.  **(Para Opción 2 - IA):** Asegúrate de que **LM Studio esté corriendo**, los modelos VLM y Texto estén **cargados**, y el **Servidor API esté iniciado**.
3.  **Ejecutar Script:**
    ```bash
    python main.py
    ```
4.  **Proporcionar Ruta CSV:** Pega la ruta completa al `Telemetry.csv`.
5.  **Elegir Opción:**
    * **Opción 1 (Gráficos Originales):**
        * Introduce el número de vuelta a visualizar.
        * Elige el tipo de gráfico (1-5) o el dashboard comparativo (4).
        * Si eliges el dashboard (4), introduce el número de la vuelta de referencia.
        * Cierra la ventana del gráfico para continuar. Usa 'V' para retroceder.
    * **Opción 2 (Análisis IA):**
        * Introduce la ruta a la imagen de **Tiempos por Vuelta**.
        * Confirma/introduce tu nombre de piloto (destino=AZUL).
        * Confirma/introduce tu **mejor tiempo de vuelta válido** (formato MM:SS.ms).
        * Introduce el nombre del piloto de **referencia**.
        * Introduce el **mejor tiempo de vuelta válido** del piloto de referencia.
        * Confirma/introduce el nombre de la pista (opcional).
        * Introduce la ruta a la imagen del gráfico de **Brake** (o escribe 'saltar').
        * Introduce la ruta a la imagen del gráfico de **Throttle** (o 'saltar').
        * Introduce la ruta a la imagen del gráfico de **Gear** (o 'saltar').
        * Introduce la ruta a la imagen del gráfico de **Speed** (o 'saltar').
        * Introduce la ruta a la imagen del gráfico de **TrackMap** (o 'saltar').
        * Espera el análisis y la síntesis final.
    * **Opción V:** Volver a seleccionar archivo CSV.
    * **Opción Q:** Salir.

## Salida

* **Consola:** Muestra logs del proceso, metadatos, resumen de vueltas, menús, resultados OCR, contexto construido, resultados individuales del VLM y el resumen final de coaching de la IA.
* **Gráficos (Opción 1):** Ventanas interactivas de Matplotlib.

## Estructura del Código

* `main.py`: Script principal, flujo, menús e interacción con el usuario. Llama a las demás funciones.
* `data_loader.py`: Carga y preparación inicial de datos CSV.
* `plotter.py`: Funciones de visualización de gráficos originales (individuales y dashboard).
* `llm_integration.py`: Lógica para OCR (Tesseract), llamadas a la API de LM Studio (VLM y LLM), y prompts de IA.
* `requirements.txt`: Dependencias de Python.
* `/data_sample/csv/Telemetry.csv`: Archivo de datos de ejemplo.

## Disclaimer

* **Cálculo de Tiempos:** Los tiempos de vuelta calculados por esta herramienta pueden diferir ligeramente (~1 intervalo de muestreo) de los mostrados en MoTeC i2 Pro debido a diferencias en el método de detección del cruce de meta (timestamp discreto vs. interpolación). Esto generalmente no afecta el análisis comparativo de patrones.
* **Análisis IA:** Los análisis y recomendaciones generados por los modelos de IA (LLaVA, Llama 3) son sugerencias basadas en los datos visuales y el contexto proporcionado. Deben ser considerados como una **herramienta de apoyo** y no reemplazan el juicio y la experiencia de un piloto o ingeniero real. La calidad del análisis puede variar según la calidad de las imágenes, la claridad de los datos y las capacidades inherentes de los modelos locales.

## Licencia

[MIT License](https://opensource.org/licenses/MIT).

## Créditos

* **Desarrollador Principal:** Jorge Torlaschi
* **Dataset Ejemplo:** Sesión de práctica en Rennsport.
* **Asistencia IA:** Gemini (Google).