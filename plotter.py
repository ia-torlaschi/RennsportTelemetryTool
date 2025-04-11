# Contenido completo para plotter.py (VERIFICADO con try-except correctos)
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import re # Asegurarse de que re está importado

GRAVITY = 9.80665 # Aceleración estándar de la gravedad en m/s^2

# --- Funciones de Ploteo Actualizadas y Nuevas ---

def plot_lap_speed_profile(df_telemetry, metadata, lap_number):
    """
    Genera un gráfico del perfil de velocidad (Speed vs Distancia) para una vuelta específica.
    """
    dist_col, speed_col, time_col, lap_col = 'LapDist', 'Speed', 'Time', 'Lap'
    required_cols = [lap_col, time_col, speed_col, dist_col]
    if not all(col in df_telemetry.columns for col in required_cols):
        missing = [col for col in required_cols if col not in df_telemetry.columns]
        print(f"Error plot_lap_speed_profile: Faltan columnas: {missing}")
        return
    if not isinstance(lap_number, int) or lap_number <= 0: return

    print(f"\n--- Generando gráfico de VELOCIDAD vs DISTANCIA para la vuelta {lap_number} ---")
    lap_data = df_telemetry[df_telemetry[lap_col] == lap_number].copy()
    if lap_data.empty: print(f"Error: No hay datos para la vuelta {lap_number}."); return

    plt.figure(figsize=(16, 7))
    plt.plot(lap_data[dist_col], lap_data[speed_col], label=f'Velocidad Vuelta {lap_number}', linewidth=1.5)

    track_name = metadata.get('Track', 'Pista Desconocida')
    vehicle_name = metadata.get('Vehicle', 'Vehículo Desconocido')
    track_length_m = None
    try: # <-- INICIO TRY
        match = re.search(r'\(([\d.]+)\s*m\)', track_name)
        if match: track_length_m = float(match.group(1))
    except Exception as e: # <-- EXCEPT CORRESPONDIENTE
        print(f"Advertencia: No se pudo extraer longitud de pista de '{track_name}': {e}")
        # track_length_m permanece None

    title = f'Perfil de Velocidad vs Distancia - Vuelta {lap_number}\n{vehicle_name} @ {track_name}'
    plt.title(title, fontsize=14)
    plt.xlabel('Distancia en Vuelta (m)')
    plt.ylabel('Velocidad (Kmh)')
    if track_length_m: plt.xlim(0, track_length_m)
    plt.legend()
    plt.grid(True)
    print("Mostrando gráfico...")
    plt.show()
    print("Gráfico cerrado.")


def plot_lap_inputs(df_telemetry, metadata, lap_number):
    """
    Genera gráficos de entradas (Acel/Freno/Volante) vs Distancia para una vuelta.
    """
    dist_col, throttle_col, brake_col, steer_col, time_col, lap_col = 'LapDist', 'Throttle', 'Brake', 'Steer', 'Time', 'Lap'
    required_cols = [lap_col, time_col, dist_col, throttle_col, brake_col, steer_col]
    if not all(col in df_telemetry.columns for col in required_cols):
        print(f"Error plot_lap_inputs: Faltan columnas: {[c for c in required_cols if c not in df_telemetry.columns]}")
        return
    if not isinstance(lap_number, int) or lap_number <= 0: return

    print(f"\n--- Generando gráfico de ENTRADAS vs DISTANCIA para la vuelta {lap_number} ---")
    lap_data = df_telemetry[df_telemetry[lap_col] == lap_number].copy()
    if lap_data.empty: print(f"Error: No hay datos para la vuelta {lap_number}."); return

    fig, axs = plt.subplots(2, 1, figsize=(16, 9), sharex=True)

    track_name = metadata.get('Track', 'Pista Desconocida')
    vehicle_name = metadata.get('Vehicle', 'Vehículo Desconocido')
    track_length_m = None
    try: # <-- INICIO TRY
        match = re.search(r'\(([\d.]+)\s*m\)', track_name)
        if match: track_length_m = float(match.group(1))
    except Exception as e: # <-- EXCEPT CORRESPONDIENTE
        print(f"Advertencia: No se pudo extraer longitud de pista de '{track_name}': {e}")

    fig.suptitle(f'Entradas del Piloto vs Distancia - Vuelta {lap_number}\n{vehicle_name} @ {track_name}', fontsize=14)

    axs[0].plot(lap_data[dist_col], lap_data[throttle_col], label='Acelerador', color='green', linewidth=1.5)
    axs[0].plot(lap_data[dist_col], lap_data[brake_col], label='Freno', color='red', linewidth=1.5)
    axs[0].set_ylabel('Pedal (0-1)'); axs[0].set_ylim(-0.05, 1.05); axs[0].legend(loc='upper right'); axs[0].grid(True)
    if track_length_m: axs[0].set_xlim(0, track_length_m)

    axs[1].plot(lap_data[dist_col], lap_data[steer_col], label='Volante', color='blue', linewidth=1.5)
    axs[1].set_xlabel('Distancia en Vuelta (m)'); axs[1].set_ylabel('Ángulo Volante (deg)')
    axs[1].legend(loc='upper right'); axs[1].grid(True); axs[1].axhline(0, color='black', lw=0.7, ls='--')
    if track_length_m: axs[1].set_xlim(0, track_length_m)

    plt.tight_layout(rect=[0, 0.03, 1, 0.95]); print("Mostrando gráfico..."); plt.show(); print("Gráfico cerrado.")


