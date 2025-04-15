# main.py (v11 - Import AI Corregido, sin perder funcionalidad original)
import pandas as pd
import numpy as np
import os
import sys
import traceback

# --- Importar funciones de plotting y carga ---
try:
    from data_loader import load_telemetry_csv
    # Importar funciones individuales Y la nueva función de dashboard
    from plotter import plot_lap_speed_profile, plot_lap_inputs, plot_lap_engine, plot_comparison_dashboard
except ImportError as e:
    print(f"Error: No se pudieron importar módulos o funciones necesarias (data_loader, plotter).")
    print(f"Detalle del error: {e}")
    sys.exit(1)

# --- Importar funciones de IA (CON IMPORT CORREGIDO) ---
# Intenta importar, si falla, la funcionalidad AI se deshabilita
try:
    from llm_integration import (
        extract_context_from_summary_image,
        analyze_telemetry_comparison_graph,
        synthesize_driving_advice,
        test_connection,
        DEFAULT_VLM_MODEL,
        # --- LÍNEA CORREGIDA ---
        DEFAULT_TEXT_MODEL # Importa directamente el nombre correcto definido en llm_integration.py
        # --- FIN CORRECCIÓN ---
    )
    AI_ENABLED = True
    # Mover el print a después de la comprobación inicial para no ser tan verboso al inicio
    # print("Módulos de IA cargados correctamente. Funcionalidad de análisis IA habilitada.")
except ImportError as e:
    # Este bloque ahora SÍ capturará el error si persiste por otra razón
    print("\nADVERTENCIA: No se pudieron importar módulos de IA (llm_integration.py).")
    print("             La funcionalidad de 'Análisis con IA' estará deshabilitada.")
    print(f"             Detalle del error: {e}") # Imprime el error de importación específico
    AI_ENABLED = False
except Exception as e_llm:
     # Captura otros errores durante la importación (como el NameError anterior)
     print(f"\nERROR inesperado al importar llm_integration: {e_llm}")
     AI_ENABLED = False


