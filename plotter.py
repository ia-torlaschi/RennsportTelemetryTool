import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import re # Asegurarse de que re está importado

GRAVITY = 9.80665 # Aceleración estándar de la gravedad en m/s^2

# --- Funciones de Ploteo Actualizadas y Nuevas ---

def plot_lap_speed_profile(df_telemetry, metadata, lap_number):
    """Genera un gráfico de Velocidad vs Distancia."""
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

    track_name = metadata.get('Track', 'Pista Desconocida'); vehicle_name = metadata.get('Vehicle', 'Vehículo Desconocido'); track_length_m = None
    try: # <-- INICIO TRY
        match = re.search(r'\(([\d.]+)\s*m\)', track_name)
        if match: track_length_m = float(match.group(1))
    except Exception as e: # <-- EXCEPT CORRESPONDIENTE
        print(f"Advertencia: No se pudo extraer longitud de pista de '{track_name}': {e}")
        # track_length_m permanece None

    title = f'Perfil de Velocidad vs Distancia - Vuelta {lap_number}\n{vehicle_name} @ {track_name}'
    plt.title(title, fontsize=14); plt.xlabel('Distancia en Vuelta (m)'); plt.ylabel('Velocidad (Kmh)')
    if track_length_m: plt.xlim(0, track_length_m)
    plt.legend(); plt.grid(True); print("Mostrando gráfico..."); plt.show(); print("Gráfico cerrado.")


def plot_lap_inputs(df_telemetry, metadata, lap_number):
    """Genera gráficos de Entradas vs Distancia."""
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
    track_name = metadata.get('Track', 'Pista Desconocida'); vehicle_name = metadata.get('Vehicle', 'Vehículo Desconocido'); track_length_m = None
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
    """Genera gráficos de RPM y Marcha vs Distancia."""
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
    if labels or labels2: ax2.legend(lines + lines2, labels + labels2, loc='upper right')
    fig.tight_layout(); print("Mostrando gráfico..."); plt.show(); print("Gráfico cerrado.")

