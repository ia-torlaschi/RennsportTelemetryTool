# main.py (vFinal Definitiva - OCR Tiempos + Input Ref + 5 Gráficos + Func. Original)

import pandas as pd
import numpy as np
import os
import sys
import traceback
import json # Para imprimir contexto
import re  # Para validar formato tiempo

# --- Importar funciones de plotting y carga ---
try:
    # Asegúrate que estos archivos .py estén en el mismo directorio o PYTHONPATH
    from data_loader import load_telemetry_csv
    from plotter import plot_lap_speed_profile, plot_lap_inputs, plot_lap_engine, plot_comparison_dashboard
except ImportError as e:
    print(f"Error FATAL importando data_loader/plotter: {e}")
    print("Asegúrate que data_loader.py y plotter.py estén en el directorio correcto.")
    sys.exit(1)

# --- Importar funciones de IA (Actualizado nombre función OCR y añadido time_str_to_seconds) ---
try:
    # Asegúrate que llm_integration.py esté en el mismo directorio o PYTHONPATH
    from llm_integration import (
        extract_context_from_laptime_image, # Nombre función OCR actualizada
        analyze_telemetry_comparison_graph,
        synthesize_driving_advice,
        test_connection,
        DEFAULT_VLM_MODEL,
        DEFAULT_TEXT_MODEL,
        time_str_to_seconds # Importar helper para validar/comparar tiempos
    )
    AI_ENABLED = True
except ImportError as e:
    print(f"\nADVERTENCIA: Importación IA falló: {e}. Funcionalidad IA deshabilitada.")
    AI_ENABLED = False
except Exception as e_llm:
     print(f"\nERROR inesperado importando llm_integration: {e_llm}")
     AI_ENABLED = False