def plot_lap_engine(df_telemetry, metadata, lap_number):
    """
    Genera gráficos de RPM y Marcha vs Distancia para una vuelta específica.
    """
    dist_col, rpm_col, gear_col, time_col, lap_col = 'LapDist', 'RPM', 'Gear', 'Time', 'Lap'
    required_cols = [lap_col, time_col, dist_col, rpm_col, gear_col]
    if not all(col in df_telemetry.columns for col in required_cols):
        print(f"Error plot_lap_engine: Faltan columnas: {[c for c in required_cols if c not in df_telemetry.columns]}")
        return
    if not isinstance(lap_number, int) or lap_number <= 0: return

    print(f"\n--- Generando gráfico de MOTOR (RPM/Marcha) vs DISTANCIA para la vuelta {lap_number} ---")
    lap_data = df_telemetry[df_telemetry[lap_col] == lap_number].copy()
    if lap_data.empty: print(f"Error: No hay datos para la vuelta {lap_number}."); return

    fig, ax1 = plt.subplots(figsize=(16, 7))
    track_name = metadata.get('Track', 'Pista Desconocida'); vehicle_name = metadata.get('Vehicle', 'Vehículo Desconocido'); track_length_m = None
    try: # <-- INICIO TRY
        match = re.search(r'\(([\d.]+)\s*m\)', track_name)
        if match: track_length_m = float(match.group(1))
    except Exception as e: # <-- EXCEPT CORRESPONDIENTE
        print(f"Advertencia: No se pudo extraer longitud de pista de '{track_name}': {e}")

    plt.title(f'RPM y Marcha vs Distancia - Vuelta {lap_number}\n{vehicle_name} @ {track_name}', fontsize=14)

    color_rpm = 'tab:blue'; ax1.set_xlabel('Distancia en Vuelta (m)'); ax1.set_ylabel('RPM', color=color_rpm)
    ax1.plot(lap_data[dist_col], lap_data[rpm_col], color=color_rpm, label='RPM', linewidth=1.5)
    ax1.tick_params(axis='y', labelcolor=color_rpm); ax1.grid(True, axis='y', linestyle='--', alpha=0.7)
    if track_length_m: ax1.set_xlim(0, track_length_m)

    ax2 = ax1.twinx(); color_gear = 'tab:green'; ax2.set_ylabel('Marcha', color=color_gear)
    ax2.step(lap_data[dist_col], lap_data[gear_col], color=color_gear, label='Marcha', where='post', linewidth=1.5)
    ax2.tick_params(axis='y', labelcolor=color_gear)
    if gear_col in lap_data and not lap_data[gear_col].empty and lap_data[gear_col].notna().any():
        try: min_gear = int(lap_data[gear_col].min()); max_gear = int(lap_data[gear_col].max()); ax2.set_yticks(range(max(0, min_gear), max_gear + 1))
        except ValueError: print(f"Advertencia: No se pudo determinar rango de marcha.")

    lines, labels = ax1.get_legend_handles_labels(); lines2, labels2 = ax2.get_legend_handles_labels()
    # Solo mostrar leyenda si ambas listas de labels no están vacías
    if labels or labels2:
         ax2.legend(lines + lines2, labels + labels2, loc='upper right')
    fig.tight_layout(); print("Mostrando gráfico..."); plt.show(); print("Gráfico cerrado.")


