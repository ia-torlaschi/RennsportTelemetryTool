# plotter.py (vFinal Definitiva - Corrección Indentación + Ticks Marcha)

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker # Para formatear ejes Y
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


# --- Función plot_delta_analysis_dashboard (OBSOLETA - Mantenida comentada) ---
# def plot_delta_analysis_dashboard(df_telemetry, metadata, lap_number, reference_lap_number):
#     ...
#     pass