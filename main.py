# main.py (Corregido con nombres de función reales)
import pandas as pd
import numpy as np
import os
import sys
import traceback # Para imprimir errores detallados

# Importar funciones de los otros módulos del proyecto con los nombres correctos
try:
    # Nombre corregido de la función en data_loader.py
    from data_loader import load_and_process_telemetry_csv
    # Nombre corregido de la función en plotter.py
    from plotter import create_combined_lap_dashboard
except ImportError as e:
    print(f"Error: No se pudieron importar módulos o funciones necesarias.")
    print(f"Asegúrate de que 'data_loader.py' contiene 'load_and_process_telemetry_csv'")
    print(f"y 'plotter.py' contiene 'create_combined_lap_dashboard'.")
    print(f"Detalle del error: {e}")
    sys.exit(1) # Salir si los módulos principales no están

# --- Funciones Auxiliares ---

def format_time(seconds):
    """Formatea segundos en MM:SS.ms"""
    if pd.isna(seconds) or not np.isfinite(seconds) or seconds < 0: # Añadido chequeo isfinite
        return "N/A"
    if isinstance(seconds, np.timedelta64):
         seconds = seconds.total_seconds()
    elif not isinstance(seconds, (int, float, np.number)):
         return "Invalid Type"

    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    millis = int(round((seconds - minutes * 60 - secs) * 1000)) # Cálculo más robusto de ms
    if millis >= 1000:
        secs += 1
        millis -= 1000
        if secs >= 60:
            minutes +=1
            secs -= 60

    return f"{minutes:02d}:{secs:02d}.{millis:03d}"

# --- Lógica Mejorada de Cálculo de Vueltas ---

def calculate_laps_improved(df, min_lap_time_threshold=60):
    """
    Calcula tiempos de vuelta, identifica Out/In laps y valida rigurosamente.
    (Misma función que antes)
    """
    required_cols = ['Time', 'Lap', 'LapDistPct', 'IsLapValid']
    if not all(col in df.columns for col in required_cols):
        missing_cols = [col for col in required_cols if col not in df.columns]
        raise ValueError(f"DataFrame must contain required columns. Missing: {missing_cols}")

    df = df.sort_values('Time').reset_index(drop=True)

    if df['IsLapValid'].dtype != bool:
        try:
            # Mapeo explícito para conversión segura a booleano
            valid_map = {'True': True, 'False': False, '1': True, '0': False, 1: True, 0: False, 1.0: True, 0.0: False, True: True, False: False}
            # Aplicar el mapeo, los valores no encontrados serán NaN -> False
            df['IsLapValid'] = df['IsLapValid'].map(valid_map).fillna(False).astype(bool)
            print("Columna 'IsLapValid' convertida a booleano.")
        except Exception as e:
            print(f"Advertencia: No se pudo convertir 'IsLapValid' a booleano. Tratando valores no True como False. Error: {e}")
            # Intento alternativo más simple si el mapeo falla
            df['IsLapValid'] = df['IsLapValid'].apply(lambda x: str(x).lower() in ['true', '1', '1.0'])


    crossing_indices = df[
        (df['LapDistPct'].shift(1).fillna(0) > 0.9) &
        (df['LapDistPct'] < 0.1) &
        (df['Lap'] != df['Lap'].shift(1))
    ].index

    if len(crossing_indices) == 0:
        print("Advertencia: No se detectaron cruces de línea de meta válidos.")
        return pd.DataFrame(columns=['Lap', 'LapType', 'StartTime', 'EndTime', 'LapTime', 'FormattedTime', 'IsLapValidSource', 'IsTimeValid', 'IsComplete'])

    crossing_times = df.loc[crossing_indices, 'Time'].tolist()
    crossing_laps_finished = df.loc[crossing_indices - 1, 'Lap'].tolist()

    lap_data = []
    processed_laps = set()

    # --- Out Lap ---
    first_crossing_time = crossing_times[0]
    first_crossing_idx = crossing_indices[0]
    outlap_num = int(df.loc[first_crossing_idx - 1, 'Lap'])
    outlap_start_time = df['Time'].iloc[0]
    outlap_end_time = first_crossing_time
    outlap_valid_source = df.loc[0:first_crossing_idx-1, 'IsLapValid'].all()

    lap_data.append({
        'Lap': outlap_num, 'LapType': 'Out Lap', 'StartTime': outlap_start_time,
        'EndTime': outlap_end_time, 'LapTime': outlap_end_time - outlap_start_time,
        'FormattedTime': format_time(outlap_end_time - outlap_start_time),
        'IsLapValidSource': outlap_valid_source, 'IsTimeValid': False, 'IsComplete': False
    })
    processed_laps.add(outlap_num)

    # --- Timed Laps ---
    for i in range(len(crossing_times) - 1):
        start_time = crossing_times[i]
        end_time = crossing_times[i+1]
        lap_num = int(df.loc[crossing_indices[i+1] - 1, 'Lap'])

        if lap_num in processed_laps: continue

        lap_time_secs = end_time - start_time
        start_idx = crossing_indices[i]
        end_idx = crossing_indices[i+1] - 1
        is_valid_source = df.loc[start_idx:end_idx, 'IsLapValid'].all()
        is_valid_time_threshold = lap_time_secs >= min_lap_time_threshold

        lap_data.append({
            'Lap': lap_num, 'LapType': 'Timed Lap', 'StartTime': start_time,
            'EndTime': end_time, 'LapTime': lap_time_secs,
            'FormattedTime': format_time(lap_time_secs),
            'IsLapValidSource': is_valid_source,
            'IsTimeValid': is_valid_source and is_valid_time_threshold,
            'IsComplete': True,
        })
        processed_laps.add(lap_num)

    # --- In Lap ---
    last_crossing_time = crossing_times[-1]
    last_crossing_idx = crossing_indices[-1]
    final_time = df['Time'].iloc[-1]
    inlap_num = int(df.loc[df.index[-1], 'Lap'])

    if final_time > last_crossing_time and inlap_num not in processed_laps:
        inlap_start_time = last_crossing_time
        inlap_end_time = final_time
        inlap_valid_source = df.loc[last_crossing_idx:, 'IsLapValid'].all()

        lap_data.append({
            'Lap': inlap_num, 'LapType': 'In Lap', 'StartTime': inlap_start_time,
            'EndTime': inlap_end_time, 'LapTime': inlap_end_time - inlap_start_time,
            'FormattedTime': format_time(inlap_end_time - inlap_start_time),
            'IsLapValidSource': inlap_valid_source, 'IsTimeValid': False, 'IsComplete': False
        })
        processed_laps.add(inlap_num)

    laps_df = pd.DataFrame(lap_data).sort_values(by='StartTime').reset_index(drop=True)
    laps_df = laps_df[['Lap', 'LapType', 'StartTime', 'EndTime', 'LapTime', 'FormattedTime', 'IsLapValidSource', 'IsTimeValid', 'IsComplete']]
    return laps_df


