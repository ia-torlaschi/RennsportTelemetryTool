# plotter.py (vFinal Definitiva - Corrección Indentación + Ticks Marcha)

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker # Para formatear ejes Y
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation
import pandas as pd
import numpy as np
import re
import traceback # Para mejor detalle en errores de plot

GRAVITY = 9.80665 # Aceleración estándar de la gravedad en m/s^2

# --- Funciones de Ploteo Individuales (Con corrección de indentación y mejoras menores) ---

def plot_lap_speed_profile(df_lap, metadata, lap_number):
    """Genera un gráfico de Velocidad vs Distancia para una vuelta específica."""
    dist_col, speed_col, time_col = 'LapDist', 'Speed', 'Time'
    required_cols = [time_col, speed_col, dist_col]
    if not all(col in df_lap.columns for col in required_cols):
        missing = [col for col in required_cols if col not in df_lap.columns]
        print(f"Error plot_lap_speed_profile V{lap_number}: Faltan columnas: {missing}")
        return
    if not isinstance(lap_number, int) or lap_number <= 0: return
    if df_lap.empty or df_lap[dist_col].isnull().all() or df_lap[speed_col].isnull().all():
        print(f"Error plot_lap_speed_profile: No hay datos válidos para la vuelta {lap_number}.")
        return

    print(f"\n--- Generando gráfico VELOCIDAD V{lap_number} ---")
    try:
        plt.figure(figsize=(16, 7))
        plot_data = df_lap.dropna(subset=[dist_col, speed_col])
        if not plot_data.empty:
             plt.plot(plot_data[dist_col], plot_data[speed_col], label=f'Velocidad V{lap_number}', linewidth=1.5)
        else:
             plt.text(0.5, 0.5, 'Datos insuficientes (NaNs)', ha='center', va='center', transform=plt.gca().transAxes)

        track_name = metadata.get('Track', 'Pista Desconocida'); vehicle_name = metadata.get('Vehicle', 'Vehículo'); track_length_m = None
        # --- Bloque try/except CORREGIDO ---
        try:
            track_name_str = str(metadata.get('Track', ''))
            match = re.search(r'\(([\d.]+)\s*m\)', track_name_str)
            if match:
                track_length_m = float(match.group(1))
            # Comprobar también la clave directa 'Track Length M'
            elif metadata.get('Track Length M') is not None:
                 try: # Intentar convertir este metadato directamente
                      track_length_m = float(metadata['Track Length M'])
                 except (ValueError, TypeError):
                      print(f"Adv: Metadato 'Track Length M' no es numérico: {metadata['Track Length M']}")
        except Exception as e_len: # Capturar cualquier error durante la extracción
             print(f"Adv: No se pudo extraer longitud de pista ({e_len})")
        # --- Fin Bloque try/except CORREGIDO ---

        title = f'Velocidad vs Distancia - Vuelta {lap_number}\n{vehicle_name} @ {track_name}'
        plt.title(title, fontsize=14); plt.xlabel('Distancia (m)'); plt.ylabel('Velocidad (Kmh)')
        if track_length_m and track_length_m > 0: plt.xlim(0, track_length_m)
        elif not plot_data.empty: plt.xlim(plot_data[dist_col].min(), plot_data[dist_col].max()) # Usar min/max de datos si no hay longitud
        plt.legend(); plt.grid(True, linestyle=':', alpha=0.7); print("Mostrando..."); plt.show(); print("Cerrado.")
    except Exception as e:
        print(f"Error FATAL al generar plot_lap_speed_profile V{lap_number}: {e}")
        traceback.print_exc()


def plot_lap_inputs(df_lap, metadata, lap_number):
    """Genera gráficos de Entradas vs Distancia para una vuelta específica."""
    dist_col, throttle_col, brake_col, steer_col, time_col = 'LapDist', 'Throttle', 'Brake', 'Steer', 'Time'
    required_cols = [time_col, dist_col, throttle_col, brake_col, steer_col]
    if not all(col in df_lap.columns for col in required_cols):
        print(f"Error plot_lap_inputs V{lap_number}: Faltan {[c for c in required_cols if c not in df_lap.columns]}")
        return
    if not isinstance(lap_number, int) or lap_number <= 0: return
    if df_lap.empty: print(f"Error plot_lap_inputs: No datos V{lap_number}."); return

    print(f"\n--- Generando gráfico ENTRADAS V{lap_number} ---")
    try:
        fig, axs = plt.subplots(2, 1, figsize=(16, 9), sharex=True, gridspec_kw={'hspace': 0.1})
        track_name = metadata.get('Track', 'Pista Desconocida'); vehicle_name = metadata.get('Vehicle', 'Vehículo'); track_length_m = None
        # --- Bloque try/except CORREGIDO ---
        try:
            track_name_str = str(metadata.get('Track', ''))
            match = re.search(r'\(([\d.]+)\s*m\)', track_name_str)
            if match:
                 track_length_m = float(match.group(1))
            elif metadata.get('Track Length M') is not None:
                 try: track_length_m = float(metadata['Track Length M'])
                 except (ValueError, TypeError): print(f"Adv: Metadato 'Track Length M' no numérico: {metadata['Track Length M']}")
        except Exception as e_len: print(f"Adv: No se pudo extraer longitud de pista ({e_len})")
        # --- Fin Bloque try/except CORREGIDO ---

        fig.suptitle(f'Entradas Piloto vs Distancia - Vuelta {lap_number}\n{vehicle_name} @ {track_name}', fontsize=14)

        # Subplot Pedales
        thr_data = df_lap.dropna(subset=[dist_col, throttle_col])
        brk_data = df_lap.dropna(subset=[dist_col, brake_col])
        if not thr_data.empty: axs[0].plot(thr_data[dist_col], thr_data[throttle_col], label='Acelerador', color='green', linewidth=1.5)
        if not brk_data.empty: axs[0].plot(brk_data[dist_col], brk_data[brake_col], label='Freno', color='red', linewidth=1.5)
        axs[0].set_ylabel('Pedal (0-1)'); axs[0].set_ylim(-0.05, 1.05); axs[0].legend(loc='upper right'); axs[0].grid(True, linestyle=':', alpha=0.7)
        axs[0].tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)

        # Subplot Volante
        steer_data = df_lap.dropna(subset=[dist_col, steer_col])
        if not steer_data.empty:
             axs[1].plot(steer_data[dist_col], steer_data[steer_col], label='Volante', color='blue', linewidth=1.5)
             axs[1].axhline(0, color='black', lw=0.7, ls='--')
        axs[1].set_xlabel('Distancia (m)'); axs[1].set_ylabel('Volante (deg)'); axs[1].legend(loc='upper right'); axs[1].grid(True, linestyle=':', alpha=0.7)
        axs[1].tick_params(axis='x', which='both', bottom=True, top=False, labelbottom=True)

        # Límites X
        if track_length_m and track_length_m > 0: axs[1].set_xlim(0, track_length_m)
        elif not df_lap[dist_col].dropna().empty: axs[1].set_xlim(df_lap[dist_col].min(), df_lap[dist_col].max())

        plt.tight_layout(rect=[0, 0.03, 1, 0.95]); print("Mostrando..."); plt.show(); print("Cerrado.")
    except Exception as e:
        print(f"Error FATAL al generar plot_lap_inputs V{lap_number}: {e}")
        traceback.print_exc()


