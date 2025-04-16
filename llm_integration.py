# llm_integration.py (vFinal Definitiva - Basado en tu código + Todas las Mejoras)

import os
import base64
import requests
import json
import subprocess
import sys
import traceback
import pytesseract # Para OCR
from PIL import Image # Para abrir imágenes con pytesseract
import io # Para manejo de bytes de imagen
import re # Para expresiones regulares (parseo OCR)
import numpy as np # Para float('inf') en conversión de tiempo

# --- Constantes Simples ---
# Asegúrate de que estos nombres coincidan EXACTAMENTE con los modelos CARGADOS en LM Studio
DEFAULT_VLM_MODEL = "llava-v1.6-mistral-7b"       # Modelo VLM para analizar gráficos
DEFAULT_TEXT_MODEL = "meta-llama-3-8b-instruct"  # Modelo LLM Texto para la síntesis
DEFAULT_PORT = 1234                              # Puerto por defecto de LM Studio API

# --- CONFIGURACIÓN TESSERACT (OPCIONAL) ---
# Si Tesseract no está en tu PATH de sistema, descomenta la siguiente línea
# y ajusta la ruta EXACTA a tu ejecutable tesseract.exe
# TESSERACT_CMD_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# try:
#     pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD_PATH
#     print(f"INFO: Usando ruta Tesseract especificada en código: {TESSERACT_CMD_PATH}")
# except Exception as e:
#      print(f"ADVERTENCIA: No se pudo establecer tesseract_cmd vía código ({e}). Asegúrate que Tesseract esté en el PATH.")

# --- Funciones de Detección de Endpoint ---
def detect_windows_host_ip():
    """Detecta la IP del host Windows desde WSL2 o devuelve IP local."""
    host_ip = "127.0.0.1" # Default
    try: # Intenta WSL2
        # Usar timeout corto para evitar bloqueos si el comando tarda
        output = subprocess.check_output("ip route show default", shell=True, stderr=subprocess.DEVNULL, timeout=2).decode()
        parts = output.split()
        if 'via' in parts:
            ip_index = parts.index('via') + 1
            if ip_index < len(parts): host_ip = parts[ip_index]
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception): pass # Ignorar errores/timeouts

    if host_ip == "127.0.0.1": # Si no es WSL o falló, intentar hostname -I
        try:
            output_hostname = subprocess.check_output("hostname -I", shell=True, stderr=subprocess.DEVNULL, timeout=2).decode()
            first_ip = output_hostname.strip().split()[0]
            # Validar formato IP simple
            if first_ip and len(first_ip.split('.')) == 4 and all(p.isdigit() for p in first_ip.split('.')):
                # print(f"Adv: Usando IP de 'hostname -I': {first_ip}") # Opcional: menos verboso
                host_ip = first_ip
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception): pass

    # Solo imprimir advertencia si realmente no se pudo detectar y se usa 127.0.0.1
    # if host_ip == "127.0.0.1": print("Adv: IP no detectada automáticamente. Usando 127.0.0.1.") # Opcional
    return host_ip

_cached_endpoint = None
def get_lm_studio_endpoint():
    """Detecta y devuelve la URL completa del endpoint de LM Studio, cacheando."""
    global _cached_endpoint
    if _cached_endpoint is None:
        host_ip = detect_windows_host_ip()
        _cached_endpoint = f"http://{host_ip}:{DEFAULT_PORT}"
        # Imprimir solo la primera vez
        print(f"Endpoint de LM Studio determinado como: {_cached_endpoint}")
    return _cached_endpoint

# --- Funciones de Utilidad (Imagen) ---
def encode_image_to_base64(image_source):
    """Codifica una imagen (ruta str o PIL.Image) a base64 string."""
    try:
        img = None
        if isinstance(image_source, str):
            if not os.path.exists(image_source): raise FileNotFoundError(f"Archivo no encontrado: {image_source}")
            img = Image.open(image_source)
        elif isinstance(image_source, Image.Image):
            img = image_source
        else: raise TypeError("image_source debe ser ruta str o PIL.Image")

        # Convertir a RGB si es necesario (para JPEG)
        if img.mode in ['RGBA', 'P', 'LA']: img = img.convert('RGB')

        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=90) # Usar JPEG por eficiencia
        return base64.b64encode(buffer.getvalue()).decode('utf-8')
    except FileNotFoundError as e: print(f"Error B64: {e}"); raise
    except Exception as e: print(f"Error B64 ({type(e).__name__}): {e}"); raise