def plot_track_map(df_telemetry, metadata, lap_number):
    """Genera un mapa de pista (Lat/Lon)."""
    lon_col, lat_col, lap_col = 'Longitude', 'Latitude', 'Lap'
    required_cols = [lap_col, lon_col, lat_col]
    if not all(col in df_telemetry.columns for col in required_cols):
        print(f"Error plot_track_map: Faltan columnas: {[c for c in required_cols if c not in df_telemetry.columns]}")
        return
    if not isinstance(lap_number, int) or lap_number <= 0: return

    print(f"\n--- Generando MAPA DE PISTA para la vuelta {lap_number} ---")
    lap_data = df_telemetry[df_telemetry[lap_col] == lap_number].copy()
    lap_data.dropna(subset=[lon_col, lat_col], inplace=True)
    if lap_data.empty: print(f"Error: No hay datos de posición válidos para la vuelta {lap_number}."); return

    plt.figure(figsize=(10, 10))
    plt.plot(lap_data[lon_col], lap_data[lat_col], label=f'Trayectoria Vuelta {lap_number}', color='blue', linewidth=1.5)
    # Solo añadir marcadores si hay al menos un punto
    if len(lap_data) > 0:
        plt.plot(lap_data[lon_col].iloc[0], lap_data[lat_col].iloc[0], 'go', markersize=8, label='Inicio Vuelta')
        plt.plot(lap_data[lon_col].iloc[-1], lap_data[lat_col].iloc[-1], 'rs', markersize=8, label='Fin Vuelta')
    plt.axis('equal')

    track_name = metadata.get('Track', 'Pista Desconocida'); vehicle_name = metadata.get('Vehicle', 'Vehículo Desconocido')
    title = f'Mapa de Pista - Vuelta {lap_number}\n{vehicle_name} @ {track_name}'
    plt.title(title, fontsize=14); plt.xlabel('Longitud (deg)'); plt.ylabel('Latitud (deg)')
    plt.legend(); plt.grid(True); print("Mostrando gráfico..."); plt.show(); print("Gráfico cerrado.")


def plot_lap_comparison(df_telemetry, metadata, lap_numbers, channel='Speed'):
    """Superpone trazados vs Distancia para múltiples vueltas."""
    dist_col, lap_col = 'LapDist', 'Lap'
    required_cols = [lap_col, dist_col, channel]
    if not all(col in df_telemetry.columns for col in required_cols):
        missing = [col for col in required_cols if col not in df_telemetry.columns]
        print(f"Error plot_lap_comparison: Faltan columnas: {missing}")
        return
    if not isinstance(lap_numbers, list) or not lap_numbers: return

    print(f"\n--- Generando COMPARACIÓN de Vueltas ({', '.join(map(str, lap_numbers))}) para el canal '{channel}' vs DISTANCIA ---")
    plt.figure(figsize=(16, 7))
    track_name = metadata.get('Track', 'Pista Desconocida'); vehicle_name = metadata.get('Vehicle', 'Vehículo Desconocido'); track_length_m = None
    try: # <-- INICIO TRY
        match = re.search(r'\(([\d.]+)\s*m\)', track_name)
        if match: track_length_m = float(match.group(1))
    except Exception as e: # <-- EXCEPT CORRESPONDIENTE
        print(f"Advertencia: No se pudo extraer longitud de pista de '{track_name}': {e}")

    prop_cycle = plt.rcParams['axes.prop_cycle']; colors = prop_cycle.by_key()['color']
    plotted_lap_count = 0
    for i, lap_num in enumerate(lap_numbers):
        if not isinstance(lap_num, int) or lap_num <= 0: continue
        lap_data = df_telemetry[df_telemetry[lap_col] == lap_num].copy()
        if lap_data.empty or lap_data[dist_col].isnull().all() or lap_data[channel].isnull().all():
             print(f"Advertencia: No hay datos válidos para graficar el canal '{channel}' en la vuelta {lap_num}, se omitirá.")
             continue
        lap_data.dropna(subset=[dist_col, channel], inplace=True)
        if lap_data.empty: continue # Volver a chequear después de dropna
        plt.plot(lap_data[dist_col], lap_data[channel], label=f'Vuelta {lap_num}', color=colors[plotted_lap_count % len(colors)], linewidth=1.5, alpha=0.8)
        plotted_lap_count += 1

    if plotted_lap_count < 1:
        print("Error: No se pudo graficar ninguna de las vueltas seleccionadas."); plt.close(); return

    title = f"Comparación de Vueltas ({channel}) vs Distancia\n{vehicle_name} @ {track_name}"
    plt.title(title, fontsize=14); plt.xlabel('Distancia en Vuelta (m)'); plt.ylabel(channel)
    if track_length_m: plt.xlim(0, track_length_m)
    plt.legend(); plt.grid(True); print("Mostrando gráfico..."); plt.show(); print("Gráfico cerrado.")


