import matplotlib.pyplot as plt
import pandas as pd # Importar pandas para type hinting

def plot_lap_speed_profile(df_telemetry, metadata, lap_number):
    """
    Genera un gráfico del perfil de velocidad (Speed vs Time) para una vuelta específica.

    Args:
        df_telemetry (pd.DataFrame): El DataFrame con los datos de telemetría.
        metadata (dict): El diccionario con los metadatos de la sesión.
        lap_number (int): El número de la vuelta a graficar.
    """
    if df_telemetry is None or 'Lap' not in df_telemetry or 'Time' not in df_telemetry or 'Speed' not in df_telemetry:
        print("Error: DataFrame no válido o faltan columnas ('Lap', 'Time', 'Speed').")
        return
    if not isinstance(lap_number, int) or lap_number <= 0:
         print(f"Error: Número de vuelta inválido: {lap_number}. Debe ser un entero positivo.")
         return

    print(f"\n--- Generando gráfico de VELOCIDAD para la vuelta {lap_number} ---")

    # Filtrar datos para la vuelta seleccionada
    lap_data = df_telemetry[df_telemetry['Lap'] == lap_number].copy() # Usar .copy()

    if lap_data.empty:
        print(f"Error: No se encontraron datos para la vuelta {lap_number}.")
        unique_laps = sorted(df_telemetry['Lap'].unique())
        print(f"Vueltas disponibles: {unique_laps}")
        return

    # Ajustar el tiempo para que empiece desde 0 para esta vuelta
    lap_data['LapTime'] = lap_data['Time'] - lap_data['Time'].iloc[0]

    # Crear el gráfico
    plt.figure(figsize=(16, 7)) # Hacerlo un poco más ancho

    plt.plot(lap_data['LapTime'], lap_data['Speed'], label=f'Velocidad Vuelta {lap_number}')

    # Añadir Títulos y Etiquetas
    track_name = metadata.get('Track', 'Pista Desconocida')
    vehicle_name = metadata.get('Vehicle', 'Vehículo Desconocido')
    title = f'Perfil de Velocidad - Vuelta {lap_number}\n{vehicle_name} @ {track_name}'
    plt.title(title, fontsize=14)
    plt.xlabel('Tiempo en Vuelta (s)')
    plt.ylabel('Velocidad (Kmh)') # Asumiendo que 'Speed' está en Kmh
    plt.legend()
    plt.grid(True)

    # Mostrar el gráfico
    print("Mostrando gráfico...")
    plt.show()
    print("Gráfico cerrado.")


def plot_lap_inputs(df_telemetry, metadata, lap_number):
    """
    Genera gráficos de las entradas del piloto (Acelerador, Freno, Volante)
    para una vuelta específica.
    """
    # --- CORRECCIÓN AQUÍ: Usar los nombres RENOMBRADOS ---
    throttle_col = 'Throttle' # Antes: 'Throttle Pedal Pos'
    brake_col = 'Brake'      # Antes: 'Brake Pedal Pos'
    steer_col = 'Steer'      # Antes: 'Steering Wheel Angle (deg)'
    time_col = 'Time'
    lap_col = 'Lap'

    # Verificar que existen las columnas necesarias (con los nombres nuevos)
    required_cols = [lap_col, time_col, throttle_col, brake_col, steer_col]
    missing_cols = [col for col in required_cols if col not in df_telemetry.columns]
    if missing_cols:
        print(f"Error: Faltan columnas necesarias para el gráfico de entradas: {missing_cols}")
        print(f"Columnas disponibles: {df_telemetry.columns.tolist()}")
        return
    # ... (resto de la validación de lap_number) ...

    print(f"\n--- Generando gráfico de ENTRADAS para la vuelta {lap_number} ---")

    # Filtrar datos para la vuelta seleccionada
    lap_data = df_telemetry[df_telemetry[lap_col] == lap_number].copy()

    if lap_data.empty:
        print(f"Error: No se encontraron datos para la vuelta {lap_number}.")
        return

    # Ajustar el tiempo para que empiece desde 0 para esta vuelta
    lap_data['LapTime'] = lap_data[time_col] - lap_data[time_col].iloc[0]

    # Crear figura con subplots
    fig, axs = plt.subplots(2, 1, figsize=(16, 9), sharex=True)

    # --- Subplot 1: Acelerador y Freno (usando nombres nuevos) ---
    axs[0].plot(lap_data['LapTime'], lap_data[throttle_col], label='Acelerador', color='green', linewidth=1.5)
    axs[0].plot(lap_data['LapTime'], lap_data[brake_col], label='Freno', color='red', linewidth=1.5)
    axs[0].set_ylabel('Pedal (0-1)') # O 'Pedal (%)' si los datos son 0-100
    axs[0].set_ylim(-0.05, 1.05)
    axs[0].legend(loc='upper right')
    axs[0].grid(True)
    track_name = metadata.get('Track', 'Pista Desconocida')
    vehicle_name = metadata.get('Vehicle', 'Vehículo Desconocido')
    fig.suptitle(f'Entradas del Piloto - Vuelta {lap_number}\n{vehicle_name} @ {track_name}', fontsize=14)


    # --- Subplot 2: Volante (usando nombre nuevo) ---
    axs[1].plot(lap_data['LapTime'], lap_data[steer_col], label='Volante', color='blue', linewidth=1.5)
    axs[1].set_xlabel('Tiempo en Vuelta (s)')
    axs[1].set_ylabel('Ángulo Volante (deg)')
    axs[1].legend(loc='upper right')
    axs[1].grid(True)
    axs[1].axhline(0, color='black', linewidth=0.7, linestyle='--')

    # Ajustar espaciado y mostrar
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    print("Mostrando gráfico...")
    plt.show()
    print("Gráfico cerrado.")

