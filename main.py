# Contenido completo para main.py (con cálculo de tiempos de vuelta)
import data_loader # Nuestro módulo
import plotter   # Nuestro módulo de gráficos
import os
# import tkinter as tk # Ya no usamos tkinter por ahora
# from tkinter import filedialog # Ya no usamos tkinter por ahora
import pandas as pd # Importar pandas aquí también para option_context

def get_path_from_terminal():
    """Pide al usuario que ingrese la ruta al archivo CSV en la terminal."""
    print("\nPor favor, pega la ruta completa al archivo Telemetry.csv y presiona Enter:")
    while True: # Repetir hasta obtener una ruta válida o vacía
        filepath = input("Ruta al archivo (o deja vacío para salir): ")
        if not filepath: # Si el usuario presiona Enter sin escribir nada
             return None
        # Quitar comillas si el usuario las pegó (común en Windows)
        filepath = filepath.strip('"')
        if os.path.exists(filepath) and filepath.lower().endswith('.csv'):
            print(f"Archivo encontrado: {filepath}")
            return filepath
        else:
            print(f"Error: La ruta '{filepath}' no es válida o no es un archivo .csv. Inténtalo de nuevo.")
            # No retorna None aquí, permite reintentar


# --- Ejecución Principal ---
print("--- Iniciando RennsportTelemetryTool ---")

# 1. Obtener la ruta del archivo desde la terminal
telemetry_csv_path = get_path_from_terminal()

