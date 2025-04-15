# llm_integration.py (Revisado para evitar NameError en importación)

import os
import base64
import requests
import json
import subprocess
import sys
import traceback
import pytesseract
from PIL import Image
import io
import re # Para OCR parsing

# --- Constantes Simples ---
# Definimos los nombres de modelo como constantes simples
DEFAULT_VLM_MODEL = "llava-v1.6-mistral-7b" # O el nombre exacto que cargaste
DEFAULT_TEXT_MODEL = "meta-llama-3-8b-instruct" # O el nombre que uses para texto
DEFAULT_PORT = 1234 # Puerto por defecto de LM Studio

# --- CONFIGURACIÓN TESSERACT (SOLO SI NO ESTÁ EN EL PATH) ---
# Descomenta y ajusta la ruta si no añadiste Tesseract al PATH de Windows
# TESSERACT_CMD_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# try:
#     # Intenta establecer la ruta del comando Tesseract
#     pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD_PATH
# except AttributeError:
#      print("Advertencia: Atributo tesseract_cmd no encontrado (¿versión pytesseract?). Asegúrate de que Tesseract esté en el PATH.")
# except FileNotFoundError:
#      print(f"ERROR CRÍTICO: Tesseract no encontrado en la ruta especificada: {TESSERACT_CMD_PATH}")
#      print("             Asegúrate de que Tesseract OCR esté instalado y la ruta sea correcta, o añádelo al PATH.")
# except Exception as e:
#      print(f"Error configurando ruta Tesseract: {e}")


# --- Funciones de Detección de Endpoint (Modificado) ---
def detect_windows_host_ip():
    """
    Detecta la IP del host Windows desde WSL2 o devuelve IP local.
    (Mantenido de tu versión anterior, con mejoras menores)
    """
    try:
        # Intenta obtener la IP desde WSL2 buscando 'via'
        output = subprocess.check_output("ip route show default", shell=True, stderr=subprocess.DEVNULL).decode()
        parts = output.split()
        ip_index = -1
        if 'via' in parts:
            ip_index = parts.index('via') + 1
            if ip_index < len(parts):
                return parts[ip_index] # IP encontrada vía 'via'

        # Fallback si no se encontró 'via' o si no es WSL: intentar 'hostname -I' (Linux genérico)
        try:
            output_hostname = subprocess.check_output("hostname -I", shell=True, stderr=subprocess.DEVNULL).decode()
            first_ip = output_hostname.split()[0]
            if first_ip:
                print(f"Advertencia: No se detectó IP 'via' en 'ip route'. Usando primera IP de 'hostname -I': {first_ip}")
                return first_ip
        except Exception:
             pass # Ignorar error si hostname -I falla

        # Si todo falla, usar localhost
        print("Advertencia: No se pudo extraer la IP de 'ip route' ni 'hostname -I'. Usando 127.0.0.1.")
        return "127.0.0.1"

    except FileNotFoundError:
        # Comandos no encontrados (probablemente no es Linux/WSL)
        print("Advertencia: Comandos 'ip' o 'hostname' no encontrados (¿No es Linux/WSL?). Usando 127.0.0.1.")
        return "127.0.0.1"
    except Exception as e:
        print(f"Advertencia: Error inesperado detectando IP ({e}). Usando 127.0.0.1.")
        return "127.0.0.1"

_cached_endpoint = None # Variable global para cachear el endpoint una vez detectado

def get_lm_studio_endpoint():
    """
    Detecta y devuelve la URL completa del endpoint de LM Studio, cacheando el resultado.
    Se llama internamente por las funciones que lo necesitan.
    """
    global _cached_endpoint
    if _cached_endpoint is None:
        host_ip = detect_windows_host_ip()
        _cached_endpoint = f"http://{host_ip}:{DEFAULT_PORT}"
        print(f"Endpoint de LM Studio determinado como: {_cached_endpoint}") # Útil para depuración
    return _cached_endpoint


