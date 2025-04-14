import pandas as pd
import os
import io
import re # Importar regular expressions para limpieza más avanzada

def load_telemetry_csv(filepath):
    """
    Carga un archivo CSV de telemetría de Rennsport en un DataFrame de pandas
    y extrae los metadatos del encabezado. Limpia y renombra columnas comunes.

    Args:
        filepath (str): Ruta completa al archivo Telemetry.csv.

    Returns:
        tuple: (pandas.DataFrame or None, dict or None)
               El DataFrame cargado y limpiado, y un diccionario con los metadatos.
               Retorna (None, None) si ocurre un error.
    """
    print(f"Intentando cargar archivo: {filepath}")
    metadata = {}
    header_row_index = -1
    delimiter = None

    if not os.path.exists(filepath):
        print(f"Error: El archivo no existe en la ruta: {filepath}")
        return None, None

    try:
        # Leer primeras líneas para metadatos y encabezado
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            potential_header_lines = [f.readline() for _ in range(20)]

        print("--- Analizando encabezado del CSV ---")
        # (Lógica de detección de metadatos y encabezado - sin cambios)
        for i, line in enumerate(potential_header_lines):
            line = line.strip()
            if not line: continue
            if delimiter is None:
                if ';' in line and line.count(';') > 1: delimiter = ';'
                elif ',' in line and line.count(',') > 1: delimiter = ','
            current_delimiter = delimiter if delimiter else ';'
            if ':' in line and current_delimiter in line:
                 parts = line.split(current_delimiter, 1)
                 key = parts[0].replace(':', '').strip()
                 value = parts[1].strip() if len(parts) > 1 else ''
                 if key and value: metadata[key] = value
            # Usamos nombres clave del encabezado para identificarlo
            if 'Time (s)' in line and 'Lap Number' in line and 'Speed (m/s)' in line and current_delimiter in line:
                header_row_index = i
                if delimiter: print(f"Detectado delimitador: '{delimiter}'")
                else: delimiter = ';'; print("Advertencia: Delimitador no detectado, usando ';'")
                print(f"Detectada fila de encabezado de datos en línea: {header_row_index + 1}")
                break

        if header_row_index == -1:
            print("Error: No se pudo encontrar la fila del encabezado de datos.")
            return None, None

        # Cargar datos con pandas
        print(f"\n--- Cargando datos tabulares con pandas (skiprows={header_row_index}) ---")
        df = pd.read_csv(filepath,
                         delimiter=delimiter,
                         skiprows=header_row_index,
                         low_memory=False)
        print(f"Archivo CSV '{os.path.basename(filepath)}' leído, procesando...")

        # --- Limpieza y Preparación ---
        df.columns = df.columns.str.strip() # Limpiar espacios

        # --- MAPA DE RENOMBRADO EXTENDIDO ---
        # Añade/modifica según sea necesario basado en tus columnas exactas
        rename_map = {
            # Core / Timing
            'Time (s)': 'Time',
            'Server Time (s)': 'ServerTime',
            'Lap Number': 'Lap',
            'Current Lap Distance (m)': 'LapDist',
            'Current Lap Distance Pct': 'LapDistPct',
            'Best Lap Time (s)': 'BestLapTime',
            'Best Lap Number': 'BestLapNum',
            'Is lap valid': 'IsLapValid', # Booleano

            # Inputs
            'Throttle Pedal Pos': 'Throttle',
            'Brake Pedal Pos': 'Brake',
            'Clutch Pedal Pos': 'Clutch',
            'Steering Wheel Angle (deg)': 'Steer',
            'Steering Shaft Torque (Nm)': 'SteerTorque',
            'Normalized Steering Shaft Torque': 'SteerTorqueNorm',
            'Gear Index': 'Gear',

            # Physics / Motion
            'Speed (m/s)': 'Speed_ms', # Mantener m/s para cálculos si es necesario
            'Speed (Kmh)': 'Speed', # Usar Kmh como principal si existe
            'Lateral Acceleration (m/s^2)': 'G_Lat',
            'Longitudinal Acceleration (m/s^2)': 'G_Lon',
            'Vertical Acceleration (m/s^2)': 'G_Vert',
            'Rotation Pitch (rad)': 'Pitch',
            'Rotation Pitch Rate (rad/s)': 'PitchRate',
            'Rotation Roll (rad)': 'Roll',
            'Rotation Roll Rate (rad/s)': 'RollRate',
            'Rotation Yaw (rad)': 'Yaw',
            'Rotation Yaw Rate (rad/s)': 'YawRate',

            # Engine / Fuel
            'Engine Revolituions Per Minute (RPM)': 'RPM', # Corregir typo común
            'Engine Revolutions Per Minute (RPM)': 'RPM', # Nombre correcto
            'Fuel Level (l)': 'Fuel',

            # Wheels (Ejemplo para LF, replicar para RF, LR, RR)
            'LF Ride Height (m)': 'LF_RideHeight',
            'LF Pressure (kPa)': 'LF_Pressure',
            'LF Inner Average Temperature (C)': 'LF_Temp_Inner', # Simplificado
            'LF Surface Average Temperature (C)': 'LF_Temp_Surface', # Simplificado
            'LF Wear': 'LF_Wear',
            'LF Slip Angle (rad)': 'LF_SlipAngle',
            'LF Revolutions per minute (RPM)': 'LF_WheelRPM',
            'RF Ride Height (m)': 'RF_RideHeight',
            'RF Pressure (kPa)': 'RF_Pressure',
            'RF Inner Average Temperature (C)': 'RF_Temp_Inner',
            'RF Surface Average Temperature (C)': 'RF_Temp_Surface',
            'RF Wear': 'RF_Wear',
            'RF Slip Angle (rad)': 'RF_SlipAngle',
            'RF Revolutions per minute (RPM)': 'RF_WheelRPM',
            'LR Ride Height (m)': 'LR_RideHeight',
            'LR Pressure (kPa)': 'LR_Pressure',
            'LR Inner Average Temperature (C)': 'LR_Temp_Inner',
            'LR Surface Average Temperature (C)': 'LR_Temp_Surface',
            'LR Wear': 'LR_Wear',
            'LR Slip Angle (rad)': 'LR_SlipAngle',
            'LR Revolutions per minute (RPM)': 'LR_WheelRPM',
            'RR Ride Height (m)': 'RR_RideHeight',
            'RR Pressure (kPa)': 'RR_Pressure',
            'RR Inner Average Temperature (C)': 'RR_Temp_Inner',
            'RR Surface Average Temperature (C)': 'RR_Temp_Surface',
            'RR Wear': 'RR_Wear',
            'RR Slip Angle (rad)': 'RR_SlipAngle',
            'RR Revolutions per minute (RPM)': 'RR_WheelRPM',

            # Position
            'Altitude (m)': 'Altitude',
            'Latitude (deg)': 'Latitude',
            'Longitude (deg)': 'Longitude',

            # Assists / Status
            'ABS Active': 'ABSActive', # Booleano
            'ABS Enabled': 'ABSEnabled', # Booleano
            'ABS Level': 'ABSLevel',
            'Traction Control Active': 'TCActive', # Booleano
            'Traction Control Enabled': 'TCEnabled', # Booleano
            'Traction Control Level': 'TCLevel',
            'Speed Limiter On': 'SpeedLimiter', # Booleano
            'Brake Bias': 'BrakeBias',
            'Driver Marker': 'DriverMarker' # Booleano?
        }

        # Aplicar renombrado solo si la columna original existe
        actual_rename_map = {k: v for k, v in rename_map.items() if k in df.columns}
        df.rename(columns=actual_rename_map, inplace=True)
        print(f"Columnas renombradas (mapeadas): {len(actual_rename_map)} de {len(rename_map)}")

        # --- Conversión de Tipos y Limpieza ---
        if 'Time' not in df.columns or 'Lap' not in df.columns:
            missing_cols = [col for col in ['Time', 'Lap'] if col not in df.columns]
            print(f"Error: Faltan columnas esenciales ('Time', 'Lap') después del renombrado. Columnas encontradas: {df.columns.tolist()}")
            return None, metadata

        # Lista más completa para conversión numérica
        numeric_cols_to_check = [
            'Time', 'ServerTime', 'Lap', 'LapDist', 'LapDistPct', 'BestLapTime', 'BestLapNum',
            'Throttle', 'Brake', 'Clutch', 'Steer', 'SteerTorque', 'SteerTorqueNorm', 'Gear',
            'Speed_ms', 'Speed', 'G_Lat', 'G_Lon', 'G_Vert',
            'Pitch', 'PitchRate', 'Roll', 'RollRate', 'Yaw', 'YawRate',
            'RPM', 'Fuel',
            'LF_RideHeight', 'LF_Pressure', 'LF_Temp_Inner', 'LF_Temp_Surface', 'LF_Wear', 'LF_SlipAngle', 'LF_WheelRPM',
            'RF_RideHeight', 'RF_Pressure', 'RF_Temp_Inner', 'RF_Temp_Surface', 'RF_Wear', 'RF_SlipAngle', 'RF_WheelRPM',
            'LR_RideHeight', 'LR_Pressure', 'LR_Temp_Inner', 'LR_Temp_Surface', 'LR_Wear', 'LR_SlipAngle', 'LR_WheelRPM',
            'RR_RideHeight', 'RR_Pressure', 'RR_Temp_Inner', 'RR_Temp_Surface', 'RR_Wear', 'RR_SlipAngle', 'RR_WheelRPM',
            'Altitude', 'Latitude', 'Longitude',
            'ABSLevel', 'TCLevel', 'BrakeBias'
        ]
        print("Convirtiendo columnas a numérico (si aplica)...")
        for col in numeric_cols_to_check:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # Conversión de booleanos (True/False strings)
        bool_cols_to_check = [
            'ABSActive', 'ABSEnabled', 'TCActive', 'TCEnabled',
            'SpeedLimiter', 'DriverMarker', 'IsLapValid'
        ]
        print("Convirtiendo columnas a booleano (si aplica)...")
        for col in bool_cols_to_check:
            if col in df.columns:
                 # Convertir 'True'/'False' strings a booleanos, manejar otros casos como NaN/None
                 if pd.api.types.is_string_dtype(df[col]):
                     df[col] = df[col].str.lower().map({'true': True, 'false': False}).astype(pd.BooleanDtype()) # Usar tipo Booleano nullable
                 elif pd.api.types.is_bool_dtype(df[col]):
                      df[col] = df[col].astype(pd.BooleanDtype()) # Asegurar tipo nullable


        rows_before_drop = len(df)
        df.dropna(subset=['Time', 'Lap'], inplace=True) # Asegurar que Time y Lap son válidos
        rows_after_drop = len(df)
        if rows_before_drop != rows_after_drop:
             print(f"Se eliminaron {rows_before_drop - rows_after_drop} filas con valores NaN en 'Time' o 'Lap'.")

        if 'Lap' in df.columns and pd.api.types.is_numeric_dtype(df['Lap']):
             if df['Lap'].notna().all() and df['Lap'].mod(1).eq(0).all(): # Check if all values are whole numbers and not NA
                 df['Lap'] = df['Lap'].astype(int)
             else:
                 print("Advertencia: Columna 'Lap' contiene valores no enteros o NaN, no se convirtió a int.")

        # Calcular Speed (Kmh) si no existe pero sí Speed_ms
        if 'Speed_ms' in df.columns and 'Speed' not in df.columns:
             if pd.api.types.is_numeric_dtype(df['Speed_ms']):
                 df['Speed'] = df['Speed_ms'] * 3.6
                 print("Columna 'Speed' (Kmh) calculada a partir de 'Speed_ms'.")

        print(f"Carga y limpieza completadas. DataFrame con {len(df)} filas y {len(df.columns)} columnas.")
        print(f"Columnas finales: {df.columns.tolist()}") # Mostrar columnas finales
        return df, metadata

    except FileNotFoundError: # Captura específica para FileNotFoundError
        print(f"Error: El archivo no existe en la ruta: {filepath}")
        return None, None
    except pd.errors.EmptyDataError: # Captura si el CSV está vacío después de skiprows
        print(f"Error: El archivo CSV parece estar vacío o no contiene datos después de la fila {header_row_index+1}.")
        return None, metadata # Devolver metadatos aunque no haya datos tabulares
    except Exception as e:
        print(f"Error crítico durante la carga o procesamiento del CSV {filepath}: {e}")
        # (Código de depuración opcional)
        return None, None