def plot_lap_engine(df_telemetry, metadata, lap_number):
    """
    Genera gráficos de RPM y Marcha para una vuelta específica.
    Utiliza ejes Y separados para mejor visualización.

    Args:
        df_telemetry (pd.DataFrame): El DataFrame con los datos de telemetría.
        metadata (dict): El diccionario con los metadatos de la sesión.
        lap_number (int): El número de la vuelta a graficar.
    """
    # Columnas esperadas (después del renombrado en data_loader)
    rpm_col = 'RPM'
    gear_col = 'Gear'
    time_col = 'Time'
    lap_col = 'Lap'

    # Verificar que existen las columnas necesarias
    required_cols = [lap_col, time_col, rpm_col, gear_col]
    missing_cols = [col for col in required_cols if col not in df_telemetry.columns]
    if missing_cols:
        print(f"Error: Faltan columnas necesarias para el gráfico de motor: {missing_cols}")
        print(f"Columnas disponibles: {df_telemetry.columns.tolist()}")
        return
    if not isinstance(lap_number, int) or lap_number <= 0:
         print(f"Error: Número de vuelta inválido: {lap_number}.")
         return

    print(f"\n--- Generando gráfico de MOTOR (RPM/Marcha) para la vuelta {lap_number} ---")

    # Filtrar datos para la vuelta seleccionada
    lap_data = df_telemetry[df_telemetry[lap_col] == lap_number].copy()

    if lap_data.empty:
        print(f"Error: No se encontraron datos para la vuelta {lap_number}.")
        return

    # Ajustar el tiempo para que empiece desde 0 para esta vuelta
    lap_data['LapTime'] = lap_data[time_col] - lap_data[time_col].iloc[0]

    # Crear figura y el primer eje (para RPM)
    fig, ax1 = plt.subplots(figsize=(16, 7))

    # Plot RPM en el primer eje (ax1)
    color_rpm = 'tab:blue'
    ax1.set_xlabel('Tiempo en Vuelta (s)')
    ax1.set_ylabel('RPM', color=color_rpm)
    ax1.plot(lap_data['LapTime'], lap_data[rpm_col], color=color_rpm, label='RPM', linewidth=1.5)
    ax1.tick_params(axis='y', labelcolor=color_rpm)
    ax1.grid(True, axis='y', linestyle='--', alpha=0.7) # Rejilla solo para eje Y primario

    # Crear el segundo eje (ax2) que comparte el mismo eje X (para Marcha)
    ax2 = ax1.twinx()
    color_gear = 'tab:green'
    ax2.set_ylabel('Marcha', color=color_gear)
    # Usar 'step' para graficar cambios discretos de marcha
    # 'where=post' significa que el escalón ocurre después del punto x
    ax2.step(lap_data['LapTime'], lap_data[gear_col], color=color_gear, label='Marcha', where='post', linewidth=1.5)
    ax2.tick_params(axis='y', labelcolor=color_gear)
    # Definir manualmente los ticks del eje Y para las marchas (ej. 0 a 8)
    # Encuentra el rango de marchas para ajustar los ticks
    min_gear = int(lap_data[gear_col].min())
    max_gear = int(lap_data[gear_col].max())
    ax2.set_yticks(range(min_gear, max_gear + 1)) # Ticks enteros para cada marcha


    # Añadir título general
    track_name = metadata.get('Track', 'Pista Desconocida')
    vehicle_name = metadata.get('Vehicle', 'Vehículo Desconocido')
    plt.title(f'RPM y Marcha - Vuelta {lap_number}\n{vehicle_name} @ {track_name}', fontsize=14)

    # Añadir leyendas (un poco más complejo con dos ejes)
    # Obtener handles y labels de ambos ejes y combinarlos
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines + lines2, labels + labels2, loc='upper right')

    fig.tight_layout() # Ajustar layout para evitar solapamientos
    print("Mostrando gráfico...")
    plt.show()
    print("Gráfico cerrado.")

