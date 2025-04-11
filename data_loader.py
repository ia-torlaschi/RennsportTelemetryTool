import pandas as pd
import os
import io

# No definimos CSV_DELIMITER y CSV_SKIPROWS como constantes globales aquí,
# ya que los determinaremos del archivo.

def load_telemetry_csv(filepath):
    """
    Carga un archivo CSV de telemetría de Rennsport en un DataFrame de pandas
    y extrae los metadatos del encabezado.

    Realiza una limpieza básica:
    - Extrae metadatos clave-valor de las líneas iniciales.
    - Determina dinámicamente la fila del encabezado de datos.
    - Elimina espacios en blanco de los nombres de columna.
    - Intenta convertir columnas numéricas clave a tipos numéricos.
    - Elimina filas donde 'Time' o 'Lap' sean inválidos/NaN.
    - Convierte la columna 'Lap' a entero.

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
        # Leer las primeras ~20 líneas para encontrar metadatos y la fila del encabezado
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            potential_header_lines = [f.readline() for _ in range(20)] # Leer hasta 20 líneas

        print("--- Analizando encabezado del CSV ---")
        for i, line in enumerate(potential_header_lines):
            line = line.strip()
            if not line: # Saltar líneas vacías
                continue

            # Intentar detectar delimitador (usaremos el primero encontrado: ; o ,)
            if delimiter is None:
                if ';' in line and line.count(';') > 1:
                    delimiter = ';'
                    print(f"Detectado delimitador: '{delimiter}'")
                elif ',' in line and line.count(',') > 1:
                    delimiter = ','
                    print(f"Detectado delimitador: '{delimiter}'")

            current_delimiter = delimiter if delimiter else ';' # Asumir ';' si no se detecta

            # Buscar metadatos (formato Clave:;Valor)
            if ':' in line and current_delimiter in line:
                 parts = line.split(current_delimiter, 1) # Dividir solo en el primer delimitador
                 key = parts[0].replace(':', '').strip()
                 value = parts[1].strip() if len(parts) > 1 else ''
                 if key and value: # Solo añadir si ambos existen
                      metadata[key] = value
                      print(f"  Metadata encontrada: '{key}': '{value}'")

            # Buscar la fila del encabezado de datos (contiene 'Time' y 'Lap')
            # Usamos los nombres de columna confirmados del ejemplo
            if 'Time (s)' in line and 'Lap Number' in line and current_delimiter in line:
                header_row_index = i
                print(f"Detectada fila de encabezado de datos en línea: {header_row_index + 1}")
                # No necesitamos seguir buscando después de encontrar el encabezado
                break

        if header_row_index == -1:
            print("Error: No se pudo encontrar la fila del encabezado de datos (que contenga 'Time (s)' y 'Lap Number').")
            return None, None
        if delimiter is None:
             print("Advertencia: No se pudo detectar el delimitador automáticamente, se usará ';' por defecto.")
             delimiter = ';' # Usar ; por defecto si no se detectó

        # Ahora leer el archivo completo con pandas, saltando las filas correctas
        print(f"\n--- Cargando datos tabulares con pandas (skiprows={header_row_index}) ---")
        df = pd.read_csv(filepath,
                         delimiter=delimiter,
                         skiprows=header_row_index, # Saltar filas hasta el encabezado inclusive
                         low_memory=False)

        print(f"Archivo CSV '{os.path.basename(filepath)}' leído, procesando...")

        # --- Limpieza y Preparación --- (Similar a antes)
        original_columns = df.columns.tolist()
        df.columns = df.columns.str.strip()
        new_columns = df.columns.tolist()
        if original_columns != new_columns:
             print(f"Nombres de columna limpiados.") # No imprimir todos si son muchos

        # Renombrar columnas para quitar unidades/info extra y simplificar
        rename_map = {
             'Time (s)': 'Time',
             'Lap Number': 'Lap',
             'Speed (m/s)': 'Speed_ms', # Guardar original si existe
             'Speed (Kmh)': 'Speed', # Usar Kmh como 'Speed' principal si existe
             'Engine Revolituions Per Minute (RPM)': 'RPM', # Corregir typo si existe
             'Engine Revolutions Per Minute (RPM)': 'RPM' # Nombre correcto probable
             # Añade más mapeos si es necesario (ej. quitar (deg), (kPa), (C))
        }
        # Aplicar solo los mapeos cuyas claves existan en las columnas
        actual_rename_map = {k: v for k, v in rename_map.items() if k in df.columns}
        df.rename(columns=actual_rename_map, inplace=True)
        print(f"Columnas renombradas: {actual_rename_map}")


        if 'Time' not in df.columns or 'Lap' not in df.columns:
            missing_cols = [col for col in ['Time', 'Lap'] if col not in df.columns]
            print(f"Error: Faltan columnas esenciales ('Time', 'Lap') después del renombrado. Columnas encontradas: {df.columns.tolist()}")
            return None, metadata # Devolver metadatos aunque falle el DataFrame

        numeric_cols_to_check = ['Time', 'Speed', 'Speed_ms', 'RPM', 'Throttle', 'Brake', 'Steer', 'Gear', 'Lap'] # Añadir más si es necesario
        print("Convirtiendo columnas a numérico (si aplica)...")
        for col in numeric_cols_to_check:
            if col in df.columns:
                original_dtype = df[col].dtype
                df[col] = pd.to_numeric(df[col], errors='coerce')
                # if original_dtype != df[col].dtype: # Muy verboso
                #      print(f"  - Columna '{col}' convertida de {original_dtype} a {df[col].dtype}")

        rows_before_drop = len(df)
        df.dropna(subset=['Time', 'Lap'], inplace=True)
        rows_after_drop = len(df)
        if rows_before_drop != rows_after_drop:
             print(f"Se eliminaron {rows_before_drop - rows_after_drop} filas con valores NaN en 'Time' o 'Lap'.")

        if 'Lap' in df.columns and pd.api.types.is_numeric_dtype(df['Lap']):
             if df['Lap'].mod(1).eq(0).all():
                 df['Lap'] = df['Lap'].astype(int)
                 # print("Columna 'Lap' convertida a tipo entero.") # Menos verboso
             else:
                 print("Advertencia: Columna 'Lap' contiene valores no enteros, no se convirtió a int.")

        # Si tenemos Speed_ms pero no Speed (Kmh), calcular Kmh
        if 'Speed_ms' in df.columns and 'Speed' not in df.columns:
             df['Speed'] = df['Speed_ms'] * 3.6
             print("Columna 'Speed' (Kmh) calculada a partir de 'Speed_ms'.")


        print(f"Carga y limpieza completadas. DataFrame con {len(df)} filas y {len(df.columns)} columnas.")
        return df, metadata

    except Exception as e:
        print(f"Error crítico durante la carga o procesamiento del CSV {filepath}: {e}")
        # Imprimir las primeras líneas puede ayudar a depurar
        try:
             with open(filepath, 'r', encoding='utf-8', errors='ignore') as f_err:
                 print("\n--- Primeras 5 líneas del archivo para depuración ---")
                 for i in range(5): print(f_err.readline().strip())
                 print("--- Fin primeras líneas ---")
        except:
             pass # Ignorar errores al intentar leer para depurar
        return None, None