# --- Funciones Auxiliares (format_time - sin cambios) ---
def format_time(seconds):
    """Formatea segundos en MM:SS.ms"""
    if pd.isna(seconds) or not np.isfinite(seconds) or seconds < 0: return "N/A"
    if isinstance(seconds, np.timedelta64): seconds = seconds.total_seconds()
    elif not isinstance(seconds, (int, float, np.number)): return "Invalid Type"
    minutes = int(seconds // 60); secs = int(seconds % 60); millis = int(round((seconds - minutes * 60 - secs) * 1000))
    # Corrección si millis >= 1000
    if millis >= 1000: secs += 1; millis = 0
    if secs >= 60: minutes +=1; secs -= 60
    return f"{minutes:02d}:{secs:02d}.{millis:03d}"


# --- Lógica de Cálculo de Vueltas (Copiada de tu versión v11) ---
def calculate_laps_improved(df, min_lap_time_threshold=60):
    """Calcula tiempos de vuelta basado en fin vuelta anterior."""
    required_cols = ['Time', 'Lap', 'IsLapValid']
    if not all(col in df.columns for col in required_cols): raise ValueError(f"Faltan cols: {[c for c in required_cols if c not in df.columns]}")
    df = df.sort_values('Time').reset_index(drop=True)
    if 'IsLapValid' not in df.columns: print("Adv: 'IsLapValid' no encontrada."); df['IsLapValid'] = True
    elif df['IsLapValid'].dtype != bool:
        try: # Intenta mapear valores comunes a booleano
             valid_map = {'True': True, 'False': False, '1': True, '0': False, 1: True, 0: False, 1.0: True, 0.0: False, True: True, False: False}
             original_type = df['IsLapValid'].dtype; df['IsLapValid'] = df['IsLapValid'].map(valid_map).fillna(False).astype(bool)
             if not pd.api.types.is_bool_dtype(original_type): print("'IsLapValid' convertida a bool.")
        except Exception as e: print(f"Adv: conversión 'IsLapValid': {e}"); df['IsLapValid'] = df['IsLapValid'].apply(lambda x: str(x).lower() in ['true', '1', '1.0'])
    lap_change_indices = df[df['Lap'] != df['Lap'].shift(1)].index
    cut_indices = pd.Index([0]).union(lap_change_indices - 1).union(pd.Index([len(df) - 1])).unique().sort_values()
    cut_indices = cut_indices[cut_indices >= 0]
    if len(cut_indices) < 3: print("Adv: No suficientes cambios de vuelta."); return pd.DataFrame()
    lap_data = []
    for i in range(len(cut_indices) - 1):
        start_idx = cut_indices[i] + 1 if i > 0 else 0; end_idx = cut_indices[i+1]
        if start_idx >= len(df) or end_idx < start_idx: continue
        # Manejo de posible error si 'Lap' no es numérico o tiene NaN en el slice
        try:
            lap_num = int(df.loc[start_idx, 'Lap'])
        except (ValueError, TypeError):
            print(f"Adv: Valor no numérico o NaN en 'Lap' en índice {start_idx}. Saltando segmento.")
            continue # Saltar este segmento si el número de vuelta no es válido
        start_time = df.loc[start_idx, 'Time']; end_time = df.loc[end_idx, 'Time']
        lap_time_secs = np.nan; is_complete = False; lap_type = 'Unknown'
        # Determinar tipo y si es completa
        if i == 0: lap_type = 'Out Lap'
        elif i == len(cut_indices) - 2: lap_type = 'In Lap'
        else: lap_type = 'Timed Lap'; is_complete = True # Asumir completa inicialmente
        # Calcular tiempo
        if i < len(cut_indices) - 1: # Evitar índice fuera de rango
            try: # Añadir try-except por si Time no es numérico
                lap_time_secs = df.loc[cut_indices[i+1], 'Time'] - df.loc[cut_indices[i], 'Time']
            except TypeError:
                print(f"Adv: Error de tipo calculando LapTime para Lap {lap_num}. T1={df.loc[cut_indices[i+1], 'Time']}, T0={df.loc[cut_indices[i], 'Time']}")
                lap_time_secs = np.nan # Marcar como inválido si hay error

        # Validar IsLapValidSource de forma segura
        is_valid_source = False
        if start_idx <= end_idx:
             try: is_valid_source = df.loc[start_idx:end_idx, 'IsLapValid'].all()
             except KeyError: print("Adv: Columna 'IsLapValid' no presente al validar fuente."); is_valid_source = True # Asumir válido si no existe
             except Exception as e_val: print(f"Adv: Error validando fuente Lap {lap_num}: {e_val}"); is_valid_source = False

        # Validar tiempo solo para vueltas cronometradas
        is_time_valid = False
        if lap_type == 'Timed Lap' and pd.notna(lap_time_secs) and lap_time_secs >= min_lap_time_threshold:
            is_time_valid = is_valid_source
        else:
            is_complete = False # Out/In o tiempo inválido no son completas para análisis comparativo

        lap_data.append({'Lap': lap_num, 'LapType': lap_type, 'StartTime': start_time, 'EndTime': end_time,
                         'LapTime': lap_time_secs, 'FormattedTime': format_time(lap_time_secs),
                         'IsLapValidSource': is_valid_source, 'IsTimeValid': is_time_valid, 'IsComplete': is_complete})
    laps_df = pd.DataFrame(lap_data)
    laps_df = laps_df[['Lap', 'LapType', 'StartTime', 'EndTime', 'LapTime', 'FormattedTime', 'IsLapValidSource', 'IsTimeValid', 'IsComplete']]
    # Corrección final IsComplete (quizás no necesaria)
    # if len(laps_df) > 1: ...
    return laps_df


# --- Función Workflow IA (ACTUALIZADA - Versión Final) ---
def run_ai_analysis_workflow():
    """Orquesta: OCR Tiempos -> Input Manual Ref (+Confirmación OCR) -> VLM -> Síntesis."""
    print("\n--- Análisis de Comparación Asistido por IA ---")
    if not AI_ENABLED:
        print("Error: Módulos IA no cargados."); return

    print("\nINFO: En los análisis, tu vuelta (piloto destino) se asume que es la línea AZUL.")
    print("      La otra línea de color corresponde al piloto/vuelta de referencia.")

    # --- PASO 1: Obtener Contexto Inicial ---
    print("\nPASO 1: Contexto Inicial")
    laptime_image_path = input("Introduce la ruta a la imagen de TIEMPOS POR VUELTA (ej. image_fa49c3.png): ").strip()
    if not os.path.exists(laptime_image_path): print(f"Error: Archivo '{laptime_image_path}' no encontrado."); return

    ocr_context = extract_context_from_laptime_image(laptime_image_path)
    if ocr_context is None: print("Error: Falló OCR inicial. No se puede continuar."); return

    # Extraer datos del OCR (pueden ser None)
    track_name_ocr = ocr_context.get('track_name')
    name1_ocr = ocr_context.get('driver_name_1') # Puede ser target o ref
    name2_ocr = ocr_context.get('driver_name_2') # Puede ser target o ref, o None
    target_best_lap_ocr = ocr_context.get('target_best_lap') # Mejor tiempo general encontrado

    print("\nPASO 1b: Introduce/Confirma Datos Esenciales (usando OCR como sugerencia)")

    # --- Nombre Piloto Destino ---
    suggested_target_name = name1_ocr # Asumir el primero encontrado como posible target
    prompt_target_name = "Confirma TU nombre piloto (destino - AZUL)"
    if suggested_target_name: prompt_target_name += f" [Detectado posible: {suggested_target_name}]"
    prompt_target_name += ": "
    target_driver_name = input(prompt_target_name).strip() or suggested_target_name
    if not target_driver_name: print("Error: Nombre piloto destino obligatorio."); return

    # --- Mejor Tiempo Piloto Destino ---
    target_best_lap_str = None
    # Usar el mejor tiempo global detectado por OCR como sugerencia inicial
    current_suggestion = target_best_lap_ocr
    while not target_best_lap_str:
        prompt_target_time = f"Introduce MEJOR vuelta VÁLIDA para {target_driver_name} (MM:SS.ms)"
        if current_suggestion: prompt_target_time += f" [Sugerencia: {current_suggestion}]"
        prompt_target_time += ": "
        time_input = input(prompt_target_time).strip() or current_suggestion
        # Validar formato más flexible (permite espacios, usa punto o coma)
        if time_input and re.match(r"^\d{1,2}\s?:\s?\d{2}\s?[.,]\s?\d{3}$", time_input):
            target_best_lap_str = time_input.replace(',', '.').replace(' ', '') # Limpiar a MM:SS.ms
            break
        else: print("Formato inválido. Usa MM:SS.ms (ej. 01:37.630)"); current_suggestion = None # Limpiar sugerencia si era inválida

    # --- Nombre Piloto Referencia ---
    reference_driver_name = ""; suggested_ref_name = None
    # Sugerir el otro nombre detectado por OCR si existe y es diferente al target
    if name1_ocr and name2_ocr: # Si OCR encontró dos nombres
        suggested_ref_name = name1_ocr if target_driver_name.lower() == name2_ocr.lower() else name2_ocr
    elif name1_ocr and name1_ocr.lower() != target_driver_name.lower(): # Si OCR solo encontró uno y no es el target
         suggested_ref_name = name1_ocr
    # (Si OCR solo encontró uno y ES el target, no podemos sugerir ref)

    while not reference_driver_name:
         ref_name_prompt = "Introduce NOMBRE Piloto Referencia (línea NO azul)"
         if suggested_ref_name: ref_name_prompt += f" [Sugerencia: {suggested_ref_name}]"
         ref_name_prompt += ": "
         reference_driver_name = input(ref_name_prompt).strip() or suggested_ref_name
         if not reference_driver_name: print("Nombre obligatorio.")
         elif reference_driver_name.lower() == target_driver_name.lower(): print("Nombres deben ser diferentes."); reference_driver_name = ""

    # --- Mejor Tiempo Piloto Referencia ---
    reference_best_lap_str = None
    while not reference_best_lap_str:
        time_input = input(f"Introduce MEJOR vuelta VÁLIDA para {reference_driver_name} (MM:SS.ms): ").strip()
        if time_input and re.match(r"^\d{1,2}\s?:\s?\d{2}\s?[.,]\s?\d{3}$", time_input):
            reference_best_lap_str = time_input.replace(',', '.').replace(' ', '')
            break
        else: print("Formato inválido. Usa MM:SS.ms")

    # --- Nombre Pista ---
    prompt_track = "Nombre de la Pista" + (f" [Detectado: {track_name_ocr}]" if track_name_ocr else "") + " (Opcional): "
    track_name = input(prompt_track).strip() or track_name_ocr or "N/A"

    # --- Construir Contexto Completo ---
    session_context = {
        "track_name": track_name, "target_driver": target_driver_name, "target_lap_time": target_best_lap_str,
        "reference_driver": reference_driver_name, "reference_lap_time": reference_best_lap_str,
        "target_color": "Blue", "reference_color": "Other/Non-Blue" }
    # Calcular rápido/lento y delta
    time_target_sec = time_str_to_seconds(target_best_lap_str)
    time_ref_sec = time_str_to_seconds(reference_best_lap_str)
    delta_str = "N/A"; faster="N/A"; slower="N/A"
    if time_target_sec != float('inf') and time_ref_sec != float('inf'):
        delta_sec = time_target_sec - time_ref_sec; delta_str = f"{delta_sec:+.3f}" # Con signo
        if delta_sec <= 0: faster = target_driver_name; slower = reference_driver_name
        else: faster = reference_driver_name; slower = target_driver_name
    else: # Si hubo error convirtiendo tiempos
         print("Advertencia: No se pudo calcular Delta debido a formato de tiempo inválido.")
         # Asignar roles basados en nombres si los tiempos fallan (menos ideal)
         faster = reference_driver_name # Asumir ref es más rápido si no hay tiempos
         slower = target_driver_name

    session_context["faster_driver"] = faster; session_context["slower_driver"] = slower; session_context["delta_time"] = delta_str
    print("\nContexto Final Construido:"); print(json.dumps(session_context, indent=2)); print("-" * 30)

    # --- Verificar Conexiones ---
    print("Verificando conexiones VLM/LLM..."); vlm_ok = "Error" not in test_connection(model_name=DEFAULT_VLM_MODEL); print(f"VLM: {'OK' if vlm_ok else 'ERROR'}")
    text_llm_ok = "Error" not in test_connection(model_name=DEFAULT_TEXT_MODEL); print(f"LLM Texto: {'OK' if text_llm_ok else 'ERROR'}")
    if not vlm_ok: print("ERROR CRÍTICO: VLM no disponible."); return

    # --- PASO 2: Analizar Gráficos Individuales ---
    graph_types_to_analyze = ["Brake", "Throttle", "Gear", "Speed", "TrackMap"]
    analyses = {gt: None for gt in graph_types_to_analyze}
    graph_paths = {}

    for graph_type in graph_types_to_analyze:
        print(f"\nPASO 2: Análisis del Gráfico de {graph_type}")
        # Pedir ruta y validar
        while True:
            graph_image_path = input(f"Introduce la ruta a la imagen del gráfico SEPARADO de {graph_type} (o 'saltar'): ").strip()
            if graph_image_path.lower() == 'saltar':
                print(f"Saltando análisis de {graph_type}.")
                analyses[graph_type] = "[Skipped: User skipped]"
                graph_paths[graph_type] = None
                break # Salir del while de pedir ruta
            elif os.path.exists(graph_image_path):
                graph_paths[graph_type] = graph_image_path
                break # Salir del while de pedir ruta
            else:
                print(f"Error: Archivo '{graph_image_path}' no encontrado. Intenta de nuevo o escribe 'saltar'.")

        if graph_paths[graph_type] is None:
             continue # Ir al siguiente tipo de gráfico si se saltó

        print(f"Enviando gráfico de {graph_type} al VLM ({DEFAULT_VLM_MODEL})...")
        analysis_result = analyze_telemetry_comparison_graph(
            image_path=graph_paths[graph_type], graph_type=graph_type,
            context=session_context, model_name=DEFAULT_VLM_MODEL )
        print(f"\n--- Resultado Análisis VLM para {graph_type} ---"); print(analysis_result if analysis_result else "[N/A o Error]"); print("-" * 30)
        analyses[graph_type] = analysis_result

    # --- PASO 3: Síntesis Final ---
    final_summary = "[Síntesis no realizada]"
    valid_analyses_count = sum(1 for a in analyses.values() if a is not None and not str(a).startswith('['))
    if text_llm_ok and session_context and valid_analyses_count > 0:
        print(f"\nPASO 3: Generando Síntesis Final (basada en {valid_analyses_count} análisis válidos)...")
        final_summary = synthesize_driving_advice(
            initial_context=session_context,
            brake_analysis=analyses.get("Brake"), throttle_analysis=analyses.get("Throttle"), gear_analysis=analyses.get("Gear"),
            speed_analysis=analyses.get("Speed"), trackmap_analysis=analyses.get("TrackMap"),
            model_name=DEFAULT_TEXT_MODEL )
    elif not text_llm_ok: print("\nAdv: Síntesis no posible (LLM Texto no disponible).")
    elif not session_context: print("\nAdv: Síntesis no posible (Contexto no construido).")
    else: print("\nAdv: Síntesis no posible (No hay análisis VLM válidos).")

    # Mostrar resultado final
    print("\n" + "="*40); print("--- RESUMEN FINAL DE CONSEJOS (GENERADO POR IA) ---"); print("="*40)
    print(final_summary); print("="*40)


# --- Función Principal (main - Llama a workflow actualizado) ---
def main():
    print("--- Iniciando RennsportTelemetryTool ---")
    while True: # Bucle principal archivo CSV
        file_path = input("\nIntroduce la ruta al archivo CSV de telemetría (o deja vacío para salir): ").strip()
        if not file_path: print("Saliendo..."); break
        if not os.path.exists(file_path): print(f"Error: '{file_path}' no existe."); continue
        if not file_path.lower().endswith('.csv'): print(f"Error: '{os.path.basename(file_path)}' no parece ser CSV."); continue

        print(f"\nProcesando archivo: {file_path}")
        # --- Carga y Cálculo Vueltas ---
        df_cleaned, metadata = None, {}
        laps_info_df, best_lap_row, slowest_lap_row, available_laps_for_analysis = pd.DataFrame(), None, None, []
        try:
            print(f"Cargando datos..."); df_cleaned, metadata = load_telemetry_csv(file_path)
            if df_cleaned is None or df_cleaned.empty: print("Error carga."); continue
            print(f"Carga OK. {df_cleaned.shape[0]}x{df_cleaned.shape[1]}."); print("Metadatos:", metadata)
            print("\nCalculando Tiempos...");
            # --- Cálculo Umbral Tiempo Mínimo ---
            track_length_m = None
            track_meta_key = 'Track Length M' # Clave exacta en tus metadatos
            if metadata and track_meta_key in metadata:
                 try: track_length_m = float(metadata[track_meta_key])
                 except (ValueError, TypeError): print(f"Advertencia: No se pudo convertir '{metadata[track_meta_key]}' a número para longitud de pista.")
            min_lap_time = 60 # Default
            if track_length_m and track_length_m > 500:
                min_lap_time = max(30, track_length_m / 40.0) # Umbral más agresivo (ej. media 144kmh)
                print(f"Umbral T Válido: > {min_lap_time:.1f} s (Estimado)")
            else: print(f"Umbral T Válido: > {min_lap_time} s (Fijo)")
            # --- Fin Cálculo Umbral ---
            laps_info_df = calculate_laps_improved(df_cleaned, min_lap_time)
            if not laps_info_df.empty:
                print("Tiempos calculados:")
                laps_display_df = laps_info_df[['Lap','LapType','FormattedTime','IsTimeValid']].copy()
                print(laps_display_df.rename(columns={'FormattedTime':'T Fmt','IsTimeValid':'Valida'}).to_string(index=False))
                valid_timed = laps_info_df[laps_info_df['IsTimeValid'] & (laps_info_df['LapType']=='Timed Lap')]
                if not valid_timed.empty:
                    best_lap_row = valid_timed.loc[valid_timed['LapTime'].idxmin()]
                    slowest_lap_row = valid_timed.loc[valid_timed['LapTime'].idxmax()]
                    print(f"Mejor: V{int(best_lap_row['Lap'])} ({best_lap_row['FormattedTime']}) | Peor: V{int(slowest_lap_row['Lap'])} ({slowest_lap_row['FormattedTime']})")
                else: print("No hay vueltas cronometradas válidas.")
                available_laps_for_analysis = sorted(laps_info_df['Lap'].unique().astype(int).tolist())
                print(f"Vueltas detectadas: {available_laps_for_analysis}")
            else: print("No se calculó info detallada de vueltas.")
        except Exception as e: print(f"Error carga/cálculo: {e}"); traceback.print_exc(); continue

        # --- Bucle Opciones Archivo ---
        while True:
            print("\n--- Opciones para Archivo Cargado ---")
            print("1: Generar Gráficos Individuales/Comparativos (Original)")
            print("2: Realizar Análisis Comparativo con IA (Nuevo)")
            print("V: Volver a selección archivo CSV")
            print("Q: Salir del programa")
            main_choice = input("Elige una opción: ").strip().upper()

            if main_choice == '1':
                 # --- Opción 1: Flujo Original de Gráficos ---
                 if not available_laps_for_analysis: print("\nNo hay vueltas disponibles."); continue
                 while True: # Bucle selección vuelta
                     lap_prompt = "\nVuelta para gráficos?"
                     if best_lap_row is not None: lap_prompt += f" (Mejor V{int(best_lap_row['Lap'])})"
                     lap_prompt += f" (Vueltas: {available_laps_for_analysis}. 'V' Volver): "
                     lap_choice = input(lap_prompt).strip().upper()
                     if lap_choice == 'V': break
                     try:
                         selected_lap_num = int(lap_choice)
                         if selected_lap_num not in available_laps_for_analysis: print("Vuelta inválida."); continue
                         lap_info_series = laps_info_df[laps_info_df['Lap'] == selected_lap_num]
                         if lap_info_series.empty: print(f"Info no encontrada V{selected_lap_num}."); continue
                         lap_info = lap_info_series.iloc[0]
                         # Asegurar que df_cleaned y lap_info['StartTime']/['EndTime'] son válidos
                         if df_cleaned is None or pd.isna(lap_info['StartTime']) or pd.isna(lap_info['EndTime']): print("Error: Datos base o tiempos de vuelta inválidos."); continue
                         df_lap = df_cleaned[(df_cleaned['Time'] >= lap_info['StartTime']) & (df_cleaned['Time'] <= lap_info['EndTime'])].copy()
                         if df_lap.empty: print("Sin datos para esta vuelta."); continue
                         # --- Submenú Gráficos ---
                         while True:
                             print(f"\n--- Menú Gráficos V{selected_lap_num} ---")
                             print("1: Velocidad | 2: Entradas | 3: Motor | 4: Dashboard Comp. | 5: TODOS | V: Volver")
                             report_choice = input("Opción: ").strip().upper()
                             if report_choice == 'V': break
                             try:
                                 if report_choice == '1': plot_lap_speed_profile(df_lap, metadata, selected_lap_num); print("OK.")
                                 elif report_choice == '2': plot_lap_inputs(df_lap, metadata, selected_lap_num); print("OK.")
                                 elif report_choice == '3': plot_lap_engine(df_lap, metadata, selected_lap_num); print("OK.")
                                 elif report_choice == '4': # Dashboard Comparativo
                                     valid_ref = laps_info_df[(laps_info_df['IsTimeValid']) & (laps_info_df['LapType']=='Timed Lap') & (laps_info_df['Lap']!=selected_lap_num)]
                                     if valid_ref.empty: print("No refs disponibles."); continue
                                     avail_ref_laps = sorted(valid_ref['Lap'].astype(int).tolist())
                                     ref_prompt = f"Ref para V{selected_lap_num}? (Disp: {avail_ref_laps}): "
                                     ref_choice = input(ref_prompt).strip().upper()
                                     try: ref_lap_num = int(ref_choice)
                                     except ValueError: print("Número inválido"); continue
                                     if ref_lap_num not in avail_ref_laps: print("Ref inválida."); continue
                                     print(f"Generando Dashboard V{selected_lap_num} vs V{ref_lap_num}...")
                                     # Pasar laps_info_df puede ser necesario si la función plotter lo usa
                                     plot_comparison_dashboard(df_cleaned, metadata, selected_lap_num, ref_lap_num, laps_info_df)
                                     print("OK.")
                                 elif report_choice == '5': # Todos
                                     print("Generando TODOS..."); err_p=False
                                     try: plot_lap_speed_profile(df_lap, metadata, selected_lap_num)
                                     except Exception as e1: print(f"Err plot 1: {e1}"); err_p=True
                                     try: plot_lap_inputs(df_lap, metadata, selected_lap_num)
                                     except Exception as e2: print(f"Err plot 2: {e2}"); err_p=True
                                     try: plot_lap_engine(df_lap, metadata, selected_lap_num)
                                     except Exception as e3: print(f"Err plot 3: {e3}"); err_p=True
                                     if not err_p: print("Todos OK.")
                                 else: print("Opción inválida.")
                             except Exception as e_p: print(f"Error gráfico: {e_p}")
                     except ValueError: print("Número inválido.")
                     except Exception as e_l: print(f"Error procesando vuelta: {e_l}")

            elif main_choice == '2':
                 # --- Opción 2: Flujo IA ---
                if AI_ENABLED: run_ai_analysis_workflow()
                else: print("Funcionalidad IA deshabilitada.")
            elif main_choice == 'V': print("Volviendo a selección archivo..."); break
            elif main_choice == 'Q': print("Saliendo..."); sys.exit()
            else: print("Opción no válida.")
        # Fin bucle opciones archivo
    # Fin bucle principal

if __name__ == "__main__":
    # --- Comprobación Conexión Inicial ---
    if AI_ENABLED:
        print("Comprobando conexión inicial con modelos IA (puede tardar)...")
        try:
             vlm_status = test_connection(model_name=DEFAULT_VLM_MODEL); print(f"- VLM ({DEFAULT_VLM_MODEL}): {vlm_status}")
             text_status = test_connection(model_name=DEFAULT_TEXT_MODEL); print(f"- LLM Texto ({DEFAULT_TEXT_MODEL}): {text_status}")
             print("-" * 20)
             if "Error" in vlm_status or "Error" in text_status: print("ADVERTENCIA: Uno o ambos modelos IA no responden.")
        except Exception as e_test: print(f"Error durante test conexión inicial: {e_test}") # Captura errores si test_connection falla
    else: print("Funcionalidad IA deshabilitada.")
    # --- Llamada a main ---
    main()