# --- Funciones de Utilidad (Tiempo) ---
def time_str_to_seconds(time_str):
    """Convierte MM:SS.ms o MM:SS,ms a segundos, devuelve inf en error."""
    if not isinstance(time_str, str): return float('inf')
    try:
        time_str_cleaned = time_str.replace(',', '.').strip()
        parts = time_str_cleaned.split(':')
        if len(parts) == 2: # Formato MM:SS.ms
            minutes = int(parts[0])
            seconds_ms_part = parts[1]
            seconds_ms = seconds_ms_part.split('.')
            if len(seconds_ms) == 2:
                 seconds = int(seconds_ms[0])
                 millis_str = seconds_ms[1]
                 if not millis_str.isdigit(): return float('inf')
                 # Truncar/rellenar milisegundos
                 if len(millis_str) > 3: millis_str = millis_str[:3]
                 elif len(millis_str) < 3: millis_str = millis_str.ljust(3, '0')
                 millis = int(millis_str)
                 if 0 <= seconds < 60 and 0 <= millis < 1000:
                      return minutes * 60.0 + seconds + millis / 1000.0
            elif len(seconds_ms) == 1: # Formato MM:SS
                 seconds = int(seconds_ms[0])
                 if 0 <= seconds < 60: return minutes * 60.0 + seconds
        return float('inf')
    except (ValueError, IndexError, TypeError): return float('inf')

