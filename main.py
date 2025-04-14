# main.py (v7 - Corregido ValueError en prompt de Análisis Delta)
import pandas as pd
import numpy as np
import os
import sys
import traceback

# Importar funciones (sin cambios)
try:
    from data_loader import load_telemetry_csv
    from plotter import plot_lap_speed_profile, plot_lap_inputs, plot_lap_engine, plot_delta_analysis_dashboard
except ImportError as e:
    print(f"Error: No se pudieron importar módulos o funciones necesarias.")
    print(f"Detalle del error: {e}")
    sys.exit(1)

# --- Funciones Auxiliares ---
# (format_time sin cambios)
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

# --- Lógica de Cálculo de Vueltas ---
# (calculate_laps_improved v4 sin cambios)
def calculate_laps_improved(df, min_lap_time_threshold=60):
    """Calcula tiempos de vuelta basado en fin vuelta anterior."""
    required_cols = ['Time', 'Lap', 'IsLapValid']
    if not all(col in df.columns for col in required_cols):
        missing_cols = [col for col in required_cols if col not in df.columns]
        raise ValueError(f"DataFrame must contain required columns. Missing: {missing_cols}")
    df = df.sort_values('Time').reset_index(drop=True)
    if 'IsLapValid' not in df.columns:
         print("Advertencia: Columna 'IsLapValid' no encontrada.")
         df['IsLapValid'] = True
    elif df['IsLapValid'].dtype != bool:
         try:
            valid_map = {'True': True, 'False': False, '1': True, '0': False, 1: True, 0: False, 1.0: True, 0.0: False, True: True, False: False}
            original_type = df['IsLapValid'].dtype
            df['IsLapValid'] = df['IsLapValid'].map(valid_map).fillna(False).astype(bool)
            if not pd.api.types.is_bool_dtype(original_type): print("Columna 'IsLapValid' convertida a booleano.")
         except Exception as e:
            print(f"Advertencia: No se pudo convertir 'IsLapValid'. Error: {e}")
            df['IsLapValid'] = df['IsLapValid'].apply(lambda x: str(x).lower() in ['true', '1', '1.0'])
    lap_change_indices = df[df['Lap'] != df['Lap'].shift(1)].index
    cut_indices = pd.Index([0]).union(lap_change_indices - 1).union(pd.Index([len(df) - 1]))
    cut_indices = cut_indices.unique().sort_values()
    cut_indices = cut_indices[cut_indices >= 0]
    if len(cut_indices) < 3:
        print("Advertencia: No se detectaron suficientes cambios de vuelta.")
        return pd.DataFrame()
    lap_data = []
    for i in range(len(cut_indices) - 1):
        start_idx = cut_indices[i] + 1 if i > 0 else 0; end_idx = cut_indices[i+1]
        if start_idx >= len(df) or end_idx < start_idx: continue
        lap_num = int(df.loc[start_idx, 'Lap'])
        start_time = df.loc[start_idx, 'Time']; end_time = df.loc[end_idx, 'Time']
        lap_time_secs = df.loc[cut_indices[i+1], 'Time'] - df.loc[cut_indices[i], 'Time'] if i < len(cut_indices)-1 else np.nan
        lap_type = 'Timed Lap'; is_complete = True
        if i == 0: lap_type = 'Out Lap'; is_complete = False; lap_time_secs = end_time - df.loc[0, 'Time']
        if i == len(cut_indices) - 2: lap_type = 'In Lap'; is_complete = False; lap_time_secs = df.loc[len(df)-1, 'Time'] - start_time
        is_valid_source = df.loc[start_idx:end_idx, 'IsLapValid'].all()
        is_valid_time_threshold = (lap_time_secs >= min_lap_time_threshold) if pd.notna(lap_time_secs) else False
        is_time_valid = False
        # Reajuste lógico para identificar correctamente Timed vs In Lap al final
        if is_complete: # Solo puede ser Timed si es completa teóricamente
             if lap_type == 'Timed Lap': # Si aún no se marcó como In/Out
                 is_time_valid = is_valid_source and is_valid_time_threshold
        # Si es el penúltimo segmento (última vuelta completa potencial)
        if i == len(cut_indices) - 3:
             # Calcular tiempo de esta vuelta completa potencial
             full_lap_time = df.loc[cut_indices[i+1], 'Time'] - df.loc[cut_indices[i], 'Time']
             if is_valid_source and full_lap_time >= min_lap_time_threshold:
                 lap_type = 'Timed Lap' # Confirmar como Timed Lap válida
                 is_complete = True
                 is_time_valid = True
                 lap_time_secs = full_lap_time # Usar el tiempo calculado entre cortes
             else: # Si no es válida o es muy corta, sigue siendo Timed pero no válida
                 lap_type = 'Timed Lap'
                 is_complete = True
                 is_time_valid = False
                 lap_time_secs = full_lap_time
        elif i == len(cut_indices) - 2: # El último segmento siempre es In Lap
             lap_type = 'In Lap'
             is_complete = False
             is_time_valid = False
             lap_time_secs = df.loc[len(df)-1, 'Time'] - start_time

        if not is_complete and lap_type not in ['Out Lap', 'In Lap']: lap_time_secs = np.nan
        lap_data.append({'Lap': lap_num, 'LapType': lap_type, 'StartTime': start_time, 'EndTime': end_time,
                         'LapTime': lap_time_secs, 'FormattedTime': format_time(lap_time_secs),
                         'IsLapValidSource': is_valid_source, 'IsTimeValid': is_time_valid, 'IsComplete': is_complete})
    laps_df = pd.DataFrame(lap_data)
    laps_df = laps_df[['Lap', 'LapType', 'StartTime', 'EndTime', 'LapTime', 'FormattedTime', 'IsLapValidSource', 'IsTimeValid', 'IsComplete']]
    return laps_df