def plot_gg(df_telemetry, metadata, lap_number):
    """Genera un Gráfico GG (G-Lat vs G-Lon) en unidades G."""
    g_lat_col, g_lon_col, lap_col = 'G_Lat', 'G_Lon', 'Lap'
    required_cols = [lap_col, g_lat_col, g_lon_col]
    if not all(col in df_telemetry.columns for col in required_cols):
        print(f"Error plot_gg: Faltan columnas: {[c for c in required_cols if c not in df_telemetry.columns]}")
        return
    if not isinstance(lap_number, int) or lap_number <= 0: return

    print(f"\n--- Generando GRÁFICO GG para la vuelta {lap_number} ---")
    lap_data = df_telemetry[df_telemetry[lap_col] == lap_number].copy()
    lap_data.dropna(subset=[g_lat_col, g_lon_col], inplace=True)
    if lap_data.empty: print(f"Error: No hay datos G válidos para la vuelta {lap_number}."); return

    plt.figure(figsize=(10, 10))
    g_lon_g = lap_data[g_lon_col] / GRAVITY; g_lat_g = lap_data[g_lat_col] / GRAVITY
    scatter_color = lap_data.get('Speed'); cmap = 'viridis' if scatter_color is not None and scatter_color.notna().any() else None

    plt.scatter(g_lon_g, g_lat_g, c=scatter_color, cmap=cmap, s=5, alpha=0.5)
    plt.axhline(0, color='black', lw=0.5); plt.axvline(0, color='black', lw=0.5)
    plt.axis('equal'); plt.grid(True)

    track_name = metadata.get('Track', 'Pista Desconocida'); vehicle_name = metadata.get('Vehicle', 'Vehículo Desconocido')
    title = f'Gráfico GG (Fricción) - Vuelta {lap_number}\n{vehicle_name} @ {track_name}'
    plt.title(title, fontsize=14); plt.xlabel('Aceleración Longitudinal (G)'); plt.ylabel('Aceleración Lateral (G)')
    if cmap: cbar = plt.colorbar(label='Velocidad (Kmh)')

    print("Mostrando gráfico..."); plt.show(); print("Gráfico cerrado.")