# 2. Proceder solo si se obtuvo una ruta válida
if telemetry_csv_path:
    # Cargar los datos y metadatos
    df_telemetry, metadata = data_loader.load_telemetry_csv(telemetry_csv_path)

    # Verificar si la carga fue exitosa
    if df_telemetry is not None:
        print("\n--- Metadatos Extraídos ---")
        if metadata:
            for key, value in metadata.items():
                print(f"- {key}: {value}")
        else:
            print("No se extrajeron metadatos.")

        # --- Verificación de Datos (Opcional mostrar todo) ---
        # (Sección comentada para brevedad)

        laps_found = []
        if 'Lap' in df_telemetry.columns:
            laps_found = sorted(df_telemetry['Lap'].unique())
            print(f"\nVueltas encontradas en el archivo: {laps_found}")
        else:
            print("\nAdvertencia: No se encontró la columna 'Lap'.")

 # --- ¡NUEVO! Cálculo de Tiempos de Vuelta y Mejor Vuelta (MEJORADO) ---
        lap_times_df = None
        best_lap_info = None
        if laps_found:
            # Verificar que tenemos las columnas necesarias
            required_cols_for_timing = ['Time', 'Lap', 'IsLapValid']
            if all(col in df_telemetry.columns for col in required_cols_for_timing):
                print("\n--- Calculando Tiempos de Vuelta (considerando validez) ---")
                try:
                    # Agrupar por vuelta, obtener min/max tiempo y el último estado de validez
                    lap_stats = df_telemetry.groupby('Lap').agg(
                        Time_min=('Time', 'min'),
                        Time_max=('Time', 'max'),
                        IsValid=('IsLapValid', 'last') # Obtener el último estado de validez registrado para la vuelta
                    )
                    # Calcular la duración registrada para cada vuelta
                    lap_stats['LapTime'] = lap_stats['Time_max'] - lap_stats['Time_min']

                    # Crear DataFrame de resultados limpio
                    lap_times_df = lap_stats[['LapTime', 'IsValid']].reset_index()
                    lap_times_df.rename(columns={'Lap': 'Vuelta', 'LapTime': 'Tiempo (s)', 'IsValid': 'Valida'}, inplace=True)

                    # Formatear tiempo a MM:SS.ms
                    def format_time(seconds):
                         if pd.isna(seconds): return "N/A"
                         try:
                             minutes = int(seconds // 60)
                             secs = int(seconds % 60)
                             millis = int((seconds - int(seconds)) * 1000)
                             return f"{minutes:02d}:{secs:02d}.{millis:03d}"
                         except ValueError: return "Error Formato"

                    lap_times_df['Tiempo Formateado'] = lap_times_df['Tiempo (s)'].apply(format_time)

                    print("Tiempos de vuelta calculados:")
                    for index, row in lap_times_df.iterrows():
                         validity_str = "(Válida)" if row['Valida'] == True else "(Inválida/Incompleta?)" # Añadir estado
                         print(f"  Vuelta {row['Vuelta']}: {row['Tiempo Formateado']} {validity_str}")

                    # --- Encontrar la MEJOR VUELTA VÁLIDA y COMPLETA ---
                    # 1. Filtrar solo vueltas marcadas como válidas
                    valid_laps = lap_times_df[lap_times_df['Valida'] == True].copy()

                    if not valid_laps.empty:
                        # 2. Heurística: Filtrar vueltas demasiado cortas (posibles out/in laps)
                        # Calcular tiempo mediano de las vueltas válidas
                        median_valid_time = valid_laps['Tiempo (s)'].median()
                        # Definir umbral (ej. 80% del mediano) - ¡AJUSTABLE!
                        min_time_threshold = median_valid_time * 0.80
                        print(f"Tiempo mediano válido: {format_time(median_valid_time)}. Umbral para vuelta completa: >{format_time(min_time_threshold)}")

                        # Filtrar por umbral de tiempo
                        complete_valid_laps = valid_laps[valid_laps['Tiempo (s)'] > min_time_threshold]

                        if not complete_valid_laps.empty:
                            # 3. Encontrar la mejor vuelta entre las válidas y completas
                            best_lap_index = complete_valid_laps['Tiempo (s)'].idxmin()
                            best_lap_row = complete_valid_laps.loc[best_lap_index]
                            best_lap_info = {
                                'lap_number': int(best_lap_row['Vuelta']),
                                'time_seconds': best_lap_row['Tiempo (s)'],
                                'time_formatted': best_lap_row['Tiempo Formateado']
                            }
                            print(f"\nMEJOR VUELTA VÁLIDA encontrada: Vuelta {best_lap_info['lap_number']} con un tiempo de {best_lap_info['time_formatted']}")
                        else:
                            print("\nNo se encontraron vueltas válidas que superen el umbral de tiempo mínimo (posiblemente solo vueltas cortas/inválidas).")
                            best_lap_info = None # Asegurarse de que es None
                    else:
                        print("\nNo se encontraron vueltas marcadas como válidas en los datos.")
                        best_lap_info = None # Asegurarse de que es None


                except Exception as e:
                    print(f"Error calculando tiempos de vuelta: {e}")
            else:
                missing_required = [col for col in required_cols_for_timing if col not in df_telemetry.columns]
                print(f"Advertencia: Faltan columnas necesarias para calcular tiempos de vuelta válidos: {missing_required}")

        # --- Fin Cálculo de Tiempos de Vuelta (MEJORADO) ---


        # --- Sección de Ploteo Mejorada ---
        if laps_found:
            # Convertir vueltas a int para mostrar limpiamente
            laps_formatted = [int(lap) for lap in laps_found]

            while True: # Bucle principal para elegir vuelta
                # --- MODIFICAR ESTA LÍNEA ---
                print(f"\nVueltas disponibles: {laps_formatted}") # Usar la lista formateada

                # Añadir info de mejor vuelta al prompt si existe
                best_lap_text = f" (Mejor Válida: Vuelta {best_lap_info['lap_number']} - {best_lap_info['time_formatted']})" if best_lap_info else ""
                print(f"\n¿Qué vuelta deseas analizar?{best_lap_text} (Escribe el número o 'Q' para salir)")

                lap_choice_str = input("Elige una vuelta: ")
                # ... (resto del código del bucle sin cambios) ...

                if lap_choice_str.upper() == 'Q':
                    print("Saliendo del menú de análisis.")
                    break # Salir del bucle principal

                try:
                    lap_choice = int(lap_choice_str) # Intentar convertir la elección de vuelta a número

                    if lap_choice not in laps_found:
                        print(f"Error: La vuelta {lap_choice} no está en la lista.")
                        continue # Volver a pedir la vuelta

                    # Si la vuelta es válida, entrar al bucle para elegir gráfico
                    while True: # Bucle interno para elegir gráfico
                        print(f"\n--- Análisis Vuelta {lap_choice} ---")
                        print("¿Qué gráfico deseas ver?")
                        print("  1: Perfil de Velocidad")
                        print("  2: Entradas del Piloto (Acel/Freno/Volante)")
                        print("  3: Motor/Caja (RPM/Marcha)")
                        print("  4: Mapa del Circuito (Lat/Lon)")
                        # (Aquí añadiremos más opciones después)
                        print("  --------------------")
                        print("  9: Elegir otra vuelta")
                        print("  0: Salir del programa")

                        plot_choice_str = input("Elige una opción: ")
                        try:
                            plot_choice = int(plot_choice_str) # Intentar convertir elección de gráfico
                        except ValueError:
                            print("Error: Ingresa un número válido para la opción de gráfico.")
                            continue # Volver a pedir opción de gráfico

                        # Ejecutar acción según la elección del gráfico
                        if plot_choice == 1:
                            plotter.plot_lap_speed_profile(df_telemetry, metadata, lap_choice)
                        elif plot_choice == 2:
                            plotter.plot_lap_inputs(df_telemetry, metadata, lap_choice)
                        elif plot_choice == 3:
                            plotter.plot_lap_engine(df_telemetry, metadata, lap_choice)
                        elif plot_choice == 4:
                            plotter.plot_track_map(df_telemetry, metadata, lap_choice)
                        elif plot_choice == 9:
                            print("Volviendo a selección de vuelta...")
                            break # Salir del bucle interno para elegir otra vuelta
                        elif plot_choice == 0:
                            print("Saliendo del programa.")
                            raise SystemExit # Usar SystemExit para salir de todo
                        else:
                            print("Opción de gráfico no válida.")

                except ValueError: # Captura error si int(lap_choice_str) falla
                    print("Error: Por favor, ingresa un número de vuelta válido o 'Q'.")
                    # El bucle principal while continuará y volverá a pedir la vuelta
                except SystemExit: # Si se eligió salir desde el menú interno
                    break # Salir del bucle principal
                except Exception as e: # Capturar cualquier otro error inesperado
                    print(f"Ocurrió un error inesperado: {e}")
                    break # Salir del bucle principal por seguridad

        else:
             print("\nNo hay vueltas disponibles para analizar.")
        # --- Fin Sección de Ploteo Mejorada ---


        print("\n--- Fin del procesamiento ---")

    else:
        print("\nNo se pudieron cargar los datos de telemetría del archivo seleccionado.")

else:
    print("\nOperación cancelada / No se proporcionó ruta válida.")


print("\n--- RennsportTelemetryTool finalizado ---")