# --- Función Principal ---
def main():
    """Función principal que orquesta la carga, análisis y visualización."""
    print("--- Iniciando RennsportTelemetryTool ---")

    while True: # Bucle principal por archivo
        file_path = input("\nPor favor, pega la ruta completa al archivo Telemetry.csv y presiona Enter: \n"
                          "Ruta al archivo (o deja vacío para salir): ").strip()
        if not file_path: print("Saliendo..."); break
        if not os.path.exists(file_path): print(f"Error: Archivo '{file_path}' no existe."); continue
        if not file_path.lower().endswith('.csv'): print(f"Error: '{os.path.basename(file_path)}' no es CSV."); continue

        print(f"Archivo encontrado: {file_path}")

        # Carga de Datos
        df_cleaned = None; metadata = {}
        try:
            print(f"Intentando cargar archivo: {os.path.basename(file_path)}")
            df_cleaned, metadata = load_telemetry_csv(file_path)
            if df_cleaned is None or df_cleaned.empty: print("Error: No se cargaron datos."); continue
            print(f"Carga y limpieza completadas. DF con {df_cleaned.shape[0]} filas y {df_cleaned.shape[1]} columnas.")
            if metadata: print("\n--- Metadatos Extraídos ---"); [print(f"- {k}: {v}") for k, v in metadata.items()]
            else: print("\nNo se encontraron metadatos.")
        except Exception as e: print(f"\nError crítico carga: {e}"); traceback.print_exc(); continue

        # Cálculo de Vueltas
        laps_info_df = pd.DataFrame(); best_lap_row = None; slowest_lap_row = None; available_laps_for_analysis = []
        print("\n--- Calculando Tiempos de Vuelta (v4 - Basado en fin vuelta anterior) ---")
        try:
            track_length_m = metadata.get('Track Length M', None)
            if track_length_m and isinstance(track_length_m, (int, float)) and track_length_m > 0:
                 min_lap_time = max(30, (track_length_m / (41.6 * 0.7))); print(f"(Usando umbral mínimo: > {min_lap_time:.1f}s)")
            else: min_lap_time = 60; print(f"(Usando umbral mínimo fijo: > {min_lap_time}s)")
            laps_info_df = calculate_laps_improved(df_cleaned, min_lap_time_threshold=min_lap_time) # Llama a v4
            if not laps_info_df.empty:
                print("Tiempos de vuelta calculados:")
                laps_display_df = laps_info_df[['Lap', 'LapType', 'LapTime', 'FormattedTime', 'IsTimeValid']].copy()
                laps_display_df['LapTime'] = laps_display_df['LapTime'].round(3)
                laps_display_df.rename(columns={'LapTime': 'Tiempo (s)', 'FormattedTime': 'Tiempo Formateado', 'IsTimeValid': 'Valida'}, inplace=True)
                print(laps_display_df[laps_display_df['Tiempo Formateado'] != "N/A"].to_string(index=False)) # Corrección v5 aplicada
                valid_timed_laps = laps_info_df[(laps_info_df['IsTimeValid']) & (laps_info_df['LapType'] == 'Timed Lap')]
                if not valid_timed_laps.empty:
                    best_lap_row = valid_timed_laps.loc[valid_timed_laps['LapTime'].idxmin()]
                    slowest_lap_row = valid_timed_laps.loc[valid_timed_laps['LapTime'].idxmax()]
                    median_lap_time = valid_timed_laps['LapTime'].median()
                    print(f"\nMEJOR VÁLIDA: Vuelta {int(best_lap_row['Lap'])} ({best_lap_row['FormattedTime']})")
                    print(f"PEOR VÁLIDA: Vuelta {int(slowest_lap_row['Lap'])} ({slowest_lap_row['FormattedTime']})")
                    print(f"Mediana válida: {format_time(median_lap_time)}")
                else: print("\nNo se encontraron vueltas cronometradas válidas.")
                available_laps_for_analysis = sorted(laps_info_df['Lap'].unique().astype(int).tolist())
                print(f"\nVueltas detectadas: {available_laps_for_analysis}")
            else: print("No se pudo calcular info de vueltas.")
        except Exception as e: print(f"\nError calculando tiempos: {e}"); traceback.print_exc()

        # --- Bucle de Selección de Vuelta y Análisis ---
        if not available_laps_for_analysis: print("\nNo hay vueltas disponibles para analizar."); continue

        while True: # Bucle selección de vuelta
            lap_prompt = "\n¿Vuelta a analizar?"
            lap_details = []
            # Usar best_lap_row de forma segura aquí también
            if best_lap_row is not None: lap_details.append(f"Mejor V{int(best_lap_row['Lap'])}: {best_lap_row['FormattedTime']}")
            if slowest_lap_row is not None: lap_details.append(f"Peor V{int(slowest_lap_row['Lap'])}: {slowest_lap_row['FormattedTime']}")
            if lap_details: lap_prompt += f" ({'; '.join(lap_details)})"
            lap_prompt += f"\n(Vueltas: {available_laps_for_analysis}. Num o 'Q' para nuevo archivo): "
            lap_choice = input(lap_prompt).strip().upper()

            if lap_choice == 'Q': break

            try:
                selected_lap_num = int(lap_choice)
                if selected_lap_num not in available_laps_for_analysis: print(f"Error: Vuelta {selected_lap_num} no disponible."); continue

                print(f"\n--- Analizando Vuelta {selected_lap_num} ---")
                lap_info_selected_rows = laps_info_df[laps_info_df['Lap'] == selected_lap_num]
                if lap_info_selected_rows.empty: print(f"Error: No info para vuelta {selected_lap_num}."); continue
                lap_info_selected = lap_info_selected_rows.iloc[0]
                df_lap_filtered = df_cleaned[(df_cleaned['Time'] >= lap_info_selected['StartTime']) & (df_cleaned['Time'] <= lap_info_selected['EndTime'])].copy()
                if df_lap_filtered.empty: print(f"Error: No data para V{selected_lap_num} ({lap_info_selected['StartTime']:.3f}-{lap_info_selected['EndTime']:.3f})."); continue

                # --- Menú de Selección de Informes ---
                while True: # Bucle selección de informe
                    print("\n--- Menú de Informes ---")
                    print("1: Perfil de Velocidad vs Distancia")
                    print("2: Entradas del Piloto (Acel/Freno/Volante) vs Distancia")
                    print("3: Motor (RPM/Marcha) vs Distancia")
                    print("4: Análisis Delta vs Vuelta de Referencia")
                    print("5: TODOS los informes individuales (1, 2, 3)")
                    print("Q: Volver a selección de vuelta")
                    report_choice = input("Elige una opción: ").strip().upper()

                    if report_choice == 'Q': break # Salir menú informes

                    try:
                        if report_choice == '1':
                            print("\nGenerando: Perfil de Velocidad..."); plot_lap_speed_profile(df_lap_filtered, metadata, selected_lap_num); print("Informe generado.")
                        elif report_choice == '2':
                            print("\nGenerando: Entradas del Piloto..."); plot_lap_inputs(df_lap_filtered, metadata, selected_lap_num); print("Informe generado.")
                        elif report_choice == '3':
                            print("\nGenerando: Motor..."); plot_lap_engine(df_lap_filtered, metadata, selected_lap_num); print("Informe generado.")
                        elif report_choice == '4':
                            print("\n--- Análisis Delta ---")
                            valid_timed_laps_for_delta = laps_info_df[(laps_info_df['IsTimeValid']) & (laps_info_df['LapType'] == 'Timed Lap') & (laps_info_df['Lap'] != selected_lap_num)]
                            if valid_timed_laps_for_delta.empty:
                                print("No hay otras vueltas válidas para usar como referencia."); continue

                            available_ref_laps = sorted(valid_timed_laps_for_delta['Lap'].astype(int).tolist())
                            # --- CORRECCIÓN AQUÍ: Comprobar si best_lap_row NO es None ---
                            ref_lap_prompt = f"Elige la vuelta de REFERENCIA para comparar con V{selected_lap_num}\n(Disponibles: {available_ref_laps}, Mejor Válida: V{int(best_lap_row['Lap']) if best_lap_row is not None else 'N/A'}. 'C' para cancelar): "
                            ref_choice = input(ref_lap_prompt).strip().upper()

                            if ref_choice == 'C': continue

                            try:
                                selected_ref_lap_num = int(ref_choice)
                                if selected_ref_lap_num not in available_ref_laps:
                                    print(f"Error: Vuelta ref {selected_ref_lap_num} no válida."); continue

                                print(f"\nGenerando: Análisis Delta (V{selected_lap_num} vs Ref V{selected_ref_lap_num})...")
                                # Pasar df completo, la función filtra internamente
                                plot_delta_analysis_dashboard(df_cleaned, metadata, selected_lap_num, selected_ref_lap_num)
                                print("Informe generado.")

                            except ValueError: print("Error: Entrada inválida para vuelta ref.")
                            except Exception as e_delta: print(f"Error delta: {e_delta}"); traceback.print_exc()

                        elif report_choice == '5':
                            print("\nGenerando TODOS los informes individuales...")
                            try: plot_lap_speed_profile(df_lap_filtered, metadata, selected_lap_num)
                            except Exception as e1: print(f"Error plot 1: {e1}")
                            try: plot_lap_inputs(df_lap_filtered, metadata, selected_lap_num)
                            except Exception as e2: print(f"Error plot 2: {e2}")
                            try: plot_lap_engine(df_lap_filtered, metadata, selected_lap_num)
                            except Exception as e3: print(f"Error plot 3: {e3}")
                            print("Informes individuales generados.")
                        else: print("Error: Opción inválida.")
                    except NameError as ne: print(f"Error: Falta función en plotter.py? {ne}"); traceback.print_exc()
                    except Exception as e_plot: print(f"Error generando informe: {e_plot}"); traceback.print_exc()
                # Fin bucle while selección informe

            except ValueError: print("Error: Entrada inválida para número vuelta.")
            except Exception as e: print(f"Error inesperado análisis vuelta: {e}"); traceback.print_exc()
        # Fin bucle while selección vuelta
        print("\nVolviendo a selección de archivo...")
if __name__ == "__main__":
    main()