def plot_delta_time(df_telemetry, metadata, lap_number, reference_lap_number):
    """Calcula y grafica el Delta Time vs Distancia (Positivo = Más Rápido)."""
    dist_col, time_col, lap_col = 'LapDist', 'Time', 'Lap'
    required_cols = [lap_col, time_col, dist_col]
    if not all(col in df_telemetry.columns for col in required_cols):
        print(f"Error plot_delta_time: Faltan columnas: {[c for c in required_cols if c not in df_telemetry.columns]}")
        return
    if not isinstance(lap_number, int) or lap_number <= 0 or \
       not isinstance(reference_lap_number, int) or reference_lap_number <= 0 or \
       lap_number == reference_lap_number:
        print("Error: Números de vuelta inválidos o iguales."); return

    print(f"\n--- Calculando y Graficando DELTA TIME vs DISTANCIA (Vuelta {lap_number} vs Vuelta Ref {reference_lap_number}) ---")

    lap_data_raw = df_telemetry[df_telemetry[lap_col] == lap_number].copy()
    ref_lap_data_raw = df_telemetry[df_telemetry[lap_col] == reference_lap_number].copy()

    lap_data = lap_data_raw.dropna(subset=[dist_col, time_col]).drop_duplicates(subset=[dist_col], keep='first').sort_values(by=dist_col)
    ref_lap_data = ref_lap_data_raw.dropna(subset=[dist_col, time_col]).drop_duplicates(subset=[dist_col], keep='first').sort_values(by=dist_col)

    if lap_data.empty or ref_lap_data.empty: print(f"Error: Datos insuficientes tras limpieza para V{lap_number} o VRef{reference_lap_number}."); return

    base_dist = ref_lap_data[dist_col].values; ref_time = ref_lap_data[time_col].values

    try:
        min_lap_dist, max_lap_dist = lap_data[dist_col].min(), lap_data[dist_col].max()
        valid_base_dist_mask = (base_dist >= min_lap_dist) & (base_dist <= max_lap_dist) & (~np.isnan(base_dist))
        if not np.any(valid_base_dist_mask): print("Error: Rango de distancia no se solapa."); return

        aligned_base_dist = base_dist[valid_base_dist_mask]; aligned_ref_time = ref_time[valid_base_dist_mask]
        if len(lap_data[dist_col].values) < 2 or len(aligned_base_dist) < 1: print("Error: Puntos insuficientes para interpolar."); return

        interp_time_lap = np.interp(aligned_base_dist, lap_data[dist_col].values, lap_data[time_col].values)
        delta_time = -((interp_time_lap - interp_time_lap[0]) - (aligned_ref_time - aligned_ref_time[0]))

    except Exception as e: print(f"Error durante interpolación/cálculo delta: {e}"); return

    plt.figure(figsize=(16, 7))
    plt.plot(aligned_base_dist, delta_time, label=f'Delta Tiempo (V{lap_number} vs Ref V{reference_lap_number})', color='purple', linewidth=1.5)
    plt.axhline(0, color='black', linestyle='--', linewidth=0.7)

    track_name = metadata.get('Track', 'Pista Desconocida'); vehicle_name = metadata.get('Vehicle', 'Vehículo Desconocido'); track_length_m = None
    try: # <-- INICIO TRY
        match = re.search(r'\(([\d.]+)\s*m\)', track_name)
        if match: track_length_m = float(match.group(1))
    except Exception as e: # <-- EXCEPT CORRESPONDIENTE
        print(f"Advertencia: No se pudo extraer longitud de pista de '{track_name}': {e}")

    title = f'Delta Time vs Distancia (V{lap_number} vs V{reference_lap_number})\n{vehicle_name} @ {track_name}'
    plt.title(title, fontsize=14); plt.xlabel('Distancia en Vuelta (m)'); plt.ylabel('Ganancia(+) / Pérdida(-) de Tiempo (s)')
    if track_length_m: plt.xlim(0, track_length_m)
    plt.legend(); plt.grid(True); print("Mostrando gráfico..."); plt.show(); print("Gráfico cerrado.")