def plot_delta_analysis_dashboard(df_telemetry, metadata, lap_number, reference_lap_number):
    """
    Genera un dashboard combinado (Mapa Lat/Lon Superpuesto/Delta/Inputs)
    con diagnóstico de datos Lat/Lon mejorado y orden de ploteo invertido en el mapa.
    """
    # --- Definición de Columnas ---
    dist_col, time_col, lap_col = 'LapDist', 'Time', 'Lap'
    lon_col, lat_col = 'Longitude', 'Latitude'
    throttle_col, brake_col = 'Throttle', 'Brake'
    speed_col = 'Speed'

    # --- Validación Inicial ---
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

    # --- Carga de Datos por Vuelta ---
    lap_data_full = df_telemetry[df_telemetry[lap_col] == lap_number].copy()
    ref_lap_data_full = df_telemetry[df_telemetry[lap_col] == reference_lap_number].copy()

    if lap_data_full.empty or ref_lap_data_full.empty:
        print(f"Error: Datos insuficientes para V{lap_number} o VRef{reference_lap_number}.")
        return

    # --- Verificar Disponibilidad de Datos ---
    can_plot_map = all(col in df_telemetry.columns for col in map_cols)
    can_plot_delta = all(col in df_telemetry.columns for col in [time_col, dist_col])
    can_plot_inputs = all(col in df_telemetry.columns for col in input_cols + [dist_col])

    # --- Cálculo Preliminar del Delta Time ---
    # (Misma lógica de cálculo de delta_time que antes)
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

    # --- Creación de la Figura y Ejes ---
    # Asumiendo sharex=False (o comentado) basado en la última versión
    fig, axs = plt.subplots(3, 1, figsize=(16, 12))
    vehicle_info = metadata.get("Vehicle","Vehículo Desconocido")
    track_info = metadata.get("Track","Pista Desconocida")
    fig.suptitle(f'Análisis Delta: Vuelta {lap_number} vs Referencia V{reference_lap_number}\n{vehicle_info} @ {track_info}', fontsize=16)

    # --- Subplot 1: Mapa de Pista Lat/Lon Superpuesto (DIAGNÓSTICO DATOS + ORDEN INVERTIDO) ---
    ax1 = axs[0]; ax1.set_title('Mapa de Pista Comparativo (Trazadas Lat/Lon)')
    if can_plot_map:
        plot_ok = False
        try:
            # --- Preparar y Diagnosticar Datos del Mapa ---
            print("  Diagnóstico Mapa Lat/Lon (Subplot 1):")
            ref_plot_data = ref_lap_data_full.dropna(subset=map_cols)
            print(f"    Ref V{reference_lap_number}: {len(ref_plot_data)} puntos Lat/Lon válidos.")
            # *** NUEVO: Imprimir muestra de datos y verificar inf/nan ***
            if not ref_plot_data.empty:
                print(f"      Ref V{reference_lap_number} - Primeros 3 puntos (Lon, Lat):")
                print(ref_plot_data[[lon_col, lat_col]].head(3).to_string(index=False))
                print(f"      Ref V{reference_lap_number} - Últimos 3 puntos (Lon, Lat):")
                print(ref_plot_data[[lon_col, lat_col]].tail(3).to_string(index=False))
                print(f"      Ref V{reference_lap_number} - NaNs en Lon: {ref_plot_data[lon_col].isna().sum()}, Inf en Lon: {np.isinf(ref_plot_data[lon_col]).sum()}")
                print(f"      Ref V{reference_lap_number} - NaNs en Lat: {ref_plot_data[lat_col].isna().sum()}, Inf en Lat: {np.isinf(ref_plot_data[lat_col]).sum()}")

            lap_plot_data = lap_data_full.dropna(subset=map_cols)
            print(f"    Lap V{lap_number}: {len(lap_plot_data)} puntos Lat/Lon válidos.")
            # (Opcional: añadir prints similares para lap_plot_data si es necesario)


            # --- Graficar si hay datos (ORDEN INVERTIDO) ---
            # 1. Graficar vuelta ACTUAL primero (azul)
            if not lap_plot_data.empty:
                 print(f"    Intentando graficar Lap V{lap_number} PRIMERO...")
                 ax1.plot(lap_plot_data[lon_col], lap_plot_data[lat_col],
                          label=f'Vuelta {lap_number}',
                          color='blue',
                          linewidth=1.2,
                          alpha=0.9,
                          zorder=2) # Delante
                 plot_ok = True

            # 2. Graficar vuelta de REFERENCIA después (naranja)
            if not ref_plot_data.empty:
                 print(f"    Intentando graficar Ref V{reference_lap_number} DESPUÉS...")
                 if ref_plot_data[lon_col].nunique() <= 1 and ref_plot_data[lat_col].nunique() <= 1:
                     print(f"    ADVERTENCIA: Datos de Ref V{reference_lap_number} parecen ser un único punto.")
                     ax1.plot(ref_plot_data[lon_col].iloc[0], ref_plot_data[lat_col].iloc[0], 'o', color='orange', markersize=6, label=f'Referencia V{reference_lap_number} (Punto)')
                 else:
                     # Graficar línea referencia
                     ax1.plot(ref_plot_data[lon_col], ref_plot_data[lat_col],
                              label=f'Referencia V{reference_lap_number}',
                              color='orange',
                              linestyle='-',
                              linewidth=1.5,
                              alpha=0.9,
                              zorder=1) # Detrás (aunque se plotea después, zorder lo controla)
                 plot_ok = True # Marcar como ok si se intentó

            # --- Configuración Final del Subplot del Mapa ---
            ax1.set_xlabel('Longitud (deg)')
            ax1.set_ylabel('Latitud (deg)')
            ax1.grid(True)
            if plot_ok:
                 ax1.legend()
                 print("    Líneas del mapa graficadas (o intentado - ORDEN CAMBIADO).")
                 # Control de aspecto (igual que antes)
                 try:
                     all_map_data = pd.concat([ref_plot_data, lap_plot_data]).dropna(subset=map_cols)
                     if not all_map_data.empty:
                         mean_latitude = all_map_data[lat_col].mean()
                         if not pd.isna(mean_latitude):
                             print(f"    Aplicando ax1.set_aspect() con latitud media: {mean_latitude:.4f} grados")
                             ax1.set_aspect(1.0 / np.cos(np.radians(mean_latitude)), adjustable='box')
                         else: ax1.set_aspect('auto')
                     else: ax1.set_aspect('auto')
                 except Exception as aspect_e:
                     print(f"    Error aplicando set_aspect: {aspect_e}. Usando aspecto por defecto.")
                     ax1.set_aspect('auto')
            else:
                 ax1.text(0.5, 0.5, 'Datos Lat/Lon insuficientes tras NaNs.', ha='center', va='center', transform=ax1.transAxes)
                 print("    ADVERTENCIA: No se graficó el mapa Lat/Lon por falta de datos válidos.")

        except Exception as e:
            print(f"--- ERROR durante el ploteo del mapa Lat/Lon (Orden Invertido): {e} ---")
            ax1.text(0.5, 0.5, f'Error al graficar mapa Lat/Lon:\n{e}', ha='center', va='center', transform=ax1.transAxes)
            ax1.set_xlabel('Longitud (deg)'); ax1.set_ylabel('Latitud (deg)'); ax1.grid(True)
    else:
        # Mensaje si faltan columnas Lat/Lon
        ax1.text(0.5, 0.5, 'Columnas Longitude/Latitude no encontradas', ha='center', va='center', transform=ax1.transAxes)
        ax1.grid(True)
        ax1.set_xlabel('Longitud (deg)'); ax1.set_ylabel('Latitud (deg)')


    # --- Subplot 2: Delta Time ---
    # (Sin cambios)
    ax2 = axs[1]; ax2.set_title('Delta Time vs Distancia')
    if can_plot_delta and delta_time is not None and aligned_base_dist is not None:
        ax2.plot(aligned_base_dist, delta_time, label=f'Delta Tiempo (V{lap_number} vs Ref V{reference_lap_number})', color='purple', linewidth=1.5)
        ax2.axhline(0, color='black', linestyle='--', linewidth=0.7)
        if len(delta_time) > 1:
            try:
                p_low = np.percentile(delta_time, 1); p_high = np.percentile(delta_time, 99)
                data_range = p_high - p_low; margin = max(data_range * 0.10, 0.1)
                y_min = p_low - margin; y_max = p_high + margin
                if np.isclose(y_min, y_max): y_min, y_max = -0.5, 0.5
                ax2.set_ylim(y_min, y_max)
            except Exception as e: print(f"Dashboard: Advertencia - ajuste límites Y Delta: {e}")
        ax2.set_ylabel('Ganancia(+) / Pérdida(-) (s)'); ax2.grid(True); ax2.legend()
        ax2.set_xlabel('Distancia en Vuelta (m)') # Asumiendo sharex=False
    else:
        ax2.text(0.5, 0.5, 'Delta Time no disponible/calculable', ha='center', va='center', transform=ax2.transAxes); ax2.grid(True)
        ax2.set_xlabel('Distancia en Vuelta (m)') # Asumiendo sharex=False

    # --- Subplot 3: Acelerador / Freno Superpuesto ---
    # (Sin cambios)
    ax3 = axs[2]; ax3.set_title('Acelerador y Freno vs Distancia')
    if can_plot_inputs:
        input_lap_data = lap_data_full.dropna(subset=input_cols + [dist_col])
        input_ref_lap_data = ref_lap_data_full.dropna(subset=input_cols + [dist_col])
        if not input_lap_data.empty and not input_ref_lap_data.empty:
            ax3.plot(input_lap_data[dist_col], input_lap_data[throttle_col], label=f'Acel V{lap_number}', color='green', linewidth=1.5, alpha=0.9)
            ax3.plot(input_lap_data[dist_col], input_lap_data[brake_col], label=f'Freno V{lap_number}', color='red', linewidth=1.5, alpha=0.9)
            ax3.plot(input_ref_lap_data[dist_col], input_ref_lap_data[throttle_col], label=f'Acel Ref V{reference_lap_number}', color='limegreen', linestyle='--', linewidth=1, alpha=0.7)
            ax3.plot(input_ref_lap_data[dist_col], input_ref_lap_data[brake_col], label=f'Freno Ref V{reference_lap_number}', color='salmon', linestyle='--', linewidth=1, alpha=0.7)
            ax3.set_ylabel('Pedal (0-1)'); ax3.set_xlabel('Distancia en Vuelta (m)')
            ax3.set_ylim(-0.05, 1.05); ax3.grid(True); ax3.legend(fontsize='small', ncol=2)
        else: ax3.text(0.5, 0.5, 'Datos Acel/Freno insuficientes tras NaNs', ha='center', va='center', transform=ax3.transAxes); ax3.grid(True)
    else: ax3.text(0.5, 0.5, 'Columnas Acel/Freno no encontradas', ha='center', va='center', transform=ax3.transAxes); ax3.grid(True)

    # --- Ajustar Límites X ---
    # (Sin cambios, aplica a ax2 y ax3 si sharex=False)
    xlim_to_set = None
    track_length_m = None
    try:
        track_name = metadata.get('Track', '')
        match = re.search(r'\(([\d.]+)\s*m\)', track_name)
        if match:
            track_length_m_extracted = float(match.group(1))
            if track_length_m_extracted > 0:
                xlim_to_set = (0, track_length_m_extracted)
                track_length_m = track_length_m_extracted
    except Exception: pass
    if xlim_to_set is None and aligned_base_dist is not None and len(aligned_base_dist) > 0:
         data_min = np.nanmin(aligned_base_dist)
         data_max = np.nanmax(aligned_base_dist)
         if data_min < data_max: xlim_to_set = (data_min, data_max)
    if xlim_to_set:
        print(f"Dashboard: Aplicando límites eje X (Distancia) a ax2 y ax3: {xlim_to_set}")
        ax2.set_xlim(xlim_to_set)
        ax3.set_xlim(xlim_to_set)

    # --- Mostrar el Dashboard ---
    plt.tight_layout(rect=[0, 0.03, 1, 0.96])
    print("Mostrando dashboard de análisis delta...")
    plt.show()
    print("Dashboard cerrado.")

# --- FIN de la función plot_delta_analysis_dashboard ---