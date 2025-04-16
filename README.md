# RennsportTelemetryTool

Herramienta de análisis, visualización y coaching asistido por IA para datos de telemetría de Rennsport exportados en formato CSV.

---

## 📅 Propósito

Esta herramienta permite a los usuarios cargar archivos `Telemetry.csv` generados por Rennsport, procesar los datos, calcular información clave de las vueltas y visualizar diferentes aspectos del rendimiento. Además, integra Inteligencia Artificial local (a través de **LM Studio**) para realizar un análisis comparativo detallado entre dos vueltas y ofrecer recomendaciones de coaching personalizadas.

---

## ✨ Características Principales

### ✅ Carga y Limpieza de Datos:
* Lee archivos `Telemetry.csv` de Rennsport.
* Detecta automáticamente el delimitador y la fila de encabezado.
* Extrae metadatos clave de la sesión (piloto, coche, pista, fecha, etc.).
* Limpia y renombra columnas comunes para facilitar el análisis (`Speed`, `Throttle`, `Brake`, etc.).
* Calcula la velocidad en Kmh si no está presente.

### ✅ Cálculo Detallado de Vueltas:
* Identifica automáticamente los límites de cada vuelta.
* Clasifica las vueltas (`Out Lap`, `Timed Lap`, `In Lap`).
* Calcula el tiempo de cada vuelta (`LapTime`).
* Valida las vueltas (`IsTimeValid`) basado en la bandera `IsLapValid` original y un umbral de tiempo mínimo (calculado o fijo) para descartar vueltas inválidas o incompletas.
* Muestra un resumen con la mejor y peor vuelta válida, y la mediana.

### ✅ Visualizaciones Comparativas y Análisis Original (Opción 1):
* Permite seleccionar una vuelta específica para analizar.
* **Gráficos Individuales (vs Distancia):**
  * Perfil de Velocidad (`plot_lap_speed_profile`).
  * Entradas del Piloto (`plot_lap_inputs` - Acelerador, Freno, Volante).
  * Motor (`plot_lap_engine` - RPM, Marcha).
* **Dashboard Comparativo (Gráfico):**
  * Compara la vuelta seleccionada con una vuelta de referencia elegida (`plot_comparison_dashboard`).
  * Muestra 5 gráficos apilados: Velocidad, Acelerador, Freno, RPM y Marcha.

### ✅ Análisis Comparativo con IA (Opción 2 - NUEVO):
* Utiliza modelos de lenguaje grandes (LLM) y modelos de lenguaje visual (VLM) ejecutándose **localmente** a través de **LM Studio**.
* **Contexto Inicial:** Intenta extraer información básica (pista, nombre piloto) mediante OCR (Tesseract) desde una imagen de "Tiempos por Vuelta" proporcionada por el usuario.
* **Entrada Manual:** Solicita al usuario confirmar/introducir los nombres de los pilotos (destino y referencia) y sus **mejores tiempos de vuelta válidos** para establecer una comparación precisa.
* **Regla de Color:** Asume que el piloto "destino" (el que recibe el coaching) es la **traza AZUL** en los gráficos comparativos.
* **Análisis VLM por Gráfico:** Analiza hasta **6 imágenes** comparativas separadas:
  * Freno (Brake)
  * Acelerador (Throttle)
  * Marcha (Gear)
  * Velocidad (Speed)
  * Trazada (TrackMap)
  * Dirección (Steering)
* Utiliza prompts detallados estilo "Race Coach Pro" ( https://chatgpt.com/g/g-67fe4f8c60c08191a8611fb61c5fb1ed-race-coach-pro-by-torlaschi-consulting ) para guiar al VLM en la identificación de diferencias clave y áreas de mejora.
* **Síntesis con LLM:** Un LLM de texto (ej. Llama 3) recibe los análisis individuales del VLM y el contexto, generando un **resumen final con 4-5 consejos de coaching accionables** dirigidos al piloto destino.
* **Output:** Muestra tanto los análisis individuales del VLM como el resumen final de coaching en la consola.

---

## ⚠️ Requisitos Previos

### 📅 Software

1. **Python:** Versión 3.9 o superior.
2. **Tesseract OCR:** Necesario para el OCR de imagen de tiempos.
3. **LM Studio:** Necesario para ejecutar localmente modelos VLM y LLM.

### 📚 Modelos requeridos (dentro de LM Studio):
* **VLM:** `llava-v1.6-mistral-7b` (GGUF).
* **LLM:** `meta-llama-3-8b-instruct` (GGUF).

---

## ⚙️ Instalación

```bash
# Clonar repositorio
https://github.com/ia-torlaschi/RennsportTelemetryTool.git
cd RennsportTelemetryTool

# Crear entorno virtual
python -m venv venv

# Activar entorno
venv\Scripts\activate      # Windows
source venv/bin/activate   # macOS/Linux

# Instalar dependencias
pip install -r requirements.txt
```

**`requirements.txt` sugerido:**
```txt
pandas>=1.3
numpy>=1.20
matplotlib>=3.4
requests>=2.25
pytesseract>=0.3.8
Pillow>=9.0
```

---

## 📁 Datos de Ejemplo

* `/data_sample/csv/Telemetry.csv`: Para Opción 1.
* Imágenes de: Lap Times, Brake, Throttle, Gear, Speed, TrackMap, Steering.

---

## ⚖️ Uso

### Opción 1: Gráficos Originales
1. Selecciona vuelta a analizar.
2. Elige tipo de gráfico individual o dashboard comparativo.

### Opción 2: Análisis IA
1. Introduce imagen con Tiempos por Vuelta.
2. Confirma nombres de pilotos y sus mejores tiempos.
3. Ingresa hasta 6 imágenes de los canales: Brake, Throttle, Gear, Speed, TrackMap, Steering.
4. Espera salida por consola con:
   * Análisis individuales por canal.
   * Resumen final de coaching generado por el LLM.

---

## 🔍 Detalles técnicos del prompt de síntesis

La generación del resumen final está guiada por un prompt de tipo "instrucción" que incluye:
* Contexto estructurado: pista, pilotos, delta, color.
* Instrucciones estrictas:
  - Sintetizar, no repetir.
  - Elegir 4-5 puntos clave.
  - Redactar como ingeniero de pista.
  - Usar lenguaje claro, directo, accionable.
  - Priorizar errores repetidos en múltiples canales.

---

## 📈 Salida

* Consola con logs paso a paso.
* Gráficos Matplotlib en Opción 1.
* Análisis por canal + coaching resumen (Opción 2).

---

## 🚫 Disclaimer

* Tiempos pueden diferir levemente de MoTeC por interpolación.
* El coaching generado por IA es solo orientativo y no reemplaza el juicio de un piloto o ingeniero humano.

---

## 🌐 Licencia

[MIT License](https://opensource.org/licenses/MIT)

---

## 👨‍💼 Créditos

* **Desarrollador:** Jorge Torlaschi
* **Asistencia IA:** Gemini + LM Studio
* **Dataset Ejemplo:** Práctica Rennsport Hockenheim GP

---

## 🔗 Badges (opcional para GitHub)

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![LM Studio](https://img.shields.io/badge/LLM-Vision%2BText-green)
![Status](https://img.shields.io/badge/status-Beta%20Estable-brightgreen)

