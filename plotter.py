# plotter.py (v3 - Dashboard comparativo específico 5 plots)

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker # Para formatear ejes Y
import pandas as pd
import numpy as np
import re

GRAVITY = 9.80665 # Aceleración estándar de la gravedad en m/s^2

# --- Funciones de Ploteo Individuales (SIN CAMBIOS) ---
# plot_lap_speed_profile, plot_lap_inputs, plot_lap_engine

def plot_lap_speed_profile(df_telemetry, metadata, lap_number):
    """Genera un gráfico de Velocidad vs Distancia."""
    # (Código de esta función sin cambios)
    dist_col, speed_col, time_col, lap_col = 'LapDist', 'Speed', 'Time', 'Lap'
    required_cols = [lap_col, time_col, speed_col, dist_col]
    if not all(col in df_telemetry.columns for col in required_cols):
        missing = [col for col in required_cols if col not in df_telemetry.columns]
        print(f"Error plot_lap_speed_profile: Faltan columnas: {missing}")
        return
    if not isinstance(lap_number, int) or lap_number <= 0: return

    print(f"\n--- Generando gráfico de VELOCIDAD vs DISTANCIA para la vuelta {lap_number} ---")
    lap_data = df_telemetry.copy()
    if lap_data.empty: print(f"Error: No hay datos para la vuelta {lap_number}."); return

    plt.figure(figsize=(16, 7))
    plt.plot(lap_data[dist_col], lap_data[speed_col], label=f'Velocidad Vuelta {lap_number}', linewidth=1.5)

    track_name = metadata.get('Track', 'Pista Desconocida'); vehicle_name = metadata.get('Vehicle', 'Vehículo Desconocido'); track_length_m = None
    try:
        match = re.search(r'\(([\d.]+)\s*m\)', track_name)
        if match: track_length_m = float(match.group(1))
        elif isinstance(metadata.get('Track Length M'), (int, float)): track_length_m = metadata['Track Length M']
    except Exception as e: print(f"Advertencia: No se pudo extraer longitud de pista: {e}")

    title = f'Perfil de Velocidad vs Distancia - Vuelta {lap_number}\n{vehicle_name} @ {track_name}'
    plt.title(title, fontsize=14); plt.xlabel('Distancia en Vuelta (m)'); plt.ylabel('Velocidad (Kmh)')
    if track_length_m and track_length_m > 0: plt.xlim(0, track_length_m)
    else:
         if dist_col in lap_data and not lap_data[dist_col].empty: plt.xlim(0, lap_data[dist_col].max() * 1.02)
    plt.legend(); plt.grid(True); print("Mostrando gráfico..."); plt.show(); print("Gráfico cerrado.")