# --- Función OCR para Imagen de Tiempos (Versión Final) ---
def extract_context_from_laptime_image(image_path):
    """
    Extrae Pista, Piloto Destino (el primero encontrado) y Mejor Tiempo Válido.
    Devuelve dict {'track_name': ..., 'target_driver_name': ..., 'target_best_lap': ...} o None.
    """
    print(f"Intentando OCR en imagen de tiempos: {image_path}")
    ocr_result = {"track_name": None, "driver_name_1": None, "driver_name_2": None, "target_best_lap": None}
    min_lap_time_sec = float('inf')
    best_lap_str = None

    try:
        # Ejecutar OCR
        try:
             custom_config = r'--psm 6' # Asumir bloque de texto uniforme
             if 'TESSERACT_CMD_PATH' in globals() and TESSERACT_CMD_PATH: pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD_PATH
             raw_text = pytesseract.image_to_string(Image.open(image_path), lang='eng+spa', config=custom_config)
        except pytesseract.TesseractNotFoundError: print("\nERROR CRÍTICO: 'tesseract' no encontrado..."); return None
        except FileNotFoundError: print(f"Error OCR: Archivo no encontrado - {image_path}"); return None
        except Exception as ocr_err: print(f"Error Tesseract/PIL: {ocr_err}"); return None

        print("--- Texto OCR Crudo (Imagen Tiempos) ---"); print(raw_text); print("---")
        lines = raw_text.splitlines()
        if not lines: print("Error OCR: No texto."); return None

        # --- Parsear Pista ---
        track_keywords = ["International Speedway", "Circuit", "Raceway", "Park", "Ring", "Track", "Motor", "Autodromo", "Sportsland"]
        track_found = False
        for line in lines:
            clean_line = re.sub(r"^\s*E\s+", "", line).strip()
            # Buscar nombre que contenga palabra clave o termine en (GP)
            if any(kw in clean_line for kw in track_keywords) or (clean_line.endswith("(GP)") and len(clean_line) > 5):
                # Intentar extraer la parte relevante
                match = re.match(r"([A-Za-z\s\-\(\)\d]+(?:{}|GP\)?))".format("|".join(track_keywords)), clean_line, re.IGNORECASE)
                if match: ocr_result["track_name"] = match.group(1).strip(); track_found = True; break
                elif clean_line.endswith("(GP)"): ocr_result["track_name"] = clean_line; track_found = True; break # Fallback
        if not track_found: print("Adv OCR: Pista no encontrada.")

        # --- Parsear Nombres Pilotos (Intentar encontrar AMBOS) ---
        driver_names_found = []
        # Buscar "E Nombre, Vehiculo YYYY" o "E Nombre," simple
        name_pattern_detailed = r"^\s*E\s+([^,]+),\s*(?:[A-Za-z0-9\- ]+\s+\d{4})$"
        name_pattern_simple = r"^\s*E\s+([^,]+),"
        for line in lines:
             match = re.search(name_pattern_detailed, line) or re.search(name_pattern_simple, line)
             if match:
                 name = match.group(1).strip()
                 # Filtrar nombres poco probables o duplicados
                 if name and len(name) > 3 and name.lower() != "practice" and not any(kw in name for kw in ["Speedway", "Circuit", "/", ":"]) and name not in driver_names_found:
                      driver_names_found.append(name)
        if len(driver_names_found) >= 1: ocr_result["driver_name_1"] = driver_names_found[0]
        if len(driver_names_found) >= 2: ocr_result["driver_name_2"] = driver_names_found[1]
        if not driver_names_found: print("Error OCR: No se encontraron nombres de piloto.")
        elif len(driver_names_found) == 1: print("Adv OCR: Solo se encontró 1 nombre de piloto.")


        # --- Parsear Tiempos de Vuelta y encontrar el mejor ---
        lap_times_found = []
        time_pattern = r"^\s*(?:lap\s?|\s)\d+\s+.*?(\d{1,2}:\d{2}[.,]\d{3})" # Más flexible al inicio
        for line in lines:
            match = re.search(time_pattern, line, re.IGNORECASE)
            if match: lap_times_found.append(match.group(1).replace(',', '.'))

        print(f"Tiempos (formato MM:SS.ms) encontrados por OCR: {lap_times_found}")
        if lap_times_found:
            valid_times_sec = []
            for time_str in lap_times_found:
                time_sec = time_str_to_seconds(time_str)
                if 30 < time_sec < 1200: valid_times_sec.append((time_sec, time_str))
            if valid_times_sec:
                valid_times_sec.sort(); min_lap_time_sec, best_lap_str = valid_times_sec[0]
                ocr_result["target_best_lap"] = best_lap_str
                print(f"Mejor tiempo VÁLIDO encontrado: {best_lap_str} ({min_lap_time_sec:.3f}s)")
            else: print("Advertencia OCR: No se encontraron tiempos VÁLIDOS.")
        else: print("Advertencia OCR: No se encontró ningún tiempo MM:SS.ms.")

        print("Resultado OCR Parcial Final:", ocr_result)
        return ocr_result

    except Exception as e: print(f"Error inesperado en OCR Tiempos: {e}"); traceback.print_exc(); return None