# --- Función Principal ---
def main():
    """Función principal que orquesta la carga, análisis y visualización."""
    print("--- Iniciando RennsportTelemetryTool ---")

    while True:
        file_path = input("\nPor favor, pega la ruta completa al archivo Telemetry.csv y presiona Enter: \n"
                          "Ruta al archivo (o deja vacío para salir): ").strip()

        if not file_path:
            print("Saliendo...")
            break

        if not os.path.exists(file_path):
            print(f"Error: El archivo '{file_path}' no existe.")
            continue
        if not file_path.lower().endswith('.csv'):
            print(f"Error: El archivo '{os.path.basename(file_path)}' no parece ser un archivo CSV.")
            continue

        print(f"Archivo encontrado: {file_path}")

        # --- Carga de Datos ---
        df_cleaned = None
        metadata = {}
        try:
            print(f"Intentando cargar archivo: {os.path.basename(file_path)}")
            # --- LLAMADA CORREGIDA ---
            df_cleaned, metadata = load_and_process_telemetry_csv(file_path)
            if df_cleaned is None or df_cleaned.empty:
                print("Error: No se pudieron cargar los datos o el archivo está vacío.")
                continue
            print(f"Carga y limpieza completadas. DataFrame con {df_cleaned.shape[0]} filas y {df_cleaned.shape[1]} columnas.")

            if metadata:
                print("\n--- Metadatos Extraídos ---")
                for key, value in metadata.items():
                    print(f"- {key}: {value}")
            else:
                print("\nNo se encontraron metadatos.")

        except Exception as e:
            print(f"\nError crítico durante la carga de datos: {e}")
            traceback.print_exc()
            continue

        # --- Cálculo de Vueltas ---
        laps_info_df = pd.DataFrame()
        best_lap_row = None
        slowest_lap_row = None
        available_laps_for_analysis = []

        print("\n--- Calculando Tiempos de Vuelta (Método Mejorado) ---")
        try:
            track_length_m = metadata.get('Track Length M', None)
            if track_length_m and isinstance(track_length_m, (int, float)) and track_length_m > 0:
                 min_lap_time = (track_length_m / (41.6 * 0.7))
                 min_lap_time = max(30, min_lap_time) # Mínimo 30s
                 print(f"(Usando umbral mínimo de tiempo: > {min_lap_time:.1f}s basado en longitud de pista)")
            else:
                 min_lap_time = 60
                 print(f"(Usando umbral mínimo de tiempo fijo: > {min_lap_time}s)")

            laps_info_df = calculate_laps_improved(df_cleaned, min_lap_time_threshold=min_lap_time)

            if not laps_info_df.empty:
                print("Tiempos de vuelta calculados:")
                laps_display_df = laps_info_df[['Lap', 'LapType', 'LapTime', 'FormattedTime', 'IsTimeValid']].copy()
                laps_display_df['LapTime'] = laps_display_df['LapTime'].round(3)
                laps_display_df.rename(columns={'LapTime': 'Tiempo (s)', 'FormattedTime': 'Tiempo Formateado', 'IsTimeValid': 'Valida'}, inplace=True)
                print(laps_display_df.to_string(index=False))

                valid_timed_laps = laps_info_df[(laps_info_df['IsTimeValid']) & (laps_info_df['LapType'] == 'Timed Lap')]

                if not valid_timed_laps.empty:
                    best_lap_row = valid_timed_laps.loc[valid_timed_laps['LapTime'].idxmin()]
                    slowest_lap_row = valid_timed_laps.loc[valid_timed_laps['LapTime'].idxmax()]
                    median_lap_time = valid_timed_laps['LapTime'].median()
                    print(f"\nMEJOR VUELTA VÁLIDA encontrada: Vuelta {int(best_lap_row['Lap'])} ({best_lap_row['FormattedTime']})")
                    print(f"VUELTA MÁS LENTA VÁLIDA encontrada: Vuelta {int(slowest_lap_row['Lap'])} ({slowest_lap_row['FormattedTime']})")
                    print(f"Tiempo mediano válido: {format_time(median_lap_time)}")
                else:
                    print("\nNo se encontraron vueltas cronometradas válidas.")

                available_laps_for_analysis = sorted(laps_info_df['Lap'].unique().astype(int).tolist())
                print(f"\nVueltas detectadas en el log: {available_laps_for_analysis}")
            else:
                print("No se pudo calcular información de vueltas.")

        except Exception as e:
            print(f"\nError calculando tiempos de vuelta: {e}")
            traceback.print_exc()

        # --- Selección de Vuelta y Visualización ---
        if not available_laps_for_analysis:
             print("\nNo hay vueltas disponibles para analizar.")
             continue

        while True:
            prompt = "\n¿Qué vuelta deseas analizar?"
            # Construcción dinámica del prompt
            details = []
            if best_lap_row is not None: details.append(f"Mejor V: V{int(best_lap_row['Lap'])} - {best_lap_row['FormattedTime']}")
            if slowest_lap_row is not None: details.append(f"Peor V: V{int(slowest_lap_row['Lap'])} - {slowest_lap_row['FormattedTime']}")
            if details: prompt += f" ({'; '.join(details)})"
            prompt += f"\n(Vueltas disponibles: {available_laps_for_analysis}. Escribe el número o 'Q' para salir/nuevo archivo): "

            choice = input(prompt).strip().upper()

            if choice == 'Q': break

            try:
                selected_lap_num = int(choice)
                if selected_lap_num not in available_laps_for_analysis:
                    print(f"Error: El número de vuelta {selected_lap_num} no está entre las disponibles.")
                    continue

                print(f"\n--- Analizando Vuelta {selected_lap_num} ---")

                lap_info_selected_rows = laps_info_df[laps_info_df['Lap'] == selected_lap_num]
                if lap_info_selected_rows.empty:
                    print(f"Error: No se encontró información para la vuelta {selected_lap_num} en el resumen.")
                    continue
                lap_info_selected = lap_info_selected_rows.iloc[0] # Tomar la primera fila si hubiera duplicados

                # Filtrar DataFrame principal usando StartTime y EndTime calculados
                df_lap_filtered = df_cleaned[
                    (df_cleaned['Time'] >= lap_info_selected['StartTime']) &
                    # Incluir el EndTime exacto si es posible, o ir ligeramente más allá para asegurar inclusión
                    (df_cleaned['Time'] <= lap_info_selected['EndTime'])
                ].copy()

                if df_lap_filtered.empty:
                     print(f"Error: No se encontraron datos para la vuelta {selected_lap_num} entre {lap_info_selected['StartTime']} y {lap_info_selected['EndTime']}.")
                     # Podría ser un problema si StartTime == EndTime o muy cercano
                     if lap_info_selected['StartTime'] == lap_info_selected['EndTime']:
                         print("StartTime y EndTime son iguales, no se pueden filtrar datos.")
                     continue


                # --- LLAMADA CORREGIDA A PLOTTING ---
                try:
                    print("Generando gráficos...")
                    # Pasar el DataFrame filtrado, el número de vuelta y el resumen completo de vueltas
                    create_combined_lap_dashboard(df_lap_filtered, selected_lap_num, laps_info_df)
                    print("Gráficos generados/mostrados.")
                # Capturar explícitamente NameError y otros posibles errores
                except NameError:
                     print("Error: La función 'create_combined_lap_dashboard' no está definida o importada correctamente desde plotter.py.")
                     traceback.print_exc()
                except Exception as e:
                    print(f"Error durante la generación de gráficos para la vuelta {selected_lap_num}: {e}")
                    traceback.print_exc()

            except ValueError:
                print("Error: Entrada inválida. Por favor, introduce un número de vuelta o 'Q'.")
            except Exception as e:
                 print(f"Error inesperado durante el análisis de la vuelta: {e}")
                 traceback.print_exc()

        print("\nVolviendo a la selección de archivo...")

if __name__ == "__main__":
    main()