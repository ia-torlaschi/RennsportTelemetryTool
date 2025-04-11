import data_loader
import os
import pandas as pd

def get_path_from_terminal():
    """Pide al usuario que ingrese la ruta al archivo CSV en la terminal."""
    print("\nPor favor, pega la ruta completa al archivo Telemetry.csv y presiona Enter:")
    filepath = input("Ruta al archivo: ")
    if os.path.exists(filepath) and filepath.lower().endswith('.csv'):
        print(f"Archivo encontrado: {filepath}")
        return filepath
    else:
        print(f"Error: La ruta '{filepath}' no es válida o no es un archivo .csv.")
        return None

# --- Ejecución Principal ---
print("--- Iniciando RennsportTelemetryTool ---")

# 1. Obtener la ruta del archivo desde la terminal
telemetry_csv_path = get_path_from_terminal()

# 2. Proceder solo si se obtuvo una ruta válida
if telemetry_csv_path:
    # ... (el resto del código de main.py permanece igual) ...
     # Cargar los datos y metadatos
    df_telemetry, metadata = data_loader.load_telemetry_csv(telemetry_csv_path)

    # Verificar si la carga fue exitosa
    if df_telemetry is not None:
        print("\n--- Metadatos Extraídos ---")
        # ... (imprimir metadatos) ...
        print("\n--- Verificación de Datos Cargados en main.py ---")
        # ... (imprimir info del dataframe) ...
        print("\n--- Fin del procesamiento básico ---")
    else:
        print("\nNo se pudieron cargar los datos de telemetría del archivo seleccionado.")
else:
    print("\nNo se proporcionó una ruta válida.")


print("\n--- RennsportTelemetryTool finalizado ---")