# --- Función de Análisis VLM (PROMPTS MEJORADOS - Versión Final) ---
def analyze_telemetry_comparison_graph(
    image_path,
    graph_type,  # "Brake", "Throttle", "Gear", "Speed", "TrackMap", "Steering"
    context,     # Contexto completo construido en main.py
    model_endpoint=None,
    model_name=DEFAULT_VLM_MODEL
):
    """Analiza gráfico VLM con prompt personalizado y contexto completo."""
    endpoint = model_endpoint or get_lm_studio_endpoint()
    if not endpoint:
        return "[Error: Endpoint LM Studio no determinado]"

    image_filename = os.path.basename(image_path) if image_path else "N/A"

    required_keys = [
        "target_driver", "reference_driver", "faster_driver", "slower_driver",
        "target_color", "reference_color", "target_lap_time", "reference_lap_time"
    ]
    if not context or not all(context.get(k) for k in required_keys):
        print(f"Error: Contexto COMPLETO inválido para VLM {graph_type}")
        print("Contexto:", context)
        return "[Error: Contexto (manual+OCR) inválido/incompleto para VLM]"

    print(f"Analizando gráfico de {graph_type}: {image_filename} con {model_name}")
    print(f"Contexto VLM: {context['target_driver']} ({context['target_color']}) vs {context['reference_driver']} ({context['reference_color']})")

    try:
        base64_image = encode_image_to_base64(image_path)
        image_data_url = f"data:image/jpeg;base64,{base64_image}"

        # --- Descripciones específicas por tipo de gráfico ---
        graph_instructions = {
            "Brake": (
                "Analiza la curva de frenado en cada sector del circuito. "
                "Identifica si el piloto destino frena más temprano o más tarde que el piloto referencia, y si aplica más o menos presión. "
                "Evalúa duración y progresividad de la frenada, especialmente en entrada a curva. "
                "Detecta posibles zonas de pérdida por exceso de precaución o por frenadas agresivas mal posicionadas."
            ),
            "Throttle": (
                "Analiza cómo aplica el acelerador el piloto destino respecto al piloto referencia, especialmente en salida de curvas. "
                "Detecta si hay retrasos en el inicio de aceleración, aplicaciones parciales inseguras o picos abruptos. "
                "Revisa la transición del freno al gas, y si mantiene buena tracción al acelerar."
            ),
            "Gear": (
                "Compara los puntos de cambio de marcha entre ambos pilotos. "
                "Evalúa si el piloto destino realiza cambios anticipados o tardíos, especialmente antes de curva o al salir de ellas. "
                "Detecta errores de sincronización que puedan comprometer la aceleración o generar rebotes de motor."
            ),
            "Speed": (
                "Compara las curvas de velocidad de ambos pilotos. "
                "En rectas, verifica si el piloto destino alcanza menor velocidad punta. "
                "En curvas, revisa si la velocidad mínima (apex) es más baja, lo cual puede indicar frenadas excesivas o mal trazado. "
                "Detecta si acelera tarde al salir de curvas o si pierde velocidad por trayectorias largas."
            ),
            "TrackMap": (
                "Analiza las líneas de trayectoria de ambos pilotos a lo largo de todo el circuito. "
                "Identifica si el piloto destino recorre más distancia, se abre demasiado en curvas o tiene líneas irregulares. "
                "Evalúa consistencia, eficiencia de radios de giro, y cómo posiciona el coche en entrada y salida de curvas. "
                "Si se sospechan correcciones de volante o sobreconducción por la forma de la trazada, indícalo incluso si no se ve el volante."
            ),
            "Steering": (
                "Analiza cómo gira el volante el piloto destino a lo largo de la vuelta, especialmente en entrada, apex y salida de curva. "
                "Detecta si hay giros demasiado bruscos, correcciones múltiples o signos de sobreconducción. "
                "Evalúa si el ángulo de giro coincide con una trazada limpia o si denota inseguridad o agresividad excesiva. "
                "Indica si el estilo de dirección puede estar afectando el ritmo o la línea óptima."
            )
        }
        graph_prompt = graph_instructions.get(graph_type, "Describe diferencias clave en el comportamiento entre ambas líneas.")

        # --- Construcción del Prompt completo ---
        prompt_text = f"""
Eres **Race Coach Pro**, un ingeniero de pista virtual especializado en análisis de telemetría y simracing de alto nivel.

Estás analizando una imagen comparativa llamada **{image_filename}**, correspondiente al circuito **{context.get('track_name', 'N/A')}**. Esta imagen fue generada desde software profesional tipo MoTeC i2pro y representa el canal: **{graph_type.upper()}**.

🔹 **Piloto objetivo (línea {context['target_color']}):** {context['target_driver']} — Mejor vuelta: {context['target_lap_time']}  
🔸 **Piloto referencia (línea {context['reference_color']}):** {context['reference_driver']} — Mejor vuelta: {context['reference_lap_time']}  
📉 **Delta entre pilotos:** {context.get('delta_time', 'N/A')} segundos

---

🎯 **Tarea:**  
Compara la actuación de ambos pilotos en esta imagen de telemetría.  
{graph_prompt}

📌 **Objetivo:**  
Detecta diferencias claras, errores cometidos y oportunidades específicas de mejora para **{context['target_driver']}** (línea {context['target_color']}).  
Ofrece un análisis técnico y accionable. Indica exactamente **qué hace diferente** el piloto referencia que el destino debería ajustar.

⚠️ **IMPORTANTE:**  
No describas el software ni su interfaz. No repitas obviedades visuales. No hagas suposiciones sin base en la imagen.  
Concéntrate en diferencias clave y en qué mejorar desde la perspectiva de coaching profesional.

Responde de forma estructurada y precisa.
""".strip()

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {"type": "image_url", "image_url": {"url": image_data_url}}
                ]
            }
        ]

        print(f"Enviando petición VLM a {endpoint} (Timeout: 300s)...")
        response = requests.post(
            f"{endpoint}/v1/chat/completions",
            headers={"Content-Type": "application/json"},
            json={
                "model": model_name,
                "messages": messages,
                "max_tokens": 1500,
                "temperature": 0.3,
                "stream": False
            },
            timeout=300
        )
        print(f"[{graph_type}] VLM Response Status Code: {response.status_code}")
        response.raise_for_status()

        # --- Procesamiento de la respuesta ---
        response_text = response.text
        try:
            response_json = json.loads(response_text)
            choices = response_json.get("choices", [])
            if choices and isinstance(choices, list):
                content = choices[0].get("message", {}).get("content")
                if content and isinstance(content, str):
                    print(f"[{graph_type}] Análisis VLM OK.")
                    return content.strip()

            print(f"¡¡¡ ADVERTENCIA [{graph_type}] !!! Contenido VLM vacío/inesperado.")
            print(f"JSON Recibido: {response_json}")
            return f"[Error: Contenido VLM vacío/inesperado ({graph_type})]"

        except json.JSONDecodeError as json_err:
            print(f"¡¡¡ ERROR [{graph_type}] !!! Error decodificando JSON: {json_err}")
            print(f"Texto de respuesta (parcial): {response_text[:1000]}")
            return f"[Error: JSON inválido recibido ({graph_type})]"

    except Exception as e:
        print(f"¡¡¡ ERROR [{graph_type}] !!! Excepción general: {e}")
        traceback.print_exc()
        return f"[Error: Excepción durante análisis VLM ({graph_type})]"