def plot_delta_analysis_dashboard(df_telemetry, metadata, lap_number, reference_lap_number):
    """
    Genera un dashboard combinado (Mapa/Delta/Inputs) para comparar dos vueltas.
    """
    dist_col, time_col, lap_col = 'LapDist', 'Time', 'Lap'
    lon_col, lat_col = 'Longitude', 'Latitude'
    throttle_col, brake_col = 'Throttle', 'Brake'

    base_required_cols = [lap_col, time_col, dist_col]
    map_cols = [lon_col, lat_col]; input_cols = [throttle_col, brake_col]
    if not all(col in df_telemetry.columns for col in base_required_cols):
        print(f"Error plot_delta_dashboard: Faltan columnas base: {[c for c in base_required_cols if c not in df_telemetry.columns]}")
        return
    if not isinstance(lap_number, int) or lap_number <= 0 or \
       not isinstance(reference_lap_number, int) or reference_lap_number <= 0 or \
       lap_number == reference_lap_number:
        print("Error: Números de vuelta inválidos o iguales."); return

    print(f"\n--- Generando DASHBOARD DE ANÁLISIS DELTA (Vuelta {lap_number} vs Vuelta Ref {reference_lap_number}) ---")

    lap_data_full = df_telemetry[df_telemetry[lap_col] == lap_number].copy()
    ref_lap_data_full = df_telemetry[df_telemetry[lap_col] == reference_lap_number].copy()

    if lap_data_full.empty or ref_lap_data_full.empty: print(f"Error: Datos insuficientes para V{lap_number} o VRef{reference_lap_number}."); return

    can_plot_map = all(col in df_telemetry.columns for col in map_cols)
    can_plot_delta = all(col in df_telemetry.columns for col in [time_col, dist_col])
    can_plot_inputs = all(col in df_telemetry.columns for col in input_cols + [dist_col])

    delta_time = None; aligned_base_dist = None
    if can_plot_delta:
        delta_lap_data = lap_data_full.dropna(subset=[dist_col, time_col]).drop_duplicates(subset=[dist_col], keep='first').sort_values(by=dist_col)
        delta_ref_lap_data = ref_lap_data_full.dropna(subset=[dist_col, time_col]).drop_duplicates(subset=[dist_col], keep='first').sort_values(by=dist_col)
        if not delta_lap_data.empty and not delta_ref_lap_data.empty:
            try:
                base_dist = delta_ref_lap_data[dist_col].values; ref_time = delta_ref_lap_data[time_col].values
                min_lap_dist, max_lap_dist = delta_lap_data[dist_col].min(), delta_lap_data[dist_col].max()
                valid_base_dist_mask = (base_dist >= min_lap_dist) & (base_dist <= max_lap_dist) & (~np.isnan(base_dist))
                if np.any(valid_base_dist_mask):
                    aligned_base_dist = base_dist[valid_base_dist_mask]; aligned_ref_time = ref_time[valid_base_dist_mask]
                    if len(delta_lap_data[dist_col].values) >= 2 and len(aligned_base_dist) >= 1:
                        interp_time_lap = np.interp(aligned_base_dist, delta_lap_data[dist_col].values, delta_lap_data[time_col].values)
                        delta_time = -((interp_time_lap - interp_time_lap[0]) - (aligned_ref_time - aligned_ref_time[0]))
                    else: can_plot_delta = False
                else: can_plot_delta = False
            except Exception as e: print(f"Error calculando delta time: {e}"); can_plot_delta = False
        else: can_plot_delta = False

    fig, axs = plt.subplots(3, 1, figsize=(16, 12), sharex=True)
    fig.suptitle(f'Análisis Delta: Vuelta {lap_number} vs Referencia V{reference_lap_number}\n{metadata.get("Vehicle","")} @ {metadata.get("Track","")}', fontsize=16)

    ax1 = axs[0]; ax1.set_title('Mapa de Pista Comparativo')
 # --- Subplot 1: Mapa de Pista Superpuesto (Corregido con TEST) ---
    ax1 = axs[0]; ax1.set_title('Mapa de Pista Comparativo')
    if can_plot_map:
        # --- INICIO BLOQUE DE DIAGNÓSTICO ---
        # (Dejamos los prints de diagnóstico por si acaso)
        print("\n--- DIAGNÓSTICO MAPA ---")
        # ... (los prints de forma, NaNs, rango van aquí) ...
        print("--- FIN DIAGNÓSTICO MAPA ---\n")
        # --- FIN BLOQUE DE DIAGNÓSTICO ---


        # --- INICIO TEST LÍNEA DIAGONAL ---
        print("--- MAP PLOT TEST: Intentando dibujar línea diagonal simple ---")
        try:
            # Usar rangos pequeños para asegurar que esté visible si funciona
            test_lon_min, test_lon_max = 8.56, 8.57
            test_lat_min, test_lat_max = 49.32, 49.33
            ax1.plot([test_lon_min, test_lon_max], [test_lat_min, test_lat_max],
                     color='red', linestyle='-', linewidth=2, label='LÍNEA DE TEST')
            print("--- MAP PLOT TEST: Comando ax1.plot ejecutado sin error ---")
            ax1.legend() # Mostrar leyenda para ver si aparece "LÍNEA DE TEST"
        except Exception as e:
            print(f"--- MAP PLOT TEST: ERROR dibujando línea de test: {e} ---")
        # --- FIN TEST LÍNEA DIAGONAL ---


        # --- Código Original Comentado Temporalmente ---
        # map_lap_data = lap_data_full.dropna(subset=map_cols)
        # map_ref_lap_data = ref_lap_data_full.dropna(subset=map_cols)
        # if not map_lap_data.empty and not map_ref_lap_data.empty:
        #      ax1.plot(map_ref_lap_data[lon_col], map_ref_lap_data[lat_col], label=f'Referencia V{reference_lap_number}', color='grey', linestyle='--', linewidth=1.5, alpha=0.8)
        #      ax1.plot(map_lap_data[lon_col], map_lap_data[lat_col], label=f'Vuelta {lap_number}', color='blue', linewidth=1.5)
        #      if not map_lap_data.empty: ax1.plot(map_lap_data[lon_col].iloc[0], map_lap_data[lat_col].iloc[0], 'bo', markersize=6, label=f'Inicio V{lap_number}')
        #      if not map_ref_lap_data.empty: ax1.plot(map_ref_lap_data[lon_col].iloc[0], map_ref_lap_data[lat_col].iloc[0], 'o', color='grey', markersize=6, label=f'Inicio V{reference_lap_number}')
        #      ax1.axis('equal'); ax1.set_xlabel('Longitud (deg)'); ax1.set_ylabel('Latitud (deg)')
        #      ax1.legend(); ax1.grid(True)
        # else:
        #      ax1.text(0.5, 0.5, 'Datos de Mapa insuficientes tras limpiar NaNs', ha='center', va='center', transform=ax1.transAxes)
        #      print("Advertencia: Datos insuficientes para graficar mapa después de limpiar NaNs.")
        ax1.grid(True) # Dejar la rejilla para referencia visual
        ax1.axis('equal') # Mantener axis equal
        ax1.set_xlabel('Longitud (deg)'); ax1.set_ylabel('Latitud (deg)') # Mantener etiquetas
        # --- Fin Código Original Comentado ---
    else:
        ax1.text(0.5, 0.5, 'Columnas Lat/Lon no encontradas', ha='center', va='center', transform=ax1.transAxes)