# --- Funciones Auxiliares (sin cambios) ---
def format_time(seconds):
    """Formatea segundos en MM:SS.ms"""
    if pd.isna(seconds) or not np.isfinite(seconds) or seconds < 0: return "N/A"
    if isinstance(seconds, np.timedelta64): seconds = seconds.total_seconds()
    elif not isinstance(seconds, (int, float, np.number)): return "Invalid Type"
    minutes = int(seconds // 60); secs = int(seconds % 60)
    millis = int(round((seconds - minutes * 60 - secs) * 1000))
    if millis >= 1000: secs += 1; millis -= 1000
    if secs >= 60: minutes +=1; secs -= 60
    return f"{minutes:02d}:{secs:02d}.{millis:03d}"

# --- Lógica de Cálculo de Vueltas (sin cambios) ---
def calculate_laps_improved(df, min_lap_time_threshold=60):
    """Calcula tiempos de vuelta basado en fin vuelta anterior."""
    # ... (código existente para calculate_laps_improved sin modificaciones) ...
    required_cols = ['Time', 'Lap', 'IsLapValid']
    if not all(col in df.columns for col in required_cols): raise ValueError(f"Faltan cols: {[c for c in required_cols if c not in df.columns]}")
    df = df.sort_values('Time').reset_index(drop=True)
    if 'IsLapValid' not in df.columns: print("Adv: 'IsLapValid' no encontrada."); df['IsLapValid'] = True
    elif df['IsLapValid'].dtype != bool:
        try:
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
        lap_num = int(df.loc[start_idx, 'Lap'])
        start_time = df.loc[start_idx, 'Time']; end_time = df.loc[end_idx, 'Time']
        lap_time_secs = df.loc[cut_indices[i+1], 'Time'] - df.loc[cut_indices[i], 'Time'] if i < len(cut_indices)-1 else np.nan
        lap_type = 'Timed Lap'; is_complete = True
        if i == 0: lap_type = 'Out Lap'; is_complete = False; lap_time_secs = end_time - df.loc[0, 'Time']
        if i == len(cut_indices) - 2: lap_type = 'In Lap'; is_complete = False; lap_time_secs = df.loc[len(df)-1, 'Time'] - df.loc[cut_indices[i], 'Time'] # Usar start_time del In Lap
        is_valid_source = df.loc[start_idx:end_idx, 'IsLapValid'].all()
        is_valid_time_threshold = (lap_time_secs >= min_lap_time_threshold) if pd.notna(lap_time_secs) else False
        is_time_valid = False; current_lap_time_calc = np.nan
        if i < len(cut_indices) - 2: current_lap_time_calc = df.loc[cut_indices[i+1], 'Time'] - df.loc[cut_indices[i], 'Time']
        if lap_type == 'Timed Lap':
                is_time_valid = is_valid_source and pd.notna(current_lap_time_calc) and current_lap_time_calc >= min_lap_time_threshold
                lap_time_secs = current_lap_time_calc
        elif lap_type == 'In Lap': is_time_valid = False; lap_time_secs = df.loc[len(df)-1, 'Time'] - df.loc[cut_indices[i], 'Time'] # Usar start_time del In Lap
        elif lap_type == 'Out Lap': is_time_valid = False; lap_time_secs = df.loc[cut_indices[i+1], 'Time'] - df.loc[0, 'Time']
        if not is_complete and lap_type not in ['Out Lap', 'In Lap']: lap_time_secs = np.nan
        lap_data.append({'Lap': lap_num, 'LapType': lap_type, 'StartTime': start_time, 'EndTime': end_time,
                         'LapTime': lap_time_secs, 'FormattedTime': format_time(lap_time_secs),
                         'IsLapValidSource': is_valid_source, 'IsTimeValid': is_time_valid, 'IsComplete': is_complete})
    laps_df = pd.DataFrame(lap_data)
    laps_df = laps_df[['Lap', 'LapType', 'StartTime', 'EndTime', 'LapTime', 'FormattedTime', 'IsLapValidSource', 'IsTimeValid', 'IsComplete']]
    if len(laps_df) > 1:
        last_full_lap_idx = -2 if laps_df.iloc[-1]['LapType'] == 'In Lap' else -1
        # Asegurarse que el índice existe antes de acceder
        if last_full_lap_idx < 0 and (last_full_lap_idx + len(laps_df)) >= 0 and laps_df.iloc[last_full_lap_idx]['LapType'] == 'Timed Lap':
                laps_df.loc[laps_df.index[last_full_lap_idx], 'IsComplete'] = True
    return laps_df


# --- NUEVA FUNCIÓN: Workflow de Análisis con IA (sin cambios respecto a anterior) ---
def run_ai_analysis_workflow():
    """Orquesta el flujo completo de análisis con OCR, VLM y LLM."""
    print("\n--- Análisis de Comparación Asistido por IA ---")
    if not AI_ENABLED:
        print("Error: Módulos de IA no cargados o con error. Funcionalidad no disponible.")
        return

    # --- 1. Extraer Contexto Inicial (OCR) ---
    print("\nPASO 1: Extracción de Contexto Inicial desde Imagen de Resumen")
    summary_image_path = input("Introduce la ruta a la imagen de RESUMEN (la que tiene texto de pilotos/tiempos, ej. image_15f621.png): ")
    if not os.path.exists(summary_image_path):
        print(f"Error: Archivo de resumen '{summary_image_path}' no encontrado.")
        return

    initial_context = extract_context_from_summary_image(summary_image_path)
    if not initial_context:
        print("Error: No se pudo extraer el contexto inicial desde la imagen usando OCR.")
        print("Verifica que Tesseract OCR esté instalado y configurado correctamente (PATH o ruta en el código).")
        print("Revisa también las expresiones regulares dentro de 'extract_context_from_summary_image' para que coincidan con tu formato de imagen.")
        return
    print("Contexto inicial obtenido con éxito.")

    # --- 2. Verificar Conexiones LLM/VLM ---
    print("\nVerificando conexión con modelos en LM Studio...")
    # Usamos los nombres importados (DEFAULT_VLM_MODEL, DEFAULT_TEXT_MODEL)
    vlm_model_name = DEFAULT_VLM_MODEL
    text_llm_model_name = DEFAULT_TEXT_MODEL # Ya importado correctamente

    vlm_conn_result = test_connection(model_name=vlm_model_name)
    vlm_ok = "Error" not in vlm_conn_result
    print(f"VLM ({vlm_model_name}): {vlm_conn_result}")

    text_llm_conn_result = test_connection(model_name=text_llm_model_name)
    text_llm_ok = "Error" not in text_llm_conn_result
    print(f"LLM Texto ({text_llm_model_name}): {text_llm_conn_result}")

    if not vlm_ok:
        print(f"\nERROR CRÍTICO: No se pudo conectar con el modelo VLM ({vlm_model_name}).")
        print("Asegúrate de que el modelo esté cargado en LM Studio y el servidor API esté activo.")
        print("El análisis de gráficos no se puede realizar.")
        return # Abortar si el VLM es esencial

    # --- 3. Analizar Gráficos Individuales con VLM ---
    analyses = {"Brake": None, "Throttle": None, "Gear": None}
    for graph_type in analyses.keys(): # Iterar sobre Brake, Throttle, Gear
        print(f"\nPASO 2: Análisis del Gráfico de {graph_type}")
        # Pedir la imagen específica para este gráfico
        graph_image_path = input(f"Introduce la ruta a la imagen del gráfico SEPARADO de {graph_type}: ")
        if not os.path.exists(graph_image_path):
            print(f"Advertencia: Archivo de gráfico de {graph_type} ('{graph_image_path}') no encontrado. Saltando este análisis.")
            continue # Pasar al siguiente tipo de gráfico

        print(f"Enviando gráfico de {graph_type} al VLM ({vlm_model_name})...")
        analysis_result = analyze_telemetry_comparison_graph(
            image_path=graph_image_path,
            graph_type=graph_type,
            context=initial_context, # Pasa el contexto extraído por OCR
            model_name=vlm_model_name # Asegura usar el modelo VLM
        )
        print(f"\n--- Resultado Análisis VLM para {graph_type} ---")
        print(analysis_result if analysis_result else "[Análisis no disponible o con error]")
        print("-" * 30)
        analyses[graph_type] = analysis_result # Guardar el resultado (o None/mensaje de error)

    # --- 4. Síntesis Final con LLM de Texto ---
    final_summary = "[Síntesis no realizada]"
    # Verificar si el LLM de texto está OK y si tenemos al menos un análisis válido de VLM
    if text_llm_ok and any(a is not None and not a.startswith("[Error") for a in analyses.values()):
        print("\nPASO 3: Generando Síntesis Final de Consejos...")
        final_summary = synthesize_driving_advice(
            initial_context=initial_context,
            brake_analysis=analyses["Brake"],
            throttle_analysis=analyses["Throttle"],
            gear_analysis=analyses["Gear"],
            model_name=text_llm_model_name # Asegura usar el modelo de Texto
        )
    elif not text_llm_ok:
         print(f"\nAdvertencia: No se puede generar la síntesis final porque el modelo de texto configurado ({text_llm_model_name}) no está disponible o no responde.")
    else:
         print("\nAdvertencia: No se puede generar la síntesis final porque no se obtuvieron análisis válidos de los gráficos.")

    # --- 5. Mostrar Resultado Final ---
    print("\n" + "="*40)
    print("--- RESUMEN FINAL DE CONSEJOS (GENERADO POR IA) ---")
    print("="*40)
    print(final_summary)
    print("="*40)


# --- Función Principal (Modificada para añadir opción IA) ---
def main():
    print("--- Iniciando RennsportTelemetryTool ---")
    # Bucle principal para seleccionar archivo CSV
    while True:
        file_path = input("\nIntroduce la ruta al archivo CSV de telemetría (o deja vacío para salir): ").strip()
        if not file_path:
            print("Saliendo...")
            break

        if not os.path.exists(file_path):
            print(f"Error: El archivo '{file_path}' no existe.")
            continue
        if not file_path.lower().endswith('.csv'):
            print(f"Error: El archivo '{os.path.basename(file_path)}' no parece ser un archivo CSV.")
            continue

        print(f"\nProcesando archivo: {file_path}")

        # --- 1. Carga de Datos ---
        df_cleaned = None; metadata = {}
        try:
            print(f"Cargando datos desde '{os.path.basename(file_path)}'...")
            df_cleaned, metadata = load_telemetry_csv(file_path)
            if df_cleaned is None or df_cleaned.empty:
                print("Error: No se pudieron cargar datos o el archivo está vacío.")
                continue
            print(f"Carga completada. DataFrame: {df_cleaned.shape[0]} filas x {df_cleaned.shape[1]} columnas.")
            if metadata:
                print("--- Metadatos Extraídos ---")
                for k, v in metadata.items(): print(f"- {k}: {v}")
                print("---------------------------")
            else:
                print("No se encontraron metadatos en el archivo.")
        except Exception as e:
            print(f"Error crítico durante la carga del archivo: {e}")
            traceback.print_exc()
            continue

        # --- 2. Cálculo de Vueltas ---
        laps_info_df = pd.DataFrame(); best_lap_row = None; slowest_lap_row = None; available_laps_for_analysis = []
        print("\n--- Calculando Tiempos de Vuelta ---")
        try:
            track_length_m = metadata.get('Track Length M', None)
            min_lap_time = 60 # Umbral por defecto
            if track_length_m and isinstance(track_length_m, (int, float)) and track_length_m > 500: # Umbral mínimo razonable para longitud de pista
                estimated_min_time = track_length_m / (27.8 * 1.5) # Estimación simple
                min_lap_time = max(30, estimated_min_time) # Mínimo absoluto de 30s
                print(f"Usando umbral de tiempo de vuelta mínimo estimado: > {min_lap_time:.1f} s (basado en longitud de pista)")
            else:
                print(f"No se pudo estimar umbral por longitud de pista. Usando umbral fijo: > {min_lap_time} s")

            laps_info_df = calculate_laps_improved(df_cleaned, min_lap_time_threshold=min_lap_time)

            if not laps_info_df.empty:
                print("Tiempos de vuelta calculados:")
                laps_display_df = laps_info_df[['Lap','LapType','LapTime','FormattedTime','IsTimeValid']].copy()
                laps_display_df['LapTime'] = laps_display_df['LapTime'].round(3)
                laps_display_df.rename(columns={'LapTime':'T (s)','FormattedTime':'T Fmt','IsTimeValid':'Valida'}, inplace=True)
                print(laps_display_df[laps_display_df['T Fmt'] != "N/A"].to_string(index=False))

                valid_timed = laps_info_df[(laps_info_df['IsTimeValid']) & (laps_info_df['LapType']=='Timed Lap')]
                if not valid_timed.empty:
                    best_lap_row = valid_timed.loc[valid_timed['LapTime'].idxmin()]
                    slowest_lap_row = valid_timed.loc[valid_timed['LapTime'].idxmax()]
                    median_time = valid_timed['LapTime'].median()
                    print(f"\nMejor Vuelta Válida: V{int(best_lap_row['Lap'])} ({best_lap_row['FormattedTime']})")
                    print(f"Peor Vuelta Válida: V{int(slowest_lap_row['Lap'])} ({slowest_lap_row['FormattedTime']})")
                    print(f"Mediana Vueltas Válidas: {format_time(median_time)}")
                else:
                    print("\nNo se encontraron vueltas cronometradas válidas para determinar la mejor/peor.")

                available_laps_for_analysis = sorted(laps_info_df['Lap'].unique().astype(int).tolist())
                print(f"Vueltas detectadas en el archivo: {available_laps_for_analysis}")
            else:
                print("No se pudo calcular información detallada de vueltas.")
        except Exception as e:
            print(f"Error durante el cálculo de vueltas: {e}")
            traceback.print_exc()

        # --- Bucle de Opciones para el archivo cargado ---
        # Este bucle ahora se ejecutará siempre después de cargar un archivo
        while True:
            print("\n--- Opciones para el Archivo Cargado ---")
            print("1: Generar Gráficos Individuales por Vuelta")
            print("2: Realizar Análisis Comparativo con IA (Requiere Imágenes Adicionales)")
            print("V: Volver a selección de archivo CSV")
            print("Q: Salir del programa")

            main_choice = input("Elige una opción: ").strip().upper()

            if main_choice == '1':
                # --- Código Original para Selección de Vuelta y Gráficos ---
                if not available_laps_for_analysis:
                    print("\nNo hay vueltas disponibles para generar gráficos.")
                    continue # Vuelve al menú de opciones para el archivo

                # --- Bucle selección vuelta para gráficos ---
                while True:
                    lap_prompt = "\n¿Vuelta para generar gráficos?"
                    lap_details = []
                    if best_lap_row is not None: lap_details.append(f"Mejor V{int(best_lap_row['Lap'])}")
                    if slowest_lap_row is not None: lap_details.append(f"Peor V{int(slowest_lap_row['Lap'])}")
                    if lap_details: lap_prompt += f" ({'; '.join(lap_details)})"
                    lap_prompt += f"\n(Vueltas: {available_laps_for_analysis}. Introduce número o 'V' para Volver a Opciones Archivo): "

                    lap_choice = input(lap_prompt).strip().upper()
                    if lap_choice == 'V':
                        break # Sale del bucle de selección de vuelta, vuelve al menú de opciones del archivo

                    try:
                        selected_lap_num = int(lap_choice)
                        if selected_lap_num not in available_laps_for_analysis:
                            print("Error: Vuelta no disponible.")
                            continue # Pide de nuevo número de vuelta

                        print(f"\n--- Preparando datos para gráficos de V{selected_lap_num} ---")
                        lap_info_series = laps_info_df[laps_info_df['Lap'] == selected_lap_num]
                        if lap_info_series.empty:
                             print(f"Error interno: No se encontró información para la vuelta {selected_lap_num} seleccionada.")
                             continue
                        lap_info = lap_info_series.iloc[0]
                        df_lap = df_cleaned[(df_cleaned['Time'] >= lap_info['StartTime']) & (df_cleaned['Time'] <= lap_info['EndTime'])].copy()
                        if df_lap.empty:
                            print(f"Error: No se encontraron datos en el DataFrame para el rango de tiempo de la vuelta {selected_lap_num}.")
                            continue

                        # --- Menú Informes Gráficos (Código Original) ---
                        while True: # Bucle Menú Informes
                            print("\n--- Menú Informes (Gráficos para V{selected_lap_num}) ---")
                            print("1: Gráfico de Velocidad")
                            print("2: Gráfico de Entradas Piloto (Acel, Freno, Volante)")
                            print("3: Gráfico de Motor (RPM/Marcha)")
                            print("4: Dashboard Comparativo vs Otra Vuelta")
                            print("5: Generar TODOS los gráficos individuales (1, 2, 3)")
                            print("V: Volver a selección de vuelta")

                            report_choice = input("Opción: ").strip().upper()
                            if report_choice == 'V':
                                break # Sale del menú informes, vuelve a selección de vuelta

                            try:
                                # ... (Manejo de report_choice 1, 2, 3, 4, 5 igual que en tu código original) ...
                                if report_choice == '1':
                                    print(f"Generando Gráfico de Velocidad para V{selected_lap_num}...")
                                    plot_lap_speed_profile(df_lap, metadata, selected_lap_num)
                                    print("Gráfico de Velocidad generado.")
                                elif report_choice == '2':
                                    print(f"Generando Gráfico de Entradas para V{selected_lap_num}...")
                                    plot_lap_inputs(df_lap, metadata, selected_lap_num)
                                    print("Gráfico de Entradas generado.")
                                elif report_choice == '3':
                                     print(f"Generando Gráfico de Motor para V{selected_lap_num}...")
                                     plot_lap_engine(df_lap, metadata, selected_lap_num)
                                     print("Gráfico de Motor generado.")
                                elif report_choice == '4':
                                    print("--- Generar Dashboard Comparativo ---")
                                    valid_ref = laps_info_df[(laps_info_df['IsTimeValid']) & (laps_info_df['LapType']=='Timed Lap') & (laps_info_df['Lap']!=selected_lap_num)]
                                    if valid_ref.empty: print("No hay otras vueltas válidas disponibles para comparar."); continue
                                    avail_ref_laps = sorted(valid_ref['Lap'].astype(int).tolist())
                                    ref_prompt = f"Elige vuelta de referencia para comparar con V{selected_lap_num}: \n(Disponibles: {avail_ref_laps}"
                                    if best_lap_row is not None and best_lap_row['Lap'] != selected_lap_num: ref_prompt += f", Mejor: V{int(best_lap_row['Lap'])}"
                                    ref_prompt += ". 'C' para cancelar): "
                                    ref_choice = input(ref_prompt).strip().upper()
                                    if ref_choice == 'C': continue
                                    try:
                                        ref_lap_num = int(ref_choice)
                                        if ref_lap_num not in avail_ref_laps: print("Error: Vuelta de referencia inválida."); continue
                                        print(f"Generando Dashboard Comparativo (V{selected_lap_num} vs Ref V{ref_lap_num})...")
                                        # Asegúrate que la función plot_comparison_dashboard existe y acepta estos args
                                        plot_comparison_dashboard(df_cleaned, metadata, selected_lap_num, ref_lap_num, laps_info_df)
                                        print("Dashboard Comparativo generado.")
                                    except ValueError: print("Error: Entrada inválida. Introduce un número de vuelta.")
                                    except Exception as e_d: print(f"Error generando el dashboard comparativo: {e_d}"); traceback.print_exc()
                                elif report_choice == '5':
                                    print(f"Generando TODOS los gráficos individuales para V{selected_lap_num}...")
                                    error_plotting = False
                                    try: plot_lap_speed_profile(df_lap, metadata, selected_lap_num)
                                    except Exception as e1: print(f"Error Gráfico Velocidad: {e1}"); error_plotting=True
                                    try: plot_lap_inputs(df_lap, metadata, selected_lap_num)
                                    except Exception as e2: print(f"Error Gráfico Entradas: {e2}"); error_plotting=True
                                    try: plot_lap_engine(df_lap, metadata, selected_lap_num)
                                    except Exception as e3: print(f"Error Gráfico Motor: {e3}"); error_plotting=True
                                    if not error_plotting: print("Todos los gráficos individuales generados.")
                                    else: print("Se generaron gráficos individuales con algunos errores.")
                                else:
                                    print("Opción inválida.")
                            except NameError as ne: print(f"Error: Parece que falta una función en 'plotter.py'. {ne}"); traceback.print_exc()
                            except Exception as e_p: print(f"Error inesperado generando el informe: {e_p}"); traceback.print_exc()
                        # Fin del bucle Menú Informes (Gráficos)
                    except ValueError:
                        print("Error: Entrada inválida. Introduce un número de vuelta.")
                    except Exception as e_lap_sel:
                        print(f"Error procesando la vuelta seleccionada: {e_lap_sel}")
                        traceback.print_exc()
                # Fin del bucle selección vuelta para gráficos

            elif main_choice == '2':
                # --- LLAMADA A LA NUEVA FUNCIONALIDAD DE IA ---
                if AI_ENABLED:
                    run_ai_analysis_workflow()
                else:
                    print("Funcionalidad de Análisis con IA no está disponible (error al importar módulos).")

            elif main_choice == 'V':
                print("Volviendo a selección de archivo CSV...")
                break # Sale del bucle de opciones del archivo, vuelve al bucle principal de selección de archivo

            elif main_choice == 'Q':
                print("Saliendo del programa...")
                sys.exit() # Termina el programa completamente

            else:
                print("Opción no válida.")
        # Fin del bucle de opciones para el archivo cargado

    # Fin del bucle principal (while True para seleccionar archivo CSV)

if __name__ == "__main__":
    # Verificar dependencias de IA al inicio si es posible
    if AI_ENABLED:
         print("Comprobando conexión inicial con modelos IA (puede tardar)...")
         # Usar los nombres de modelo correctos importados
         if "Error" not in test_connection(model_name=DEFAULT_VLM_MODEL): print(f"- VLM ({DEFAULT_VLM_MODEL}) OK")
         else: print(f"- VLM ({DEFAULT_VLM_MODEL}) ERROR")
         if "Error" not in test_connection(model_name=DEFAULT_TEXT_MODEL): print(f"- LLM Texto ({DEFAULT_TEXT_MODEL}) OK")
         else: print(f"- LLM Texto ({DEFAULT_TEXT_MODEL}) ERROR")
         print("-" * 20)
    else:
        print("Funcionalidad IA deshabilitada debido a errores de importación.")

    main()