def plot_lap_engine(df_lap, metadata, lap_number):
    """Genera gráficos de RPM y Marcha vs Distancia para una vuelta específica."""
    dist_col, rpm_col, gear_col, time_col = 'LapDist', 'RPM', 'Gear', 'Time'
    required_cols = [time_col, dist_col, rpm_col, gear_col]
    if not all(col in df_lap.columns for col in required_cols):
        print(f"Error plot_lap_engine V{lap_number}: Faltan {[c for c in required_cols if c not in df_lap.columns]}")
        return
    if not isinstance(lap_number, int) or lap_number <= 0: return
    if df_lap.empty: print(f"Error plot_lap_engine: No datos V{lap_number}."); return

    print(f"\n--- Generando gráfico MOTOR V{lap_number} ---")
    try:
        fig, ax1 = plt.subplots(figsize=(16, 7))
        track_name = metadata.get('Track', 'Pista Desconocida'); vehicle_name = metadata.get('Vehicle', 'Vehículo'); track_length_m = None
        # --- Bloque try/except CORREGIDO ---
        try:
            track_name_str = str(metadata.get('Track', ''))
            match = re.search(r'\(([\d.]+)\s*m\)', track_name_str)
            if match:
                 track_length_m = float(match.group(1))
            elif metadata.get('Track Length M') is not None:
                 try: track_length_m = float(metadata['Track Length M'])
                 except (ValueError, TypeError): print(f"Adv: Metadato 'Track Length M' no numérico: {metadata['Track Length M']}")
        except Exception as e_len: print(f"Adv: No se pudo extraer longitud de pista ({e_len})")
        # --- Fin Bloque try/except CORREGIDO ---

        plt.title(f'RPM y Marcha vs Distancia - Vuelta {lap_number}\n{vehicle_name} @ {track_name}', fontsize=14)

        # Eje RPM
        color_rpm='tab:blue'; ax1.set_xlabel('Distancia (m)'); ax1.set_ylabel('RPM', color=color_rpm)
        rpm_data = df_lap.dropna(subset=[dist_col, rpm_col])
        if not rpm_data.empty:
            ax1.plot(rpm_data[dist_col], rpm_data[rpm_col], color=color_rpm, label='RPM', linewidth=1.5)
            ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: format(int(x), ',')))
        ax1.tick_params(axis='y', labelcolor=color_rpm); ax1.grid(True, axis='y', linestyle=':', alpha=0.7)

        # Eje Marcha
        ax2 = ax1.twinx(); color_gear = 'tab:green'; ax2.set_ylabel('Marcha', color=color_gear)
        gear_data = df_lap.dropna(subset=[dist_col, gear_col])
        if not gear_data.empty:
            ax2.step(gear_data[dist_col], gear_data[gear_col], color=color_gear, label='Marcha', where='post', linewidth=1.5)
            ax2.tick_params(axis='y', labelcolor=color_gear)
            # Ajustar ticks Marcha (robusto)
            try:
                # Usar unique() sobre la serie filtrada directamente
                unique_gears = gear_data[gear_col].unique()
                valid_gears = pd.to_numeric(unique_gears, errors='coerce')
                valid_gears = valid_gears[~np.isnan(valid_gears)]
                if valid_gears.size > 0:
                    min_g, max_g = int(valid_gears.min()), int(valid_gears.max())
                    if min_g <= max_g: ax2.set_yticks(np.arange(min_g, max_g + 1))
            except Exception as e_tick: print(f"Adv Ticks Marcha V{lap_number}: {e_tick}")

        # Leyenda combinada
        lines, labels = ax1.get_legend_handles_labels(); lines2, labels2 = ax2.get_legend_handles_labels()
        if labels or labels2: ax2.legend(lines + lines2, labels + labels2, loc='upper right')

        # Límites X
        if track_length_m and track_length_m > 0: ax1.set_xlim(0, track_length_m)
        elif not df_lap[dist_col].dropna().empty: ax1.set_xlim(df_lap[dist_col].min(), df_lap[dist_col].max())

        fig.tight_layout(); print("Mostrando..."); plt.show(); print("Cerrado.")
    except Exception as e:
        print(f"Error FATAL al generar plot_lap_engine V{lap_number}: {e}")
        traceback.print_exc()