def plot_lap_inputs(df_telemetry, metadata, lap_number):
    """Genera gráficos de Entradas vs Distancia."""
     # (Código de esta función sin cambios)
    dist_col, throttle_col, brake_col, steer_col, time_col, lap_col = 'LapDist', 'Throttle', 'Brake', 'Steer', 'Time', 'Lap'
    required_cols = [lap_col, time_col, dist_col, throttle_col, brake_col, steer_col]
    if not all(col in df_telemetry.columns for col in required_cols):
        print(f"Error plot_lap_inputs: Faltan columnas: {[c for c in required_cols if c not in df_telemetry.columns]}")
        return
    if not isinstance(lap_number, int) or lap_number <= 0: return

    print(f"\n--- Generando gráfico de ENTRADAS vs DISTANCIA para la vuelta {lap_number} ---")
    lap_data = df_telemetry.copy()
    if lap_data.empty: print(f"Error: No hay datos para la vuelta {lap_number}."); return

    fig, axs = plt.subplots(2, 1, figsize=(16, 9), sharex=True)
    track_name = metadata.get('Track', 'Pista Desconocida'); vehicle_name = metadata.get('Vehicle', 'Vehículo Desconocido'); track_length_m = None
    try:
        match = re.search(r'\(([\d.]+)\s*m\)', track_name)
        if match: track_length_m = float(match.group(1))
        elif isinstance(metadata.get('Track Length M'), (int, float)): track_length_m = metadata['Track Length M']
    except Exception as e: print(f"Advertencia: No se pudo extraer longitud de pista: {e}")

    fig.suptitle(f'Entradas del Piloto vs Distancia - Vuelta {lap_number}\n{vehicle_name} @ {track_name}', fontsize=14)
    axs[0].plot(lap_data[dist_col], lap_data[throttle_col], label='Acelerador', color='green', linewidth=1.5)
    axs[0].plot(lap_data[dist_col], lap_data[brake_col], label='Freno', color='red', linewidth=1.5)
    axs[0].set_ylabel('Pedal (0-1)'); axs[0].set_ylim(-0.05, 1.05); axs[0].legend(loc='upper right'); axs[0].grid(True)
    axs[1].plot(lap_data[dist_col], lap_data[steer_col], label='Volante', color='blue', linewidth=1.5)
    axs[1].set_xlabel('Distancia en Vuelta (m)'); axs[1].set_ylabel('Ángulo Volante (deg)')
    axs[1].legend(loc='upper right'); axs[1].grid(True); axs[1].axhline(0, color='black', lw=0.7, ls='--')
    if track_length_m and track_length_m > 0: axs[1].set_xlim(0, track_length_m)
    else:
         if dist_col in lap_data and not lap_data[dist_col].empty: axs[1].set_xlim(0, lap_data[dist_col].max() * 1.02)
    plt.tight_layout(rect=[0, 0.03, 1, 0.95]); print("Mostrando gráfico..."); plt.show(); print("Gráfico cerrado.")


def plot_lap_engine(df_telemetry, metadata, lap_number):
    """Genera gráficos de RPM y Marcha vs Distancia."""
     # (Código de esta función sin cambios)
    dist_col, rpm_col, gear_col, time_col, lap_col = 'LapDist', 'RPM', 'Gear', 'Time', 'Lap'
    required_cols = [lap_col, time_col, dist_col, rpm_col, gear_col]
    if not all(col in df_telemetry.columns for col in required_cols):
        print(f"Error plot_lap_engine: Faltan columnas: {[c for c in required_cols if c not in df_telemetry.columns]}")
        return
    if not isinstance(lap_number, int) or lap_number <= 0: return

    print(f"\n--- Generando gráfico de MOTOR (RPM/Marcha) vs DISTANCIA para la vuelta {lap_number} ---")
    lap_data = df_telemetry.copy()
    if lap_data.empty: print(f"Error: No hay datos para la vuelta {lap_number}."); return

    fig, ax1 = plt.subplots(figsize=(16, 7))
    track_name = metadata.get('Track', 'Pista Desconocida'); vehicle_name = metadata.get('Vehicle', 'Vehículo Desconocido'); track_length_m = None
    try:
        match = re.search(r'\(([\d.]+)\s*m\)', track_name)
        if match: track_length_m = float(match.group(1))
        elif isinstance(metadata.get('Track Length M'), (int, float)): track_length_m = metadata['Track Length M']
    except Exception as e: print(f"Advertencia: No se pudo extraer longitud de pista: {e}")

    plt.title(f'RPM y Marcha vs Distancia - Vuelta {lap_number}\n{vehicle_name} @ {track_name}', fontsize=14)
    color_rpm = 'tab:blue'; ax1.set_xlabel('Distancia en Vuelta (m)'); ax1.set_ylabel('RPM', color=color_rpm)
    ax1.plot(lap_data[dist_col], lap_data[rpm_col], color=color_rpm, label='RPM', linewidth=1.5)
    ax1.tick_params(axis='y', labelcolor=color_rpm); ax1.grid(True, axis='y', linestyle='--', alpha=0.7)
    ax2 = ax1.twinx(); color_gear = 'tab:green'; ax2.set_ylabel('Marcha', color=color_gear)
    ax2.step(lap_data[dist_col], lap_data[gear_col], color=color_gear, label='Marcha', where='post', linewidth=1.5)
    ax2.tick_params(axis='y', labelcolor=color_gear)
    if gear_col in lap_data and not lap_data[gear_col].empty and lap_data[gear_col].notna().any():
        try:
            valid_gears = lap_data[gear_col].dropna().unique()
            min_gear = int(valid_gears.min()); max_gear = int(valid_gears.max())
            if min_gear <= max_gear: ax2.set_yticks(np.arange(min_gear, max_gear + 1))
        except (ValueError, TypeError): print(f"Advertencia: No se pudo determinar rango de marcha.")
    lines, labels = ax1.get_legend_handles_labels(); lines2, labels2 = ax2.get_legend_handles_labels()
    if labels or labels2: ax2.legend(lines + lines2, labels + labels2, loc='upper right')
    if track_length_m and track_length_m > 0: ax1.set_xlim(0, track_length_m)
    else:
         if dist_col in lap_data and not lap_data[dist_col].empty: ax1.set_xlim(0, lap_data[dist_col].max() * 1.02)
    fig.tight_layout(); print("Mostrando gráfico..."); plt.show(); print("Gráfico cerrado.")


