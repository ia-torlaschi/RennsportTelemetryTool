import data_loader
import plotter
import os
import pandas as pd
import numpy as np

def get_path_from_terminal():
    """Pide al usuario que ingrese la ruta al archivo CSV en la terminal."""
    print("\nPor favor, pega la ruta completa al archivo Telemetry.csv y presiona Enter:")
    while True:
        filepath = input("Ruta al archivo (o deja vacío para salir): ")
        if not filepath: return None
        filepath = filepath.strip('"')
        if os.path.exists(filepath) and filepath.lower().endswith('.csv'):
            print(f"Archivo encontrado: {filepath}"); return filepath
        else: print(f"Error: Ruta '{filepath}' inválida o no es .csv.");

def get_lap_list_from_input(prompt, available_laps):
     """ Pide al usuario una lista de vueltas separadas por coma. """
     while True:
         print(prompt)
         laps_str = input(f"Vueltas disponibles: {available_laps}. Ingresa números separados por coma: ")
         try:
             selected_laps = [int(lap.strip()) for lap in laps_str.split(',')]
             if all(lap in available_laps for lap in selected_laps):
                 if len(selected_laps) >= 2: return selected_laps
                 else: print("Error: Debes seleccionar al menos dos vueltas.")
             else: print("Error: Una o más vueltas no están disponibles.")
         except ValueError: print("Error: Ingresa números separados por coma (ej. 9,10,11).")

# --- Ejecución Principal ---
print("--- Iniciando RennsportTelemetryTool ---")
telemetry_csv_path = get_path_from_terminal()