# --- DASHBOARD COMPARATIVO (CON CORRECCIÓN TICKS MARCHA Y MEJORAS) ---
def plot_comparison_dashboard(df_telemetry, metadata, lap_number, reference_lap_number, laps_info_df=None): # Aceptar laps_info_df opcional pero NO USARLO INTERNAMENTE
    """Genera dashboard comparativo con 5 subplots: Vel, Thr, Brk, RPM, Gear."""
    # --- Definición Columnas ---
    dist_col, time_col, lap_col = 'LapDist', 'Time', 'Lap'
    speed_col, throttle_col, brake_col = 'Speed', 'Throttle', 'Brake'
    rpm_col, gear_col = 'RPM', 'Gear'
    required_cols = list(set([lap_col, time_col, dist_col, speed_col, throttle_col, brake_col, rpm_col, gear_col]))
    missing_cols = [col for col in required_cols if col not in df_telemetry.columns]
    if missing_cols: print(f"Error Dashboard: Faltan columnas: {missing_cols}"); return
    if not (isinstance(lap_number, int) and isinstance(reference_lap_number, int) and lap_number != reference_lap_number): print("Error: Vueltas inválidas."); return

    print(f"\n--- Generando DASHBOARD COMPARATIVO (V{lap_number} vs Ref V{reference_lap_number}) ---")

    # --- Preparación Datos ---
    lap_data_full = df_telemetry[df_telemetry[lap_col] == lap_number].copy()
    ref_lap_data_full = df_telemetry[df_telemetry[lap_col] == reference_lap_number].copy()
    if lap_data_full.empty or ref_lap_data_full.empty: print(f"Error: Datos insuficientes V{lap_number} o VRef{reference_lap_number}."); return

    # --- Creación Figura y Ejes ---
    fig, axs = plt.subplots(5, 1, figsize=(16, 15), sharex=True, gridspec_kw={'hspace': 0.1})
    vehicle_info = metadata.get("Vehicle","Vehículo"); track_info = metadata.get("Track","Pista")
    fig.suptitle(f'Comparativa: V{lap_number} vs Ref V{reference_lap_number}\n{vehicle_info} @ {track_info}', fontsize=16)
    lap_color = 'blue'; ref_color = 'orange'; lap_style = '-'; ref_style = '--'; lap_lw = 1.5; ref_lw = 1.2

    # --- Función Auxiliar Plot ---
    def plot_subplot(ax, data_lap, data_ref, col, title, ylabel, ylim=None, use_step=False, format_y_thousands=False):
        ax.set_title(title, loc='left', fontsize=10)
        plot_data_lap = data_lap.dropna(subset=[dist_col, col])
        plot_data_ref = data_ref.dropna(subset=[dist_col, col])

        if not plot_data_lap.empty and not plot_data_ref.empty:
            plot_args_lap = {'label': f'V{lap_number}', 'color': lap_color, 'linestyle': lap_style, 'linewidth': lap_lw}
            plot_args_ref = {'label': f'Ref V{reference_lap_number}', 'color': ref_color, 'linestyle': ref_style, 'linewidth': ref_lw}
            plot_func = ax.step if use_step else ax.plot
            if use_step: plot_args_lap['where'] = 'post'; plot_args_ref['where'] = 'post'

            try: # Envuelve el ploteo en try-except por si hay datos inconsistentes
                plot_func(plot_data_lap[dist_col], plot_data_lap[col], **plot_args_lap)
                plot_func(plot_data_ref[dist_col], plot_data_ref[col], **plot_args_ref)
            except Exception as e_plot:
                print(f"Error al plotear subplot '{title}': {e_plot}")
                ax.text(0.5, 0.5, f'Error Ploteando Datos ({e_plot})', color='red', ha='center', va='center', transform=ax.transAxes)

            ax.grid(True, linestyle=':', alpha=0.7); ax.legend(fontsize=9)
            if ylim: ax.set_ylim(ylim)
            if format_y_thousands: ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: format(int(x), ',')))
        else:
            ax.text(0.5, 0.5, 'Datos insuficientes', ha='center', va='center', transform=ax.transAxes); ax.grid(True, linestyle=':', alpha=0.7)
        ax.set_ylabel(ylabel, fontsize=9)
        ax.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)


    # --- Ploteo de cada Subplot ---
    try: plot_subplot(axs[0], lap_data_full, ref_lap_data_full, speed_col, 'Velocidad', 'Kmh')
    except Exception as e: print(f"Error subplot Velocidad: {e}"); axs[0].text(0.5, 0.5, 'Error', ha='c', va='c', transform=axs[0].transAxes)
    try: plot_subplot(axs[1], lap_data_full, ref_lap_data_full, throttle_col, 'Acelerador', '0-1', ylim=(-0.05, 1.05))
    except Exception as e: print(f"Error subplot Acelerador: {e}"); axs[1].text(0.5, 0.5, 'Error', ha='c', va='c', transform=axs[1].transAxes)
    try: plot_subplot(axs[2], lap_data_full, ref_lap_data_full, brake_col, 'Freno', '0-1', ylim=(-0.05, 1.05))
    except Exception as e: print(f"Error subplot Freno: {e}"); axs[2].text(0.5, 0.5, 'Error', ha='c', va='c', transform=axs[2].transAxes)
    try: plot_subplot(axs[3], lap_data_full, ref_lap_data_full, rpm_col, 'RPM', 'RPM', format_y_thousands=True)
    except Exception as e: print(f"Error subplot RPM: {e}"); axs[3].text(0.5, 0.5, 'Error', ha='c', va='c', transform=axs[3].transAxes)
    try: # Marcha con ticks corregidos
        plot_subplot(axs[4], lap_data_full, ref_lap_data_full, gear_col, 'Marcha', 'Marcha', use_step=True)
        try: # Ajustar ticks Y Marcha (CORREGIDO)
            # Concatenar y obtener únicos directamente de las Series originales (más robusto a tipos mixtos)
            gear_series_lap = pd.to_numeric(lap_data_full[gear_col], errors='coerce')
            gear_series_ref = pd.to_numeric(ref_lap_data_full[gear_col], errors='coerce')
            combined_gears = pd.concat([gear_series_lap, gear_series_ref]).dropna()

            if not combined_gears.empty:
                # Obtener únicos y asegurar que sean enteros
                valid_int_gears = np.unique(combined_gears.astype(int))
                if valid_int_gears.size > 0:
                    min_g, max_g = valid_int_gears.min(), valid_int_gears.max()
                    if min_g <= max_g:
                         # Generar ticks enteros desde min a max gear encontrado
                         axs[4].set_yticks(np.arange(min_g, max_g + 1))
            # else: print("Adv Plotter: No hay marchas numéricas válidas para ticks.") # Silenciado
        except Exception as e_tick: print(f"Advertencia: No se pudo ajustar ticks Marcha: {e_tick}")
    except Exception as e: print(f"Error subplot Marcha: {e}"); axs[4].text(0.5, 0.5, 'Error', ha='c', va='c', transform=axs[4].transAxes)

    # --- Ajustes Finales Eje X ---
    axs[4].tick_params(axis='x', which='both', bottom=True, top=False, labelbottom=True)
    axs[4].set_xlabel('Distancia en Vuelta (m)', fontsize=10)
    xlim_to_set = None; track_length_m = None
    try: # Intentar obtener longitud de pista
        track_name_str = str(metadata.get('Track', '')); match = re.search(r'\(([\d.]+)\s*m\)', track_name_str)
        if match: track_length_m = float(match.group(1))
        elif isinstance(metadata.get('Track Length M'), (int, float)): track_length_m = metadata['Track Length M']
        if track_length_m and track_length_m > 0: xlim_to_set = (0, track_length_m)
    except: pass
    if xlim_to_set is None: # Fallback
        all_dist = pd.concat([lap_data_full[dist_col], ref_lap_data_full[dist_col]]).dropna()
        if not all_dist.empty:
             # Asegurar que min/max no sean NaN
             d_min, d_max = all_dist.min(), all_dist.max()
             if pd.notna(d_min) and pd.notna(d_max) and d_min < d_max: xlim_to_set = (d_min, d_max)
    if xlim_to_set: axs[4].set_xlim(xlim_to_set)
    else: print("Advertencia: No se pudo determinar límite X dashboard.")

    # --- Mostrar Figura ---
    plt.tight_layout(rect=[0, 0.03, 1, 0.96])
    print("Mostrando dashboard comparativo...")
    try: plt.show()
    except Exception as e_show: print(f"Error mostrando gráfico: {e_show}")
    print("Dashboard cerrado.")