# ... (resto de la función para subplots 2 y 3 sin cambios) ...

    ax2 = axs[1]; ax2.set_title('Delta Time vs Distancia')
    if can_plot_delta and delta_time is not None and aligned_base_dist is not None:
        ax2.plot(aligned_base_dist, delta_time, label=f'Delta Tiempo (V{lap_number} vs Ref V{reference_lap_number})', color='purple', linewidth=1.5)
        ax2.axhline(0, color='black', linestyle='--', linewidth=0.7)
        ax2.set_ylabel('Ganancia(+) / Pérdida(-) (s)'); ax2.grid(True); ax2.legend()
    else: ax2.text(0.5, 0.5, 'Delta Time no disponible/calculable', ha='center', va='center', transform=ax2.transAxes)

    ax3 = axs[2]; ax3.set_title('Acelerador y Freno vs Distancia')
    if can_plot_inputs:
        input_lap_data = lap_data_full.dropna(subset=input_cols + [dist_col])
        input_ref_lap_data = ref_lap_data_full.dropna(subset=input_cols + [dist_col])
        if not input_lap_data.empty and not input_ref_lap_data.empty:
            ax3.plot(input_lap_data[dist_col], input_lap_data[throttle_col], label=f'Acel V{lap_number}', color='green', linewidth=1.5)
            ax3.plot(input_lap_data[dist_col], input_lap_data[brake_col], label=f'Freno V{lap_number}', color='red', linewidth=1.5)
            ax3.plot(input_ref_lap_data[dist_col], input_ref_lap_data[throttle_col], label=f'Acel Ref V{reference_lap_number}', color='lightgreen', linestyle='--', linewidth=1)
            ax3.plot(input_ref_lap_data[dist_col], input_ref_lap_data[brake_col], label=f'Freno Ref V{reference_lap_number}', color='salmon', linestyle='--', linewidth=1)
            ax3.set_ylabel('Pedal (0-1)'); ax3.set_xlabel('Distancia en Vuelta (m)')
            ax3.set_ylim(-0.05, 1.05); ax3.grid(True); ax3.legend(fontsize='small', ncol=2)
        else: ax3.text(0.5, 0.5, 'Datos Acel/Freno insuficientes tras NaNs', ha='center', va='center', transform=ax3.transAxes)
    else: ax3.text(0.5, 0.5, 'Columnas Acel/Freno no encontradas', ha='center', va='center', transform=ax3.transAxes)

    track_length_m = None
    try:
        track_name = metadata.get('Track', '')
        match = re.search(r'\(([\d.]+)\s*m\)', track_name)
        if match:
            track_length_m = float(match.group(1))
            axs[0].set_xlim(0, track_length_m)
    except Exception:
        try:
            common_min_dist = min(lap_data_full[dist_col].min(), ref_lap_data_full[dist_col].min())
            common_max_dist = max(lap_data_full[dist_col].max(), ref_lap_data_full[dist_col].max())
            axs[0].set_xlim(common_min_dist, common_max_dist)
        except (KeyError, ValueError):
            pass  # Handle cases where data is insufficient
        except (KeyError, ValueError): pass # Evitar error si no hay datos

    plt.tight_layout(rect=[0, 0.03, 1, 0.96])
    print("Mostrando dashboard de análisis delta...")
    plt.show()
    print("Dashboard cerrado.")