# --- Función de Síntesis Final (PROMPT MEJORADO - Versión Final) ---
def synthesize_driving_advice(
    initial_context, brake_analysis, throttle_analysis, gear_analysis,
    speed_analysis, trackmap_analysis, steering_analysis=None, model_endpoint=None, model_name=DEFAULT_TEXT_MODEL ):
    """Genera resumen final conciso estilo Race Coach Pro."""
    endpoint = model_endpoint or get_lm_studio_endpoint()
    if not endpoint: return "[Error: Endpoint no determinado para síntesis]"
    required_keys = ["target_driver", "reference_driver", "faster_driver", "slower_driver", "target_lap_time", "reference_lap_time"]
    if not initial_context or not all(initial_context.get(k) for k in required_keys): return "[Error: Contexto incompleto para síntesis]"

    print(f"Iniciando síntesis final con {model_name}...")

    # Construir texto con los análisis disponibles
    analysis_text = ""; analysis_count = 0
    analysis_map = {"Freno": brake_analysis, "Acelerador": throttle_analysis, "Marcha": gear_analysis, "Velocidad": speed_analysis, "Trazada": trackmap_analysis, "Volante": steering_analysis }
    for key, analysis in analysis_map.items():
        status = "N/A o Error."
        if analysis and isinstance(analysis, str) and not analysis.startswith('['): status = analysis; analysis_count += 1
        analysis_text += f"--- Análisis de {key} ---\n{status}\n\n"
    if analysis_count == 0: return "[Error: No hay análisis válidos para la síntesis]" # No llamar a LLM si no hay nada que sintetizar

    # Prompt de síntesis final
    synthesis_prompt = (
        f"Eres **Race Coach Pro**, un ingeniero de pista virtual especializado en análisis de simracing.\n"
        f"Tu tarea es sintetizar los análisis previos y generar un resumen final de coaching para el piloto más lento.\n\n"
        
        f"📍 **Contexto de la Comparación:**\n"
        f"- Pista: {initial_context.get('track_name', 'N/A')}\n"
        f"- Piloto Destino (más lento, línea azul): {initial_context['target_driver']} (Vuelta: {initial_context['target_lap_time']})\n"
        f"- Piloto Referencia (más rápido): {initial_context['reference_driver']} (Vuelta: {initial_context['reference_lap_time']})\n"
        f"- Delta total: {initial_context.get('delta_time', 'N/A')} s\n\n"

        f"📊 **Análisis IA por Canal (Generado automáticamente por IA de Visión):**\n\n"
        f"{analysis_text.strip()}\n\n"
        f"---\n\n"

        f"🎯 **Objetivo del Resumen:**\n"
        f"Redacta un resumen técnico y accionable con los **4 a 5 puntos de mejora más relevantes** para que {initial_context['slower_driver']} reduzca la diferencia con {initial_context['faster_driver']}.\n"
        f"Usa un lenguaje profesional, claro y directo. Evita repetir literalmente lo anterior. Prioriza las recomendaciones que aparezcan en múltiples gráficos.\n\n"

        f"✅ **Estructura sugerida para cada consejo:**\n"
        f"- Breve título del punto.\n"
        f"- Qué diferencia observaste.\n"
        f"- Qué debería hacer el piloto para mejorar.\n\n"

        f"📌 Dirige los consejos directamente a {initial_context['slower_driver']}. Mantén el tono de ingeniero de pista técnico.\n\n"

        f"**Resumen de Coaching para {initial_context['slower_driver']}:**"
    )

    try:
        response = requests.post(
            f"{endpoint}/v1/chat/completions", headers={"Content-Type": "application/json"},
            json={ "model": model_name, "messages": [{"role": "user", "content": synthesis_prompt}],
                   "max_tokens": 1500, "temperature": 0.5, "stream": False },
            timeout=300 )
        if response.status_code != 200: print(f"Error Síntesis: Status={response.status_code}"); return f"[Error servidor LLM ({response.status_code}) Síntesis]"
        response_json = response.json()
        try:
            summary_content = response_json.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
            if not summary_content: raise ValueError("Contenido vacío")
            print("Síntesis OK."); return summary_content
        except (KeyError, IndexError, TypeError, ValueError) as e: print(f"Respuesta Síntesis inesperada: {response_json}. Error: {e}"); return "[Error: Respuesta LLM inesperada (Síntesis)]"
    except requests.exceptions.Timeout: print("Error Síntesis: Timeout"); return "[Error: Timeout LLM Síntesis]"
    except requests.exceptions.RequestException as e: print(f"Error Síntesis: Red - {e}"); return f"[Error red LLM Síntesis]"
    except Exception as e: print(f"Error Síntesis inesperado: {e}"); traceback.print_exc(); return f"[Error inesperado Síntesis]"