def plot_live_comparison_replay(df_telemetry, metadata, lap_number, reference_lap_number, sample_points=800, interval_ms=32):
    """Dashboard dinamico de coach: circuito, pedales, volante, marchas y telemetria comparada."""
    lap_col, dist_col = 'Lap', 'LapDist'
    required_cols = [lap_col, dist_col, 'Speed', 'Throttle', 'Brake', 'Steer', 'RPM', 'Gear']
    missing_cols = [col for col in required_cols if col not in df_telemetry.columns]
    if missing_cols:
        print(f"Error Replay Dashboard: Faltan columnas: {missing_cols}")
        return
    if not (isinstance(lap_number, int) and isinstance(reference_lap_number, int) and lap_number != reference_lap_number):
        print("Error Replay Dashboard: Vueltas invalidas.")
        return

    lap_data = df_telemetry[df_telemetry[lap_col] == lap_number].copy().sort_values(dist_col)
    ref_data = df_telemetry[df_telemetry[lap_col] == reference_lap_number].copy().sort_values(dist_col)
    if lap_data.empty or ref_data.empty:
        print(f"Error Replay Dashboard: Datos insuficientes V{lap_number} o VRef{reference_lap_number}.")
        return

    def prepare_lap(data):
        data = data.dropna(subset=[dist_col]).copy()
        return data.drop_duplicates(subset=[dist_col], keep='first').sort_values(dist_col)

    def interp_series(data, col, distances):
        if col not in data.columns:
            return np.full_like(distances, np.nan, dtype=float)
        valid = data.dropna(subset=[dist_col, col])
        if valid.empty:
            return np.full_like(distances, np.nan, dtype=float)
        x = valid[dist_col].astype(float).to_numpy()
        y = pd.to_numeric(valid[col], errors='coerce').to_numpy(dtype=float)
        mask = np.isfinite(x) & np.isfinite(y)
        if mask.sum() < 2:
            return np.full_like(distances, y[mask][0] if mask.sum() == 1 else np.nan, dtype=float)
        return np.interp(distances, x[mask], y[mask])

    def metric_label(value, fmt="{:.1f}"):
        return fmt.format(value) if np.isfinite(value) else "-"

    lap_data = prepare_lap(lap_data)
    ref_data = prepare_lap(ref_data)
    min_dist = max(lap_data[dist_col].min(), ref_data[dist_col].min())
    max_dist = min(lap_data[dist_col].max(), ref_data[dist_col].max())
    if not np.isfinite(max_dist) or max_dist <= min_dist:
        print("Error Replay Dashboard: No se pudo determinar rango de distancia valido.")
        return

    distances = np.linspace(min_dist, max_dist, sample_points)
    channels = ['Speed', 'Throttle', 'Brake', 'Steer', 'RPM', 'Gear']
    lap = {col: interp_series(lap_data, col, distances) for col in channels}
    ref = {col: interp_series(ref_data, col, distances) for col in channels}
    has_map = all(col in df_telemetry.columns for col in ['Latitude', 'Longitude'])
    if has_map:
        lap['Latitude'] = interp_series(lap_data, 'Latitude', distances)
        lap['Longitude'] = interp_series(lap_data, 'Longitude', distances)
        ref['Latitude'] = interp_series(ref_data, 'Latitude', distances)
        ref['Longitude'] = interp_series(ref_data, 'Longitude', distances)
        has_map = all(np.isfinite(lap[col]).any() and np.isfinite(ref[col]).any() for col in ['Latitude', 'Longitude'])

    steer_abs = np.abs(np.concatenate([lap['Steer'], ref['Steer']]))
    steer_limit = max(90, min(540, float(np.nanmax(steer_abs)) * 1.1 if np.isfinite(steer_abs).any() else 180))
    turn_intensity = np.clip(np.abs(lap['Steer']) / steer_limit, 0, 1)

    print(f"\n--- Dashboard Dinamico Coach V{lap_number} vs Ref V{reference_lap_number} ---")
    print("Cierra la ventana del dashboard para volver al menu.")

    vehicle_info = metadata.get("Vehicle", "Vehiculo")
    track_info = metadata.get("Track", "Pista")
    lap_color = '#1f77b4'
    ref_color = '#d627b0'

    fig = plt.figure(figsize=(19, 10.5), facecolor='#f2f2f2')
    grid = fig.add_gridspec(5, 3, width_ratios=[1.05, 0.82, 1.65], hspace=0.35, wspace=0.24)
    ax_map = fig.add_subplot(grid[:, 0])
    ax_dash = fig.add_subplot(grid[:, 1])
    ax_brake = fig.add_subplot(grid[0, 2])
    ax_throttle = fig.add_subplot(grid[1, 2])
    ax_speed = fig.add_subplot(grid[2, 2])
    ax_steer = fig.add_subplot(grid[3, 2])
    ax_engine = fig.add_subplot(grid[4, 2])
    fig.suptitle(f"Driving Analyzer - V{lap_number} vs V{reference_lap_number} | {vehicle_info} @ {track_info}", fontsize=15, fontweight='bold')

    if has_map:
        ax_map.plot(lap['Longitude'], lap['Latitude'], color='0.75', lw=7, alpha=0.45, solid_capstyle='round')
        ax_map.plot(lap['Longitude'], lap['Latitude'], color='0.28', lw=1.2, alpha=0.75, label='Circuito')
        brake_idx = np.where(lap['Brake'] > 0.12)[0]
        throttle_idx = np.where(lap['Throttle'] > 0.85)[0]
        turn_idx = np.where(turn_intensity > 0.28)[0]
        ax_map.scatter(lap['Longitude'][throttle_idx], lap['Latitude'][throttle_idx], s=9, color='#21a65b', alpha=0.45, label='Gas V')
        ax_map.scatter(lap['Longitude'][brake_idx], lap['Latitude'][brake_idx], s=12, color='#d62728', alpha=0.55, label='Freno V')
        ax_map.scatter(lap['Longitude'][turn_idx], lap['Latitude'][turn_idx], s=8, color='#9467bd', alpha=0.35, label='Giro V')
        ax_map.plot(ref['Longitude'], ref['Latitude'], color=ref_color, alpha=0.35, lw=1.2, ls='--', label=f'Ref V{reference_lap_number}')
        lap_marker, = ax_map.plot([], [], 'o', color=lap_color, markersize=11, markeredgecolor='white', markeredgewidth=1.4)
        ref_marker, = ax_map.plot([], [], 'o', color=ref_color, markersize=9, markeredgecolor='white', markeredgewidth=1.2)
        turn_ray, = ax_map.plot([], [], color='#6f42c1', lw=2.0, alpha=0.85)
        ax_map.set_xlabel('Longitud')
        ax_map.set_ylabel('Latitud')
        ax_map.axis('equal')
    else:
        ax_map.plot(distances, np.zeros_like(distances), color='0.7', lw=5)
        lap_marker, = ax_map.plot([], [], 'o', color=lap_color, markersize=11)
        ref_marker, = ax_map.plot([], [], 'o', color=ref_color, markersize=9)
        turn_ray, = ax_map.plot([], [], color='#6f42c1', lw=2.0)
        ax_map.set_yticks([])
        ax_map.set_xlabel('Distancia (m)')
    ax_map.set_title('Circuito: verde gas | rojo freno | violeta giro', loc='left', fontsize=11, fontweight='bold')
    ax_map.grid(True, linestyle=':', alpha=0.35)
    ax_map.legend(loc='best', fontsize=8)
    info_text = ax_map.text(0.02, 0.98, '', transform=ax_map.transAxes, va='top', ha='left',
                            bbox=dict(facecolor='white', alpha=0.88, edgecolor='0.75'))

    ax_dash.set_title('Cockpit Coach', loc='left', fontsize=11, fontweight='bold')
    ax_dash.set_xlim(0, 1)
    ax_dash.set_ylim(0, 1)
    ax_dash.axis('off')
    ax_dash.add_patch(patches.FancyBboxPatch((0.03, 0.03), 0.94, 0.93, boxstyle="round,pad=0.015",
                                             facecolor='white', edgecolor='0.82', alpha=0.96))
    values_text = ax_dash.text(0.08, 0.93, '', va='top', ha='left', fontsize=8.2,
                               bbox=dict(facecolor='#f7f9fb', alpha=0.95, edgecolor='0.82'))

    wheel_ax = ax_dash.inset_axes([0.285, 0.465, 0.43, 0.32])
    wheel_ax.set_xlim(-1, 1)
    wheel_ax.set_ylim(-1, 1)
    wheel_ax.set_aspect('equal', adjustable='box')
    wheel_ax.axis('off')
    wheel_radius = 0.82
    wheel_ax.add_patch(patches.Circle((0, 0), wheel_radius + 0.035, fill=False, lw=2, edgecolor='0.60', alpha=0.35))
    wheel_ax.add_patch(patches.Circle((0, 0), wheel_radius, fill=False, lw=10, edgecolor='0.13'))
    wheel_ax.add_patch(patches.Circle((0, 0), 0.15, fill=True, facecolor='0.18', edgecolor='0.35', lw=1.5))
    wheel_line, = wheel_ax.plot([], [], color=lap_color, lw=4.2, solid_capstyle='round')
    wheel_ref_line, = wheel_ax.plot([], [], color=ref_color, lw=2.4, alpha=0.82, solid_capstyle='round')
    ax_dash.text(0.50, 0.435, 'STEERING', ha='center', fontsize=8, color='0.25', fontweight='bold')
    steering_value_text = ax_dash.text(0.50, 0.405, '', ha='center', fontsize=12, color=lap_color, fontweight='bold')

    pedal_base_y = 0.135
    pedal_height = 0.205
    pedal_width = 0.060
    pedal_specs = [
        ('CLUTCH', 0.100, '0.70', '0.90'),
        ('BRAKE', 0.220, '#d62728', '#f2b1b1'),
        ('GAS', 0.340, '#21a65b', '#b8e3c8'),
    ]
    pedal_bars = {}
    pedal_ref_bars = {}
    pedal_value_texts = {}
    for label, x, color, ref_fill in pedal_specs:
        ax_dash.text(x + pedal_width / 2, pedal_base_y + pedal_height + 0.025, label, ha='center', fontsize=7.3,
                     color=color if label != 'CLUTCH' else '0.35', fontweight='bold')
        ax_dash.add_patch(patches.Rectangle((x, pedal_base_y), pedal_width, pedal_height,
                                            facecolor='0.88', edgecolor='0.65', lw=1))
        ref_bar = patches.Rectangle((x + pedal_width + 0.012, pedal_base_y), 0.020, 0.0,
                                    facecolor=ref_fill, edgecolor='none', alpha=0.95)
        main_bar = patches.Rectangle((x, pedal_base_y), pedal_width, 0.0,
                                     facecolor=color, edgecolor='none', alpha=0.88)
        ax_dash.add_patch(ref_bar)
        ax_dash.add_patch(main_bar)
        pedal_ref_bars[label] = ref_bar
        pedal_bars[label] = main_bar
        pedal_value_texts[label] = ax_dash.text(x + pedal_width / 2, pedal_base_y - 0.030, '', ha='center',
                                                fontsize=7.2, color='0.25')

    ax_dash.text(0.695, 0.355, 'GEAR', ha='center', fontsize=8, color='0.25', fontweight='bold')
    ax_dash.text(0.835, 0.355, 'REF', ha='center', fontsize=8, color='0.45', fontweight='bold')
    gear_box = patches.FancyBboxPatch((0.625, 0.165), 0.135, 0.155, boxstyle="round,pad=0.01",
                                      facecolor='#eef5ff', edgecolor=lap_color, lw=1.5)
    gear_ref_box = patches.FancyBboxPatch((0.795, 0.185), 0.100, 0.115, boxstyle="round,pad=0.01",
                                          facecolor='#fff2fb', edgecolor=ref_color, lw=1.2)
    ax_dash.add_patch(gear_box)
    ax_dash.add_patch(gear_ref_box)
    gear_text = ax_dash.text(0.692, 0.240, '', ha='center', va='center', fontsize=40, color=lap_color, fontweight='bold')
    gear_ref_text = ax_dash.text(0.845, 0.240, '', ha='center', va='center', fontsize=28, color=ref_color, fontweight='bold')
    coach_text = ax_dash.text(0.08, 0.052, '', va='bottom', ha='left', fontsize=7.9,
                              bbox=dict(facecolor='#fff8cc', alpha=0.96, edgecolor='#d4b106'))

    def setup_axis(ax, title, ylabel, ylim=None):
        ax.set_title(title, loc='left', fontsize=10, fontweight='bold')
        ax.set_ylabel(ylabel)
        ax.grid(True, linestyle=':', alpha=0.45)
        ax.set_xlim(min_dist, max_dist)
        if ylim:
            ax.set_ylim(*ylim)

    setup_axis(ax_brake, 'Brake %', '%', (-5, 105))
    setup_axis(ax_throttle, 'Throttle %', '%', (-5, 105))
    setup_axis(ax_speed, 'Speed', 'km/h')
    setup_axis(ax_steer, 'Steering angle', 'deg', (-steer_limit, steer_limit))
    setup_axis(ax_engine, 'RPM / Gear', 'RPM')
    ax_engine.set_xlabel('Distancia de vuelta (m)')
    ax_gear = ax_engine.twinx()
    ax_gear.set_ylabel('Marcha')

    ax_brake.plot(distances, lap['Brake'] * 100, color=lap_color, lw=1.5, label=f'V{lap_number}')
    ax_brake.plot(distances, ref['Brake'] * 100, color=ref_color, lw=1.2, ls='--', label=f'Ref V{reference_lap_number}')
    ax_throttle.plot(distances, lap['Throttle'] * 100, color=lap_color, lw=1.5, label=f'V{lap_number}')
    ax_throttle.plot(distances, ref['Throttle'] * 100, color=ref_color, lw=1.2, ls='--', label=f'Ref V{reference_lap_number}')
    ax_speed.plot(distances, lap['Speed'], color=lap_color, lw=1.5, label=f'V{lap_number}')
    ax_speed.plot(distances, ref['Speed'], color=ref_color, lw=1.2, ls='--', label=f'Ref V{reference_lap_number}')
    ax_steer.plot(distances, lap['Steer'], color=lap_color, lw=1.4, label=f'V{lap_number}')
    ax_steer.plot(distances, ref['Steer'], color=ref_color, lw=1.1, ls='--', label=f'Ref V{reference_lap_number}')
    ax_engine.plot(distances, lap['RPM'], color=lap_color, lw=1.3, label='RPM V')
    ax_engine.plot(distances, ref['RPM'], color=ref_color, lw=1.0, ls='--', label='RPM Ref')
    ax_gear.step(distances, lap['Gear'], color='#111111', where='post', lw=1.2, label='Gear V')
    ax_gear.step(distances, ref['Gear'], color='0.45', where='post', lw=1.0, ls='--', label='Gear Ref')
    for ax in [ax_brake, ax_throttle, ax_speed, ax_steer]:
        ax.legend(loc='upper right', fontsize=8, ncol=2)
    engine_lines, engine_labels = ax_engine.get_legend_handles_labels()
    gear_lines, gear_labels = ax_gear.get_legend_handles_labels()
    ax_gear.legend(engine_lines + gear_lines, engine_labels + gear_labels, loc='upper right', fontsize=8, ncol=2)

    cursor_lines = [ax.axvline(min_dist, color='black', lw=1, alpha=0.75) for ax in [ax_brake, ax_throttle, ax_speed, ax_steer, ax_engine]]
    metric_boxes = {
        'brake': ax_brake.text(0.01, 0.88, '', transform=ax_brake.transAxes, fontsize=8, bbox=dict(facecolor='white', alpha=0.8, edgecolor='0.8')),
        'throttle': ax_throttle.text(0.01, 0.88, '', transform=ax_throttle.transAxes, fontsize=8, bbox=dict(facecolor='white', alpha=0.8, edgecolor='0.8')),
        'speed': ax_speed.text(0.01, 0.88, '', transform=ax_speed.transAxes, fontsize=8, bbox=dict(facecolor='white', alpha=0.8, edgecolor='0.8')),
        'steer': ax_steer.text(0.01, 0.88, '', transform=ax_steer.transAxes, fontsize=8, bbox=dict(facecolor='white', alpha=0.8, edgecolor='0.8')),
    }

    playback_state = {'paused': False, 'frame': 0}

    def render_frame(frame):
        frame = int(np.clip(frame, 0, len(distances) - 1))
        playback_state['frame'] = frame
        d = distances[frame]
        for line in cursor_lines:
            line.set_xdata([d, d])
        if has_map:
            lx, ly = lap['Longitude'][frame], lap['Latitude'][frame]
            rx, ry = ref['Longitude'][frame], ref['Latitude'][frame]
            lap_marker.set_data([lx], [ly])
            ref_marker.set_data([rx], [ry])
            steer_norm = np.clip(lap['Steer'][frame] / steer_limit, -1, 1) if np.isfinite(lap['Steer'][frame]) else 0
            scale_x = (np.nanmax(lap['Longitude']) - np.nanmin(lap['Longitude'])) * 0.04
            scale_y = (np.nanmax(lap['Latitude']) - np.nanmin(lap['Latitude'])) * 0.04
            turn_ray.set_data([lx, lx + steer_norm * scale_x], [ly, ly + abs(steer_norm) * scale_y])
        else:
            lap_marker.set_data([d], [0])
            ref_marker.set_data([d], [0])
            turn_ray.set_data([d, d], [0, 0])

        steer_angle = lap['Steer'][frame] if np.isfinite(lap['Steer'][frame]) else 0
        ref_steer_angle = ref['Steer'][frame] if np.isfinite(ref['Steer'][frame]) else 0
        wheel_angle = np.deg2rad(np.clip(steer_angle, -180, 180))
        ref_wheel_angle = np.deg2rad(np.clip(ref_steer_angle, -180, 180))
        wheel_line.set_data(
            [-np.cos(wheel_angle) * wheel_radius * 0.70, np.cos(wheel_angle) * wheel_radius * 0.70],
            [-np.sin(wheel_angle) * wheel_radius * 0.70, np.sin(wheel_angle) * wheel_radius * 0.70]
        )
        wheel_ref_line.set_data(
            [-np.cos(ref_wheel_angle) * wheel_radius * 0.58, np.cos(ref_wheel_angle) * wheel_radius * 0.58],
            [-np.sin(ref_wheel_angle) * wheel_radius * 0.58, np.sin(ref_wheel_angle) * wheel_radius * 0.58]
        )
        steering_value_text.set_text(f"{steer_angle:+.1f} deg | ref {ref_steer_angle:+.1f}")

        brake_value = float(np.clip(lap['Brake'][frame], 0, 1))
        throttle_value = float(np.clip(lap['Throttle'][frame], 0, 1))
        ref_brake_value = float(np.clip(ref['Brake'][frame], 0, 1))
        ref_throttle_value = float(np.clip(ref['Throttle'][frame], 0, 1))
        pedal_bars['CLUTCH'].set_height(0.0)
        pedal_ref_bars['CLUTCH'].set_height(0.0)
        pedal_bars['BRAKE'].set_height(brake_value * pedal_height)
        pedal_ref_bars['BRAKE'].set_height(ref_brake_value * pedal_height)
        pedal_bars['GAS'].set_height(throttle_value * pedal_height)
        pedal_ref_bars['GAS'].set_height(ref_throttle_value * pedal_height)
        pedal_value_texts['CLUTCH'].set_text("0%")
        pedal_value_texts['BRAKE'].set_text(f"{brake_value * 100:.0f}%")
        pedal_value_texts['GAS'].set_text(f"{throttle_value * 100:.0f}%")

        gear_text.set_text(str(int(round(lap['Gear'][frame]))) if np.isfinite(lap['Gear'][frame]) else '-')
        gear_ref_text.set_text(str(int(round(ref['Gear'][frame]))) if np.isfinite(ref['Gear'][frame]) else '-')
        speed_delta = lap['Speed'][frame] - ref['Speed'][frame]
        brake_delta = (lap['Brake'][frame] - ref['Brake'][frame]) * 100
        throttle_delta = (lap['Throttle'][frame] - ref['Throttle'][frame]) * 100
        steer_delta = lap['Steer'][frame] - ref['Steer'][frame]
        info_text.set_text(
            f"Distancia: {d:7.1f} m\n"
            f"Velocidad V{lap_number}: {metric_label(lap['Speed'][frame])} km/h\n"
            f"Velocidad Ref: {metric_label(ref['Speed'][frame])} km/h\n"
            f"Delta velocidad: {speed_delta:+.1f} km/h"
        )
        values_text.set_text(
            f"V{lap_number} vs Ref V{reference_lap_number}\n"
            f"Speed {metric_label(lap['Speed'][frame])}/{metric_label(ref['Speed'][frame])} km/h\n"
            f"Brake {lap['Brake'][frame]*100:4.0f}/{ref['Brake'][frame]*100:4.0f}%\n"
            f"Gas   {lap['Throttle'][frame]*100:4.0f}/{ref['Throttle'][frame]*100:4.0f}%\n"
            f"RPM   {lap['RPM'][frame]:5.0f}/{ref['RPM'][frame]:5.0f}"
        )
        coach_text.set_text(
            "Coach focus:\n"
            f"Brake delta {brake_delta:+.1f}%\n"
            f"Gas delta {throttle_delta:+.1f}%\n"
            f"Steer delta {steer_delta:+.1f} deg\n"
            "Mapa: rojo freno, verde gas,\n"
            "violeta radio/giro."
        )
        metric_boxes['brake'].set_text(f"Delta brake: {brake_delta:+.1f}%")
        metric_boxes['throttle'].set_text(f"Delta gas: {throttle_delta:+.1f}%")
        metric_boxes['speed'].set_text(f"Delta speed: {speed_delta:+.1f} km/h")
        metric_boxes['steer'].set_text(f"Delta steering: {steer_delta:+.1f} deg")
        state_text = "PAUSA" if playback_state['paused'] else "PLAY"
        fig.suptitle(
            f"Driving Analyzer - {state_text} - V{lap_number} vs V{reference_lap_number} | "
            f"{vehicle_info} @ {track_info} | Space pausa/reanuda | Flechas paso a paso",
            fontsize=15,
            fontweight='bold'
        )
        return [lap_marker, ref_marker, turn_ray, info_text, wheel_line, wheel_ref_line, steering_value_text,
                *pedal_bars.values(), *pedal_ref_bars.values(),
                *pedal_value_texts.values(), gear_text, gear_ref_text, values_text, coach_text,
                *cursor_lines, *metric_boxes.values()]

    def update(frame):
        if playback_state['paused']:
            return render_frame(playback_state['frame'])
        return render_frame(frame)

    def on_key_press(event):
        key = (event.key or '').lower()
        if key == ' ':
            playback_state['paused'] = not playback_state['paused']
        elif key in ['right', 'd']:
            playback_state['paused'] = True
            playback_state['frame'] = min(playback_state['frame'] + 5, len(distances) - 1)
        elif key in ['left', 'a']:
            playback_state['paused'] = True
            playback_state['frame'] = max(playback_state['frame'] - 5, 0)
        elif key in ['up', 'w']:
            playback_state['paused'] = True
            playback_state['frame'] = min(playback_state['frame'] + 25, len(distances) - 1)
        elif key in ['down', 's']:
            playback_state['paused'] = True
            playback_state['frame'] = max(playback_state['frame'] - 25, 0)
        elif key == 'home':
            playback_state['paused'] = True
            playback_state['frame'] = 0
        elif key == 'end':
            playback_state['paused'] = True
            playback_state['frame'] = len(distances) - 1
        render_frame(playback_state['frame'])
        fig.canvas.draw_idle()

    fig.canvas.mpl_connect('key_press_event', on_key_press)
    anim = FuncAnimation(fig, update, frames=len(distances), interval=interval_ms, blit=False, repeat=True)
    fig._replay_animation = anim
    fig.subplots_adjust(left=0.04, right=0.98, top=0.91, bottom=0.06)
    print("Mostrando dashboard dinamico de coach...")
    try:
        plt.show()
    except Exception as e_show:
        print(f"Error mostrando replay dashboard: {e_show}")
    print("Dashboard dinamico cerrado.")


# --- Función plot_delta_analysis_dashboard (OBSOLETA - Mantenida comentada) ---
# def plot_delta_analysis_dashboard(df_telemetry, metadata, lap_number, reference_lap_number):
#     ...
#     pass