# --- Funciones de Utilidad (Imagen) ---
def encode_image_to_base64(image_source):
    """Codifica una imagen (ruta de archivo o objeto PIL.Image) a base64 string."""
    # ... (código de encode_image_to_base64 sin cambios, como en la respuesta anterior) ...
    try:
        if isinstance(image_source, str): # Es una ruta de archivo
            if not os.path.exists(image_source):
                 raise FileNotFoundError(f"Archivo no encontrado: {image_source}")
            with open(image_source, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode('utf-8')
        elif isinstance(image_source, Image.Image): # Es un objeto PIL
            buffer = io.BytesIO()
            # Guarda en formato JPEG para eficiencia (o PNG si prefieres)
            # Asegúrate de que el formato sea compatible con lo que espera el VLM
            image_format = 'JPEG' if image_source.mode == 'RGB' else 'PNG'
            image_source.save(buffer, format=image_format)
            return base64.b64encode(buffer.getvalue()).decode('utf-8')
        else:
            raise TypeError("image_source debe ser una ruta de archivo (str) o un objeto PIL.Image")
    except FileNotFoundError as e:
        print(f"Error en encode_image_to_base64: {e}")
        raise
    except Exception as e:
        print(f"Error inesperado en encode_image_to_base64: {e}")
        raise

# --- Función de Extracción de Contexto (OCR) ---
def extract_context_from_summary_image(image_path):
    """
    Extrae el contexto (pilotos, tiempos, delta, pista, colores) de la imagen de resumen usando OCR.
    Devuelve un diccionario con los datos encontrados o None si falla.
    AJUSTA LAS EXPRESIONES REGULARES A TU FORMATO DE IMAGEN.
    """
    # ... (código de extract_context_from_summary_image sin cambios, como en la respuesta anterior) ...
    print(f"Intentando extraer contexto con OCR de: {image_path}")
    context_data = {
        "track_name": None, "driver1_name": None, "driver1_color": None, "driver1_laptime": None,
        "driver2_name": None, "driver2_color": None, "driver2_laptime": None, "delta_time": None,
        "faster_driver": None, "slower_driver": None, "faster_color": None, "slower_color": None
    }
    try:
        # Asegúrate de manejar errores si Tesseract no está configurado
        try:
             raw_text = pytesseract.image_to_string(Image.open(image_path), lang='eng+spa')
        except pytesseract.TesseractNotFoundError:
             print("\nERROR CRÍTICO: El comando 'tesseract' no se encontró.")
             print("1. Asegúrate de que Tesseract OCR esté instalado en tu sistema.")
             print("2. Añade la carpeta de instalación de Tesseract a la variable de entorno PATH.")
             print("3. Opcionalmente, descomenta y configura TESSERACT_CMD_PATH al inicio de este archivo.")
             return None
        except Exception as ocr_err:
             print(f"Error durante la ejecución de Tesseract OCR: {ocr_err}")
             return None

        print("--- Texto OCR Crudo ---"); print(raw_text); print("----------------------")

        # --- Parsear el texto crudo (AJUSTAR PATRONES SEGÚN NECESARIO) ---
        # Pista
        match = re.search(r"(?:Track|Circuito):?\s*(.+)", raw_text, re.IGNORECASE)
        if match: context_data["track_name"] = match.group(1).strip()

        # Pilotos/Tiempos/Colores (Ejemplo muy específico, AJUSTAR)
        driver_lines = re.findall(r"(.+?)\s*\((Red|Blue|Rojo|Azul)\).*Best Lap:?\s*(\d{1,2}:\d{2}\.\d{3})", raw_text, re.IGNORECASE | re.MULTILINE)

        if len(driver_lines) >= 2:
            def normalize_color(color_str):
                 color_lower = color_str.lower()
                 if color_lower in ["red", "rojo"]: return "Red"
                 if color_lower in ["blue", "azul"]: return "Blue"
                 return None # O manejar otros colores si es necesario

            context_data["driver1_name"] = driver_lines[0][0].strip()
            context_data["driver1_color"] = normalize_color(driver_lines[0][1])
            context_data["driver1_laptime"] = driver_lines[0][2]

            context_data["driver2_name"] = driver_lines[1][0].strip()
            context_data["driver2_color"] = normalize_color(driver_lines[1][1])
            context_data["driver2_laptime"] = driver_lines[1][2]

        # Delta Time
        match = re.search(r"Delta:?\s*([-+]?\s?\d{1,2}\.\d{3})", raw_text, re.IGNORECASE)
        if match: context_data["delta_time"] = match.group(1).replace(" ","") # Quitar espacios

        # Determinar rápido/lento (Conversión a segundos para comparación robusta)
        def time_to_seconds(time_str):
            try:
                parts = time_str.split(':')
                if len(parts) == 2: # MM:SS.ms
                    minutes = int(parts[0])
                    seconds_ms = parts[1].split('.')
                    seconds = int(seconds_ms[0])
                    millis = int(seconds_ms[1])
                    return minutes * 60 + seconds + millis / 1000.0
                elif len(parts) == 1: # Solo segundos? SS.ms
                     seconds_ms = parts[0].split('.')
                     seconds = int(seconds_ms[0])
                     millis = int(seconds_ms[1])
                     return seconds + millis / 1000.0
                return float('inf') # Formato no reconocido
            except:
                return float('inf') # Error en conversión

        time1 = time_to_seconds(context_data["driver1_laptime"]) if context_data["driver1_laptime"] else float('inf')
        time2 = time_to_seconds(context_data["driver2_laptime"]) if context_data["driver2_laptime"] else float('inf')

        if time1 != float('inf') and time2 != float('inf'):
            if time1 <= time2:
                context_data["faster_driver"], context_data["slower_driver"] = context_data["driver1_name"], context_data["driver2_name"]
                context_data["faster_color"], context_data["slower_color"] = context_data["driver1_color"], context_data["driver2_color"]
            else:
                context_data["faster_driver"], context_data["slower_driver"] = context_data["driver2_name"], context_data["driver1_name"]
                context_data["faster_color"], context_data["slower_color"] = context_data["driver2_color"], context_data["driver1_color"]

        # --- Validación ---
        required_keys = ["driver1_name", "driver1_color", "driver1_laptime", "driver2_name", "driver2_color", "driver2_laptime", "faster_driver", "slower_driver", "faster_color", "slower_color"]
        if all(context_data.get(k) is not None for k in required_keys):
             print("Contexto extraído con éxito:"); print(json.dumps(context_data, indent=2))
             return context_data
        else:
             print("Error: No se pudo extraer toda la información requerida."); print("Datos Parciales:", json.dumps(context_data, indent=2)); return None

    except FileNotFoundError:
        print(f"Error OCR: Archivo de imagen no encontrado en {image_path}")
        return None
    except Exception as e:
        print(f"Error inesperado durante OCR o parseo: {e}"); traceback.print_exc(); return None


# --- Función de Análisis VLM (Usa get_lm_studio_endpoint) ---
def analyze_telemetry_comparison_graph(
    image_path,
    graph_type, # "Brake", "Throttle", "Gear"
    context, # El diccionario devuelto por extract_context_from_summary_image
    model_endpoint=None, # Permitir override, pero normalmente usará el detectado
    model_name=DEFAULT_VLM_MODEL # Usa constante simple
):
    """Analiza gráfico VLM usando contexto y obteniendo endpoint internamente."""
    # --- Obtener endpoint ---
    endpoint = model_endpoint or get_lm_studio_endpoint()
    if not endpoint: return "[Error: No se pudo determinar el endpoint de LM Studio]"

    image_filename = os.path.basename(image_path) if image_path else "N/A"
    # ... (resto del código de analyze_telemetry_comparison_graph SIN CAMBIOS,
    #      ya que usará la variable 'endpoint' definida arriba.
    #      Asegúrate de que la llamada a requests.post use f"{endpoint}/v1/chat/completions"
    #      y que el JSON incluya "model": model_name) ...
    if not context or not all(k in context for k in ["faster_driver", "slower_driver", "faster_color", "slower_color"]):
         print(f"Error: Contexto inválido o incompleto proporcionado para analizar {image_filename}"); return "[Error: Contexto inicial inválido o incompleto]"
    print(f"Analizando gráfico de {graph_type}: {image_filename} con modelo {model_name}")
    print(f"Contexto: {context['slower_driver']} ({context['slower_color']}) vs {context['faster_driver']} ({context['faster_color']})")
    try:
        base64_image = encode_image_to_base64(image_path)
        image_format = "jpeg" if image_path.lower().endswith((".jpg", ".jpeg")) else "png"
        image_data_url = f"data:image/{image_format};base64,{base64_image}"
        # Prompts (igual que antes)
        prompt_base = (
            f"Eres un ingeniero de datos y coach de pilotos experto en MoTeC i2. Analiza SOLO el gráfico de '{graph_type}' vs Distancia de la imagen proporcionada.\n\n"
            f"**Contexto del Análisis:**\n"
            f"* Pista: {context.get('track_name', 'N/A')}\n"
            f"* Piloto Más Rápido: {context['faster_driver']} (Traza: {context['faster_color']})\n"
            f"* Piloto Más Lento: {context['slower_driver']} (Traza: {context['slower_color']})\n"
            f"* Delta Time (aprox): {context.get('delta_time', 'N/A')} s\n\n"
            f"**Tu Tarea Detallada (Enfocada en {graph_type}):**\n"
            f"1. Compara las trazas de {context['faster_driver']} ({context['faster_color']}) y {context['slower_driver']} ({context['slower_color']}) en este gráfico de {graph_type}.\n"
        )
        if graph_type == "Brake": prompt_details = (...); # igual que antes
        elif graph_type == "Throttle": prompt_details = (...); # igual que antes
        elif graph_type == "Gear": prompt_details = (...); # igual que antes
        else: prompt_details = "2. Realiza un análisis comparativo general.\n\n**Análisis Comparativo General:**"
        # --- Bloques de prompt_details (copiados de respuesta anterior) ---
        if graph_type == "Brake":
             prompt_details = (
                 f"2. Identifica diferencias clave en puntos de inicio de frenada, presión máxima/forma, duración y forma de liberación.\n"
                 f"3. Proporciona 1-2 consejos específicos y accionables sobre la FRENADA para {context['slower_driver']}, indicando rangos de distancia aproximados.\n\n"
                 f"**Análisis Comparativo (Freno) y Consejos para {context['slower_driver']}:**"
             )
        elif graph_type == "Throttle":
             prompt_details = (
                 f"2. Identifica diferencias clave en el primer punto de aplicación del acelerador, la rapidez/progresividad de la aplicación, y si levanta el pie innecesariamente.\n"
                 f"3. Proporciona 1-2 consejos específicos y accionables sobre el ACELERADOR para {context['slower_driver']}, indicando rangos de distancia aproximados.\n\n"
                 f"**Análisis Comparativo (Acelerador) y Consejos para {context['slower_driver']}:**"
             )
        elif graph_type == "Gear":
             prompt_details = (
                 f"2. Compara los puntos donde cambian de marcha y la marcha utilizada en diferentes secciones. ¿Parece {context['slower_driver']} estar en la marcha correcta?\n"
                 f"3. Proporciona 1-2 consejos específicos y accionables sobre el USO DE MARCHAS para {context['slower_driver']}, indicando rangos de distancia aproximados.\n\n"
                 f"**Análisis Comparativo (Marcha) y Consejos para {context['slower_driver']}:**"
             )
        else: # Fallback por si acaso
             prompt_details = "2. Realiza un análisis comparativo general.\n\n**Análisis Comparativo General:**"
        # --- Fin bloques prompt_details ---
        prompt_text = prompt_base + prompt_details
        messages = [ {"role": "user", "content": [ {"type": "text", "text": prompt_text}, {"type": "image_url", "image_url": {"url": image_data_url}} ] } ]
        print(f"Enviando petición VLM a {endpoint} con modelo {model_name}...")
        response = requests.post(
            f"{endpoint}/v1/chat/completions", # Usa la variable endpoint
            headers={"Content-Type": "application/json"},
            json={ "model": model_name, "messages": messages, "max_tokens": 400, "temperature": 0.3, "stream": False },
            timeout=180
        )
        # ... (manejo de respuesta/errores igual que antes) ...
        if response.status_code != 200:
            error_details = f"Error en petición VLM ({graph_type}) para {image_filename}: Status={response.status_code}, Reason={response.reason}, Body={response.text[:500]}"
            print(error_details); return f"[Error servidor VLM ({response.status_code}) para {graph_type}]"
        response_json = response.json()
        if ("choices" in response_json and isinstance(response_json.get("choices"), list) and len(response_json["choices"]) > 0 and
            "message" in response_json["choices"][0] and "content" in response_json["choices"][0].get("message", {})):
            analysis_content = response_json["choices"][0]["message"]["content"].strip()
            print(f"Análisis VLM para {graph_type} recibido."); return analysis_content
        else:
            print(f"Respuesta inesperada VLM ({graph_type}) para {image_filename}: {response_json}"); return f"[Error: Respuesta VLM inesperada ({graph_type})]"
    except FileNotFoundError: print(f"Error VLM: Archivo no encontrado - {image_path}"); return f"[Error: Archivo no encontrado - {image_path}]"
    except requests.exceptions.Timeout: print(f"Error VLM ({graph_type}): Timeout"); return f"[Error: Timeout VLM para {graph_type}]"
    except requests.exceptions.RequestException as e: print(f"Error VLM ({graph_type}): Conexión/Red - {e}"); return f"[Error de red VLM para {graph_type}]"
    except Exception as e: print(f"Error inesperado en VLM ({graph_type}): {type(e).__name__} - {e}"); traceback.print_exc(); return f"[Error inesperado VLM para {graph_type}]"


# --- Función de Síntesis Final (Usa get_lm_studio_endpoint) ---
def synthesize_driving_advice(
    initial_context,
    brake_analysis,
    throttle_analysis,
    gear_analysis,
    model_endpoint=None, # Permitir override
    model_name=DEFAULT_TEXT_MODEL # Usa constante simple
):
    """Genera resumen final usando LLM Texto y obteniendo endpoint internamente."""
     # --- Obtener endpoint ---
    endpoint = model_endpoint or get_lm_studio_endpoint()
    if not endpoint: return "[Error: No se pudo determinar el endpoint de LM Studio para la síntesis]"

    if not initial_context: return "[Error: Contexto inicial no disponible para la síntesis]"
    print(f"Iniciando síntesis final con modelo {model_name} en {endpoint}...")
    # ... (resto del código de synthesize_driving_advice SIN CAMBIOS,
    #      asegúrate de que la llamada a requests.post use f"{endpoint}/v1/chat/completions"
    #      y que el JSON incluya "model": model_name) ...
    synthesis_prompt = (
        f"Eres un coach de pilotos de carreras profesional generando un resumen final.\n\n"
        f"**Contexto General:**\n"
        f"* Pista: {initial_context.get('track_name', 'N/A')}\n"
        f"* Piloto Rápido: {initial_context.get('faster_driver', 'N/A')} ({initial_context.get('faster_color', 'N/A')})\n"
        f"* Piloto Lento: {initial_context.get('slower_driver', 'N/A')} ({initial_context.get('slower_color', 'N/A')})\n"
        f"* Delta Tiempo: {initial_context.get('delta_time', 'N/A')} s\n\n"
        f"**Análisis Detallados de Gráficos (Realizados por IA de Visión):**\n\n"
        f"--- Análisis de Freno ---\n{brake_analysis if brake_analysis and not brake_analysis.startswith('[Error') else 'No disponible o Error.'}\n\n"
        f"--- Análisis de Acelerador ---\n{throttle_analysis if throttle_analysis and not throttle_analysis.startswith('[Error') else 'No disponible o Error.'}\n\n"
        f"--- Análisis de Marcha ---\n{gear_analysis if gear_analysis and not gear_analysis.startswith('[Error') else 'No disponible o Error.'}\n\n"
        f"**Instrucciones para el Resumen Final:**\n"
        f"1.  NO repitas literalmente los análisis detallados anteriores.\n"
        f"2.  Basándote en el contexto y los análisis válidos, escribe un resumen CONCISO (máximo 3-4 puntos clave) de los consejos de pilotaje más importantes para que '{initial_context.get('slower_driver', 'el piloto más lento')}' mejore y reduzca la diferencia de tiempo.\n"
        f"3.  Enfócate en recomendaciones accionables y claras.\n"
        f"4.  Dirígete directamente al piloto más lento si es posible.\n\n"
        f"**Resumen de Consejos para {initial_context.get('slower_driver', 'el piloto más lento')}:**"
    )
    try:
        response = requests.post(
            f"{endpoint}/v1/chat/completions", # Usa la variable endpoint
            headers={"Content-Type": "application/json"},
            json={ "model": model_name, "messages": [{"role": "user", "content": synthesis_prompt}], "max_tokens": 300, "temperature": 0.5, "stream": False },
            timeout=120
        )
        # ... (manejo de respuesta/errores igual que antes) ...
        if response.status_code != 200:
             error_details = f"Error en petición Síntesis: Status={response.status_code}, Reason={response.reason}, Body={response.text[:500]}"
             print(error_details); return f"[Error servidor LLM ({response.status_code}) para Síntesis]"
        response_json = response.json()
        if ("choices" in response_json and isinstance(response_json.get("choices"), list) and len(response_json["choices"]) > 0 and
            "message" in response_json["choices"][0] and "content" in response_json["choices"][0].get("message", {})):
            summary_content = response_json["choices"][0]["message"]["content"].strip()
            print("Síntesis final recibida."); return summary_content
        else:
             print(f"Respuesta inesperada Síntesis: {response_json}"); return "[Error: Respuesta LLM inesperada (Síntesis)]"
    except requests.exceptions.Timeout: print("Error Síntesis: Timeout"); return "[Error: Timeout LLM para Síntesis]"
    except requests.exceptions.RequestException as e: print(f"Error Síntesis: Conexión/Red - {e}"); return f"[Error de red LLM para Síntesis]"
    except Exception as e: print(f"Error inesperado en Síntesis: {type(e).__name__} - {e}"); traceback.print_exc(); return f"[Error inesperado Síntesis]"


# --- Función de Test de Conexión (Usa get_lm_studio_endpoint) ---
def test_connection(
    model_endpoint=None, # Permitir override
    model_name=DEFAULT_TEXT_MODEL # Usa constante simple
):
    """Prueba la conexión básica con el servidor LLM obteniendo endpoint internamente."""
    # --- Obtener endpoint ---
    endpoint = model_endpoint or get_lm_studio_endpoint()
    if not endpoint: return "[Error: No se pudo determinar el endpoint de LM Studio para test_connection]"

    print(f"Intentando conectar a: {endpoint} con modelo: {model_name}")
    response = None; json_response = None # Inicializar fuera del try
    try:
        # ... (resto del código de test_connection SIN CAMBIOS,
        #      asegúrate de que la llamada a requests.post use f"{endpoint}/v1/chat/completions"
        #      y que el JSON incluya "model": model_name) ...
        response = requests.post(
            f"{endpoint}/v1/chat/completions", # Usa la variable endpoint
            headers={"Content-Type": "application/json"},
            json={ "model": model_name, "messages": [{"role": "user", "content": "¿Puedes confirmar que estás operativo?"}],
                   "temperature": 0.1, "max_tokens": 20, "top_p": 1.0, "stream": False },
            timeout=30
        )
        response.raise_for_status() # Lanza excepción para errores HTTP
        json_response = response.json()
        # ... (validación de respuesta json_response igual que antes) ...
        if isinstance(json_response, dict) and "choices" in json_response:
             choices = json_response.get("choices")
             if (isinstance(choices, list) and len(choices) > 0 and
                 isinstance(choices[0], dict) and "message" in choices[0]):
                 message = choices[0].get("message")
                 if isinstance(message, dict) and "content" in message:
                      return f"Conexión OK. Modelo responde: {message.get('content', '[vacío]')[:50]}..." # Acortar respuesta larga
        return f"Conexión OK (200), pero formato respuesta inesperado. Keys: {list(json_response.keys()) if isinstance(json_response, dict) else 'No es dict'}"

    except requests.exceptions.Timeout: return f"Error Conexión: Timeout (30s)."
    except requests.exceptions.RequestException as e:
         status_code_str = e.response.status_code if hasattr(e, 'response') and e.response is not None else "N/A"
         return f"Error Conexión/HTTP ({status_code_str}): {str(e)}"
    except json.JSONDecodeError:
         body_str = response.text[:200] if response is not None else "N/A"; return f"Error Conexión: Respuesta no es JSON válido. Body: {body_str}..."
    except Exception as e: print(f"Error inesperado en test_connection: {type(e).__name__} - {e}"); traceback.print_exc(); return f"Error inesperado en test_connection ({type(e).__name__})."