# (Asegúrate de tener 'import matplotlib.pyplot as plt' al inicio)

def plot_track_map(df_telemetry, metadata, lap_number):
    """
    Genera un gráfico 2D simple (mapa) de la trayectoria para una vuelta específica
    usando las columnas de Longitud y Latitud.

    Args:
        df_telemetry (pd.DataFrame): El DataFrame con los datos de telemetría.
        metadata (dict): El diccionario con los metadatos de la sesión.
        lap_number (int): El número de la vuelta a graficar.
    """
    # Columnas esperadas (después del renombrado en data_loader)
    lon_col = 'Longitude'
    lat_col = 'Latitude'
    lap_col = 'Lap'

    # Verificar que existen las columnas necesarias
    required_cols = [lap_col, lon_col, lat_col]
    missing_cols = [col for col in required_cols if col not in df_telemetry.columns]
    if missing_cols:
        print(f"Error: Faltan columnas necesarias para el mapa de pista: {missing_cols}")
        print(f"Columnas disponibles: {df_telemetry.columns.tolist()}")
        return
    if not isinstance(lap_number, int) or lap_number <= 0:
         print(f"Error: Número de vuelta inválido: {lap_number}.")
         return

    print(f"\n--- Generando MAPA DE PISTA para la vuelta {lap_number} ---")

    # Filtrar datos para la vuelta seleccionada
    lap_data = df_telemetry[df_telemetry[lap_col] == lap_number].copy()

    if lap_data.empty or lap_data[lon_col].isnull().all() or lap_data[lat_col].isnull().all():
        print(f"Error: No se encontraron datos de posición válidos (Longitud/Latitud) para la vuelta {lap_number}.")
        return

    # Crear el gráfico
    plt.figure(figsize=(10, 10)) # Usar un aspect ratio cuadrado

    # Graficar la trayectoria
    plt.plot(lap_data[lon_col], lap_data[lat_col], label=f'Trayectoria Vuelta {lap_number}', color='blue', linewidth=1.5)

    # Marcar inicio y fin de la vuelta
    plt.plot(lap_data[lon_col].iloc[0], lap_data[lat_col].iloc[0], 'go', markersize=8, label='Inicio Vuelta') # 'go' = green circle
    plt.plot(lap_data[lon_col].iloc[-1], lap_data[lat_col].iloc[-1], 'rs', markersize=8, label='Fin Vuelta') # 'rs' = red square

    # --- ¡IMPORTANTE! Mantener la relación de aspecto ---
    # Esto es crucial para que el mapa no se vea deformado
    plt.axis('equal')

    # Añadir Títulos y Etiquetas
    track_name = metadata.get('Track', 'Pista Desconocida')
    vehicle_name = metadata.get('Vehicle', 'Vehículo Desconocido')
    title = f'Mapa de Pista - Vuelta {lap_number}\n{vehicle_name} @ {track_name}'
    plt.title(title, fontsize=14)
    plt.xlabel('Longitud (deg)')
    plt.ylabel('Latitud (deg)')
    plt.legend()
    plt.grid(True)

    # Mostrar el gráfico
    print("Mostrando gráfico...")
    plt.show()
    print("Gráfico cerrado.")