if telemetry_csv_path:
    df_telemetry, metadata = data_loader.load_telemetry_csv(telemetry_csv_path)

    if df_telemetry is not None:
        print("\n--- Metadatos Extraídos ---")
        if metadata:
            for key, value in metadata.items(): print(f"- {key}: {value}")
        else: print("No se extrajeron metadatos.")

        laps_found_raw = sorted(df_telemetry['Lap'].unique()) if 'Lap' in df_telemetry else []

        lap_times_df = None
        best_lap_info = None
        # --- Cálculo de Tiempos de Vuelta y Mejor Vuelta ---
        if laps_found_raw:
             # ... (Bloque de cálculo de tiempos y mejor vuelta - sin cambios respecto a la versión anterior) ...
            required_cols_for_timing = ['Time', 'Lap', 'IsLapValid']
            if all(col in df_telemetry.columns for col in required_cols_for_timing):
                print("\n--- Calculando Tiempos de Vuelta (considerando validez) ---")
                try:
                    lap_stats = df_telemetry.groupby('Lap').agg(
                        Time_min=('Time', 'min'), Time_max=('Time', 'max'), IsValid=('IsLapValid', 'last')
                    )
                    lap_stats['LapTime'] = lap_stats['Time_max'] - lap_stats['Time_min']
                    lap_times_df = lap_stats[['LapTime', 'IsValid']].reset_index()
                    lap_times_df.rename(columns={'Lap': 'Vuelta', 'LapTime': 'Tiempo (s)', 'IsValid': 'Valida'}, inplace=True)
                    def format_time(seconds):
                        if pd.isna(seconds): return "N/A"
                        try: minutes = int(seconds // 60); secs = int(seconds % 60); millis = int((seconds - int(seconds)) * 1000); return f"{minutes:02d}:{secs:02d}.{millis:03d}"
                        except ValueError: return "Error Formato"
                    lap_times_df['Tiempo Formateado'] = lap_times_df['Tiempo (s)'].apply(format_time)
                    print("Tiempos de vuelta calculados:")
                    for index, row in lap_times_df.iterrows(): print(f"  Vuelta {row['Vuelta']}: {row['Tiempo Formateado']} ({'Válida' if row['Valida']==True else 'Inválida/Inc.'})") # Formato Validez
                    valid_laps = lap_times_df[lap_times_df['Valida'] == True].copy()
                    if not valid_laps.empty:
                        median_valid_time = valid_laps['Tiempo (s)'].median()
                        min_time_threshold = median_valid_time * 0.80
                        print(f"Tiempo mediano válido: {format_time(median_valid_time)}. Umbral vuelta completa: >{format_time(min_time_threshold)}")
                        complete_valid_laps = valid_laps[valid_laps['Tiempo (s)'] > min_time_threshold]
                        if not complete_valid_laps.empty:
                            best_lap_index = complete_valid_laps['Tiempo (s)'].idxmin()
                            best_lap_row = complete_valid_laps.loc[best_lap_index]
                            best_lap_info = {'lap_number': int(best_lap_row['Vuelta']), 'time_seconds': best_lap_row['Tiempo (s)'],'time_formatted': best_lap_row['Tiempo Formateado']}
                            print(f"\nMEJOR VUELTA VÁLIDA encontrada: Vuelta {best_lap_info['lap_number']} ({best_lap_info['time_formatted']})")
                        else: print("\nNo se encontraron vueltas válidas completas."); best_lap_info = None
                    else: print("\nNo se encontraron vueltas marcadas como válidas."); best_lap_info = None
                except Exception as e: print(f"Error calculando tiempos de vuelta: {e}")
            else: print(f"Advertencia: Faltan columnas para calcular tiempos válidos.")
        # --- Fin Cálculo ---

        # --- Sección de Ploteo Principal ---
        if laps_found_raw:
            laps_available_int = [int(lap) for lap in laps_found_raw]

            while True: # Bucle principal para elegir vuelta
                print(f"\nVueltas disponibles: {laps_available_int}")
                best_lap_text = f" (Mejor Válida: V{best_lap_info['lap_number']} - {best_lap_info['time_formatted']})" if best_lap_info else ""
                print(f"\n¿Qué vuelta deseas analizar?{best_lap_text} (Escribe el número o 'Q' para salir)")
                lap_choice_str = input("Elige una vuelta: ")
                if lap_choice_str.upper() == 'Q': break

                try:
                    lap_choice = int(lap_choice_str)
                    if lap_choice not in laps_available_int: print(f"Error: Vuelta {lap_choice} no válida."); continue

                    # Bucle interno para elegir gráfico
                    while True:
                        print(f"\n--- Análisis Vuelta {lap_choice} ---")
                        print("¿Qué gráfico deseas ver?")
                        print("  1: Perfil de Velocidad (vs Dist)")
                        print("  2: Entradas Piloto (vs Dist)")
                        print("  3: Motor/Caja (vs Dist)")
                        print("  4: Mapa del Circuito (Lat/Lon)")
                        print("  5: Gráfico GG (G-Lat vs G-Lon)")
                        print("  --- Comparaciones ---")
                        print("  6: Comparar Vueltas (Velocidad vs Dist)")
                        print("  7: Delta Time vs Mejor Vuelta (vs Dist)")
                        print("  8: DASHBOARD Análisis Delta (Mapa/Delta/Inputs)") # <-- NUEVA OPCIÓN
                        print("  --------------------")
                        print("  9: Elegir otra vuelta")
                        print("  0: Salir del programa")

                        plot_choice_str = input("Elige una opción: ")
                        try: plot_choice = int(plot_choice_str)
                        except ValueError: print("Error: Ingresa un número."); continue

                        # Ejecutar acción
                        if plot_choice == 1: plotter.plot_lap_speed_profile(df_telemetry, metadata, lap_choice)
                        elif plot_choice == 2: plotter.plot_lap_inputs(df_telemetry, metadata, lap_choice)
                        elif plot_choice == 3: plotter.plot_lap_engine(df_telemetry, metadata, lap_choice)
                        elif plot_choice == 4: plotter.plot_track_map(df_telemetry, metadata, lap_choice)
                        elif plot_choice == 5: plotter.plot_gg(df_telemetry, metadata, lap_choice)
                        elif plot_choice == 6:
                             laps_to_compare = get_lap_list_from_input("\nIntroduce vueltas a comparar (ej. 7,8,11)", laps_available_int)
                             if laps_to_compare: plotter.plot_lap_comparison(df_telemetry, metadata, laps_to_compare, channel='Speed')
                        elif plot_choice == 7:
                            if best_lap_info:
                                if lap_choice != best_lap_info['lap_number']: plotter.plot_delta_time(df_telemetry, metadata, lap_choice, best_lap_info['lap_number'])
                                else: print("Ya estás analizando la mejor vuelta.")
                            else: print("No hay mejor vuelta válida de referencia.")
                        elif plot_choice == 8: # <-- NUEVA LÓGICA
                            if best_lap_info:
                                if lap_choice != best_lap_info['lap_number']:
                                    plotter.plot_delta_analysis_dashboard(df_telemetry, metadata, lap_choice, best_lap_info['lap_number'])
                                else:
                                     print(f"Estás analizando la mejor vuelta (V{lap_choice}). No se puede comparar contra sí misma.")
                                     print("Consejo: Elige la opción 8 cuando analices una vuelta *diferente* a la mejor.")
                            else:
                                print("No se ha identificado una mejor vuelta válida para usar como referencia en el dashboard delta.")

                        elif plot_choice == 9: break # Salir del bucle interno
                        elif plot_choice == 0: raise SystemExit # Salir del programa
                        else: print("Opción no válida.")

                except ValueError: print("Error: Ingresa un número de vuelta válido o 'Q'.")
                except SystemExit: break
                except Exception as e: print(f"Ocurrió un error inesperado: {e}"); break
        else: print("\nNo hay vueltas disponibles para analizar.")
        # --- Fin Sección de Ploteo ---
        print("\n--- Fin del procesamiento ---")
    else: print("\nNo se pudieron cargar los datos.")
else: print("\nOperación cancelada / No se proporcionó ruta válida.")

print("\n--- RennsportTelemetryTool finalizado ---")