# --- *** NUEVA FUNCIÓN DE DASHBOARD COMPARATIVO (Estilo MoTeC v2) *** ---

def plot_comparison_dashboard(df_telemetry, metadata, lap_number, reference_lap_number):
    """
    Genera un dashboard comparativo estilo MoTeC con 5 subplots vs Distancia:
    1. Velocidad
    2. Acelerador
    3. Freno
    4. RPM
    5. Marcha
    """
    # --- Definición de Columnas ---
    dist_col, time_col, lap_col = 'LapDist', 'Time', 'Lap'
    speed_col, throttle_col, brake_col = 'Speed', 'Throttle', 'Brake'
    rpm_col, gear_col = 'RPM', 'Gear'

    # --- Validación Inicial ---
    base_required = [lap_col, time_col, dist_col]
    speed_required = base_required + [speed_col]
    throttle_required = base_required + [throttle_col]
    brake_required = base_required + [brake_col]
    rpm_required = base_required + [rpm_col]
    gear_required = base_required + [gear_col]
    all_required = list(set(speed_required + throttle_required + brake_required + rpm_required + gear_required))

    missing_cols = [col for col in all_required if col not in df_telemetry.columns]
    if missing_cols:
        print(f"Error plot_comparison_dashboard: Faltan columnas necesarias: {missing_cols}")
        return

    if not isinstance(lap_number, int) or not isinstance(reference_lap_number, int) or lap_number == reference_lap_number:
        print("Error: Números de vuelta inválidos o iguales."); return

    print(f"\n--- Generando DASHBOARD COMPARATIVO (V{lap_number} vs Ref V{reference_lap_number}) ---")

    # --- Carga y Preparación de Datos por Vuelta ---
    lap_data_full = df_telemetry[df_telemetry[lap_col] == lap_number].copy()
    ref_lap_data_full = df_telemetry[df_telemetry[lap_col] == reference_lap_number].copy()

    if lap_data_full.empty or ref_lap_data_full.empty:
        print(f"Error: Datos insuficientes para V{lap_number} o VRef{reference_lap_number}."); return

    # --- Creación de la Figura y 5 Ejes (compartiendo X) ---
    fig, axs = plt.subplots(5, 1, figsize=(16, 15), sharex=True) # 5 filas, ajustar altura
    vehicle_info = metadata.get("Vehicle","Vehículo Desconocido")
    track_info = metadata.get("Track","Pista Desconocida")
    fig.suptitle(f'Comparativa: Vuelta {lap_number} vs Referencia V{reference_lap_number}\n{vehicle_info} @ {track_info}', fontsize=16)

    # --- Estilos de línea comunes ---
    lap_color = 'blue'; ref_color = 'orange'
    lap_style = '-'; ref_style = '--'
    lap_lw = 1.5; ref_lw = 1.2

    # --- Subplot 1: Velocidad ---
    ax1 = axs[0]; ax1.set_title('Velocidad')
    spd_lap_data = lap_data_full.dropna(subset=[dist_col, speed_col])
    spd_ref_lap_data = ref_lap_data_full.dropna(subset=[dist_col, speed_col])
    if not spd_lap_data.empty and not spd_ref_lap_data.empty:
        ax1.plot(spd_lap_data[dist_col], spd_lap_data[speed_col], label=f'V{lap_number}', color=lap_color, linestyle=lap_style, linewidth=lap_lw)
        ax1.plot(spd_ref_lap_data[dist_col], spd_ref_lap_data[speed_col], label=f'Ref V{reference_lap_number}', color=ref_color, linestyle=ref_style, linewidth=ref_lw)
        ax1.grid(True); ax1.legend()
    else: ax1.text(0.5, 0.5, 'Datos insuficientes', ha='center', va='center', transform=ax1.transAxes); ax1.grid(True)
    ax1.set_ylabel('Velocidad (Kmh)')

    # --- Subplot 2: Acelerador ---
    ax2 = axs[1]; ax2.set_title('Acelerador')
    thr_lap_data = lap_data_full.dropna(subset=[dist_col, throttle_col])
    thr_ref_lap_data = ref_lap_data_full.dropna(subset=[dist_col, throttle_col])
    if not thr_lap_data.empty and not thr_ref_lap_data.empty:
        ax2.plot(thr_lap_data[dist_col], thr_lap_data[throttle_col], label=f'V{lap_number}', color=lap_color, linestyle=lap_style, linewidth=lap_lw)
        ax2.plot(thr_ref_lap_data[dist_col], thr_ref_lap_data[throttle_col], label=f'Ref V{reference_lap_number}', color=ref_color, linestyle=ref_style, linewidth=ref_lw)
        ax2.set_ylim(-0.05, 1.05); ax2.grid(True); ax2.legend()
    else: ax2.text(0.5, 0.5, 'Datos insuficientes', ha='center', va='center', transform=ax2.transAxes); ax2.grid(True)
    ax2.set_ylabel('Acelerador (0-1)')

    # --- Subplot 3: Freno ---
    ax3 = axs[2]; ax3.set_title('Freno')
    brk_lap_data = lap_data_full.dropna(subset=[dist_col, brake_col])
    brk_ref_lap_data = ref_lap_data_full.dropna(subset=[dist_col, brake_col])
    if not brk_lap_data.empty and not brk_ref_lap_data.empty:
        ax3.plot(brk_lap_data[dist_col], brk_lap_data[brake_col], label=f'V{lap_number}', color=lap_color, linestyle=lap_style, linewidth=lap_lw)
        ax3.plot(brk_ref_lap_data[dist_col], brk_ref_lap_data[brake_col], label=f'Ref V{reference_lap_number}', color=ref_color, linestyle=ref_style, linewidth=ref_lw)
        ax3.set_ylim(-0.05, 1.05); ax3.grid(True); ax3.legend()
    else: ax3.text(0.5, 0.5, 'Datos insuficientes', ha='center', va='center', transform=ax3.transAxes); ax3.grid(True)
    ax3.set_ylabel('Freno (0-1)')

    # --- Subplot 4: RPM ---
    ax4 = axs[3]; ax4.set_title('RPM')
    rpm_lap_data = lap_data_full.dropna(subset=[dist_col, rpm_col])
    rpm_ref_lap_data = ref_lap_data_full.dropna(subset=[dist_col, rpm_col])
    if not rpm_lap_data.empty and not rpm_ref_lap_data.empty:
        ax4.plot(rpm_lap_data[dist_col], rpm_lap_data[rpm_col], label=f'V{lap_number}', color=lap_color, linestyle=lap_style, linewidth=lap_lw)
        ax4.plot(rpm_ref_lap_data[dist_col], rpm_ref_lap_data[rpm_col], label=f'Ref V{reference_lap_number}', color=ref_color, linestyle=ref_style, linewidth=ref_lw)
        ax4.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: format(int(x), ','))) # Formato miles
        ax4.grid(True); ax4.legend()
    else: ax4.text(0.5, 0.5, 'Datos insuficientes', ha='center', va='center', transform=ax4.transAxes); ax4.grid(True)
    ax4.set_ylabel('RPM')

    # --- Subplot 5: Marcha ---
    ax5 = axs[4]; ax5.set_title('Marcha')
    gear_lap_data = lap_data_full.dropna(subset=[dist_col, gear_col])
    gear_ref_lap_data = ref_lap_data_full.dropna(subset=[dist_col, gear_col])
    if not gear_lap_data.empty and not gear_ref_lap_data.empty:
        ax5.step(gear_lap_data[dist_col], gear_lap_data[gear_col], label=f'V{lap_number}', color=lap_color, where='post', linewidth=lap_lw)
        ax5.step(gear_ref_lap_data[dist_col], gear_ref_lap_data[gear_col], label=f'Ref V{reference_lap_number}', color=ref_color, linestyle=ref_style, where='post', linewidth=ref_lw)
        ax5.grid(True); ax5.legend()
        try: # Ajustar ticks Y
             combined = pd.concat([gear_lap_data[gear_col], gear_ref_lap_data[gear_col]]).dropna().unique()
             # Filtrar no numéricos si los hubiera antes de min/max
             numeric_gears = pd.to_numeric(combined, errors='coerce').dropna()
             if not numeric_gears.empty:
                 min_g, max_g = int(numeric_gears.min()), int(numeric_gears.max())
                 if min_g <= max_g: ax5.set_yticks(np.arange(min_g, max_g + 1))
        except Exception as e_tick: print(f"Advertencia: No se pudo ajustar ticks de Marcha: {e_tick}")
    else: ax5.text(0.5, 0.5, 'Datos insuficientes', ha='center', va='center', transform=ax5.transAxes); ax5.grid(True)
    ax5.set_ylabel('Marcha')


    # --- Ajustes Finales ---
    axs[4].set_xlabel('Distancia en Vuelta (m)') # Etiqueta X solo en el último

    xlim_to_set = None; track_length_m = None
    try:
        track_name = metadata.get('Track', '')
        match = re.search(r'\(([\d.]+)\s*m\)', track_name)
        if match: track_length_m = float(match.group(1))
        elif isinstance(metadata.get('Track Length M'), (int, float)): track_length_m = metadata['Track Length M']
        if track_length_m and track_length_m > 0: xlim_to_set = (0, track_length_m)
    except: pass
    if xlim_to_set is None:
         all_dist = pd.concat([lap_data_full[dist_col], ref_lap_data_full[dist_col]]).dropna()
         if not all_dist.empty:
             d_min, d_max = all_dist.min(), all_dist.max()
             if d_min < d_max: xlim_to_set = (d_min, d_max)

    if xlim_to_set: print(f"Dashboard: Aplicando límites X: {xlim_to_set}"); axs[4].set_xlim(xlim_to_set)
    else: print("Advertencia: No se pudo determinar límite X.")

    # --- Mostrar ---
    plt.tight_layout(rect=[0, 0.03, 1, 0.96])
    print("Mostrando dashboard comparativo...")
    plt.show()
    print("Dashboard cerrado.")


# --- Función plot_delta_analysis_dashboard (OBSOLETA) ---
# Se deja comentada por si se quiere recuperar o adaptar en el futuro
# def plot_delta_analysis_dashboard(df_telemetry, metadata, lap_number, reference_lap_number):
#    ... (código de la versión anterior con Mapa/Delta/Inputs(combinado)) ...
#    pass