# --- Función de Test de Conexión ---
def test_connection( model_endpoint=None, model_name=DEFAULT_TEXT_MODEL ):
    """Prueba la conexión básica con el servidor LLM."""
    endpoint = model_endpoint or get_lm_studio_endpoint()
    if not endpoint: return "[Error: Endpoint no determinado test_connection]"
    print(f"Intentando conectar a: {endpoint} con modelo: {model_name}")
    try:
        response = requests.post(
            f"{endpoint}/v1/chat/completions", headers={"Content-Type": "application/json"},
            json={ "model": model_name, "messages": [{"role": "user", "content": "Responde solamente cuanto es 9+1, sin nigún detalle o texto extra"}],
                   "temperature": 0.1, "max_tokens": 20, "stream": False },
            timeout=60 ) # Timeout más Largo
        response.raise_for_status()
        response_json = response.json()
        content = response_json.get("choices", [{}])[0].get("message", {}).get("content", "")
        return f"Conexión OK. Respuesta: {content[:60]}..."
    except requests.exceptions.Timeout: return f"Error Conexión: Timeout (60s)."
    except requests.exceptions.RequestException as e: status = e.response.status_code if hasattr(e, 'response') and e.response is not None else "N/A"; return f"Error Conexión/HTTP ({status}): {str(e)[:100]}..."
    except Exception as e: print(f"Error test_connection: {e}"); return f"Error test_connection ({type(e).__name__})."