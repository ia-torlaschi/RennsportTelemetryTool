# main.py (v9 - Llama a plot_comparison_dashboard y actualiza menú)
import pandas as pd
import numpy as np
import os
import sys
import traceback

# Importar funciones
try:
    from data_loader import load_telemetry_csv
    # Importar funciones individuales Y la nueva función de dashboard
    from plotter import plot_lap_speed_profile, plot_lap_inputs, plot_lap_engine, plot_comparison_dashboard # Nombre nuevo/modificado
except ImportError as e:
    print(f"Error: No se pudieron importar módulos o funciones necesarias.")
    print(f"Detalle del error: {e}")
    sys.exit(1)

# --- Funciones Auxiliares ---
def format_time(seconds):
    """Formatea segundos en MM:SS.ms"""
    if pd.isna(seconds) or not np.isfinite(seconds) or seconds < 0: return "N/A"
    if isinstance(seconds, np.timedelta64): seconds = seconds.total_seconds()
    elif not isinstance(seconds, (int, float, np.number)): return "Invalid Type"
    minutes = int(seconds // 60); secs = int(seconds % 60)
    millis = int(round((seconds - minutes * 60 - secs) * 1000))
    if millis >= 1000: secs += 1; millis -= 1000
    if secs >= 60: minutes +=1; secs -= 60
    return f"{minutes:02d}:{secs:02d}.{millis:03d}"

# --- Lógica de Cálculo de Vueltas ---
def calculate_laps_improved(df, min_lap_time_threshold=60):
    """Calcula tiempos de vuelta basado en fin vuelta anterior."""
    required_cols = ['Time', 'Lap', 'IsLapValid']
    if not all(col in df.columns for col in required_cols): raise ValueError(f"Faltan cols: {[c for c in required_cols if c not in df.columns]}")
    df = df.sort_values('Time').reset_index(drop=True)
    if 'IsLapValid' not in df.columns: print("Adv: 'IsLapValid' no encontrada."); df['IsLapValid'] = True
    elif df['IsLapValid'].dtype != bool:
         try:
            valid_map = {'True': True, 'False': False, '1': True, '0': False, 1: True, 0: False, 1.0: True, 0.0: False, True: True, False: False}
            original_type = df['IsLapValid'].dtype; df['IsLapValid'] = df['IsLapValid'].map(valid_map).fillna(False).astype(bool)
            if not pd.api.types.is_bool_dtype(original_type): print("'IsLapValid' convertida a bool.")
         except Exception as e: print(f"Adv: conversión 'IsLapValid': {e}"); df['IsLapValid'] = df['IsLapValid'].apply(lambda x: str(x).lower() in ['true', '1', '1.0'])
    lap_change_indices = df[df['Lap'] != df['Lap'].shift(1)].index
    cut_indices = pd.Index([0]).union(lap_change_indices - 1).union(pd.Index([len(df) - 1])).unique().sort_values()
    cut_indices = cut_indices[cut_indices >= 0]
    if len(cut_indices) < 3: print("Adv: No suficientes cambios de vuelta."); return pd.DataFrame()
    lap_data = []
    for i in range(len(cut_indices) - 1):
        start_idx = cut_indices[i] + 1 if i > 0 else 0; end_idx = cut_indices[i+1]
        if start_idx >= len(df) or end_idx < start_idx: continue
        lap_num = int(df.loc[start_idx, 'Lap'])
        start_time = df.loc[start_idx, 'Time']; end_time = df.loc[end_idx, 'Time']
        lap_time_secs = df.loc[cut_indices[i+1], 'Time'] - df.loc[cut_indices[i], 'Time'] if i < len(cut_indices)-1 else np.nan
        lap_type = 'Timed Lap'; is_complete = True
        if i == 0: lap_type = 'Out Lap'; is_complete = False; lap_time_secs = end_time - df.loc[0, 'Time']
        if i == len(cut_indices) - 2: lap_type = 'In Lap'; is_complete = False; lap_time_secs = df.loc[len(df)-1, 'Time'] - start_time
        is_valid_source = df.loc[start_idx:end_idx, 'IsLapValid'].all()
        is_valid_time_threshold = (lap_time_secs >= min_lap_time_threshold) if pd.notna(lap_time_secs) else False
        is_time_valid = False; current_lap_time_calc = np.nan
        if i < len(cut_indices) - 2: current_lap_time_calc = df.loc[cut_indices[i+1], 'Time'] - df.loc[cut_indices[i], 'Time']
        if lap_type == 'Timed Lap':
             is_time_valid = is_valid_source and pd.notna(current_lap_time_calc) and current_lap_time_calc >= min_lap_time_threshold
             lap_time_secs = current_lap_time_calc
        elif lap_type == 'In Lap': is_time_valid = False; lap_time_secs = df.loc[len(df)-1, 'Time'] - df.loc[cut_indices[i], 'Time'] # Usar start_time del In Lap
        elif lap_type == 'Out Lap': is_time_valid = False; lap_time_secs = df.loc[cut_indices[i+1], 'Time'] - df.loc[0, 'Time']
        if not is_complete and lap_type not in ['Out Lap', 'In Lap']: lap_time_secs = np.nan
        lap_data.append({'Lap': lap_num, 'LapType': lap_type, 'StartTime': start_time, 'EndTime': end_time,
                         'LapTime': lap_time_secs, 'FormattedTime': format_time(lap_time_secs),
                         'IsLapValidSource': is_valid_source, 'IsTimeValid': is_time_valid, 'IsComplete': is_complete})
    laps_df = pd.DataFrame(lap_data)
    laps_df = laps_df[['Lap', 'LapType', 'StartTime', 'EndTime', 'LapTime', 'FormattedTime', 'IsLapValidSource', 'IsTimeValid', 'IsComplete']]
    if len(laps_df) > 1:
         last_full_lap_idx = -2 if laps_df.iloc[-1]['LapType'] == 'In Lap' else -1
         if last_full_lap_idx < 0 and laps_df.iloc[last_full_lap_idx]['LapType'] == 'Timed Lap':
              laps_df.loc[laps_df.index[last_full_lap_idx], 'IsComplete'] = True
    return laps_df

# --- Función Principal ---
def main():
    print("--- Iniciando RennsportTelemetryTool ---")
    while True:
        file_path = input("\nArchivo CSV Telemetry.csv (o vacío para salir): ").strip()
        if not file_path: print("Saliendo..."); break
        if not os.path.exists(file_path): print(f"Error: '{file_path}' no existe."); continue
        if not file_path.lower().endswith('.csv'): print(f"Error: '{os.path.basename(file_path)}' no es CSV."); continue
        print(f"Archivo: {file_path}")
        # Carga
        df_cleaned = None; metadata = {}
        try:
            print(f"Cargando: {os.path.basename(file_path)}..."); df_cleaned, metadata = load_telemetry_csv(file_path)
            if df_cleaned is None or df_cleaned.empty: print("Error carga."); continue
            print(f"Carga OK. DF: {df_cleaned.shape[0]}x{df_cleaned.shape[1]}.")
            if metadata: print("--- Metadatos ---"); [print(f"- {k}: {v}") for k, v in metadata.items()]
            else: print("No metadatos.")
        except Exception as e: print(f"Error carga: {e}"); traceback.print_exc(); continue
        # Cálculo Vueltas
        laps_info_df = pd.DataFrame(); best_lap_row = None; slowest_lap_row = None; available_laps_for_analysis = []
        print("\n--- Calculando Tiempos (v4) ---")
        try:
            track_length_m = metadata.get('Track Length M', None)
            if track_length_m and isinstance(track_length_m, (int, float)) and track_length_m > 0:
                 min_lap_time = max(30, (track_length_m/(41.6*0.7))); print(f"(Umbral: >{min_lap_time:.1f}s)")
            else: min_lap_time = 60; print(f"(Umbral fijo: >{min_lap_time}s)")
            laps_info_df = calculate_laps_improved(df_cleaned, min_lap_time_threshold=min_lap_time)
            if not laps_info_df.empty:
                print("Tiempos calculados:")
                laps_display_df = laps_info_df[['Lap','LapType','LapTime','FormattedTime','IsTimeValid']].copy()
                laps_display_df['LapTime'] = laps_display_df['LapTime'].round(3)
                laps_display_df.rename(columns={'LapTime':'T (s)','FormattedTime':'T Fmt','IsTimeValid':'Valida'}, inplace=True)
                print(laps_display_df[laps_display_df['T Fmt'] != "N/A"].to_string(index=False))
                valid_timed = laps_info_df[(laps_info_df['IsTimeValid']) & (laps_info_df['LapType']=='Timed Lap')]
                if not valid_timed.empty:
                    best_lap_row = valid_timed.loc[valid_timed['LapTime'].idxmin()]
                    slowest_lap_row = valid_timed.loc[valid_timed['LapTime'].idxmax()]
                    median_time = valid_timed['LapTime'].median()
                    print(f"\nMejor: V{int(best_lap_row['Lap'])} ({best_lap_row['FormattedTime']})")
                    print(f"Peor: V{int(slowest_lap_row['Lap'])} ({slowest_lap_row['FormattedTime']})")
                    print(f"Mediana: {format_time(median_time)}")
                else: print("\nNo vueltas válidas.")
                available_laps_for_analysis = sorted(laps_info_df['Lap'].unique().astype(int).tolist())
                print(f"Vueltas: {available_laps_for_analysis}")
            else: print("No se calculó info vueltas.")
        except Exception as e: print(f"Error cálculo: {e}"); traceback.print_exc()

        # Selección y Análisis
        if not available_laps_for_analysis: print("\nNo vueltas disponibles."); continue
        while True: # Bucle selección vuelta
            lap_prompt = "\n¿Vuelta a analizar?"; lap_details = [];
            if best_lap_row is not None: lap_details.append(f"Mejor V{int(best_lap_row['Lap'])}: {best_lap_row['FormattedTime']}")
            if slowest_lap_row is not None: lap_details.append(f"Peor V{int(slowest_lap_row['Lap'])}: {slowest_lap_row['FormattedTime']}")
            if lap_details: lap_prompt += f" ({'; '.join(lap_details)})"
            lap_prompt += f"\n(Vueltas: {available_laps_for_analysis}. Num o 'Q'): "
            lap_choice = input(lap_prompt).strip().upper()
            if lap_choice == 'Q': break
            try:
                selected_lap_num = int(lap_choice)
                if selected_lap_num not in available_laps_for_analysis: print("Error: Vuelta no disponible."); continue
                print(f"\n--- Analizando V{selected_lap_num} ---")
                lap_info = laps_info_df[laps_info_df['Lap'] == selected_lap_num].iloc[0]
                df_lap = df_cleaned[(df_cleaned['Time']>=lap_info['StartTime']) & (df_cleaned['Time']<=lap_info['EndTime'])].copy()
                if df_lap.empty: print(f"Error: No data V{selected_lap_num}."); continue

                # Menú Informes
                while True:
                    print("\n--- Menú Informes ---")
                    print("1: Velocidad"); print("2: Entradas Piloto"); print("3: Motor (RPM/Marcha)")
                    # Texto Menú Actualizado
                    print("4: Dashboard Comparativo (Vel, Thr, Brk, RPM, Gear)")
                    print("5: TODOS individuales (1, 2, 3)"); print("Q: Volver")
                    report_choice = input("Opción: ").strip().upper()
                    if report_choice == 'Q': break
                    try:
                        if report_choice == '1': plot_lap_speed_profile(df_lap, metadata, selected_lap_num)
                        elif report_choice == '2': plot_lap_inputs(df_lap, metadata, selected_lap_num)
                        elif report_choice == '3': plot_lap_engine(df_lap, metadata, selected_lap_num)
                        elif report_choice == '4':
                            print("--- Dashboard Comparativo ---")
                            valid_ref = laps_info_df[(laps_info_df['IsTimeValid']) & (laps_info_df['LapType']=='Timed Lap') & (laps_info_df['Lap']!=selected_lap_num)]
                            if valid_ref.empty: print("No refs disponibles."); continue
                            avail_ref = sorted(valid_ref['Lap'].astype(int).tolist())
                            ref_prompt = f"Ref para V{selected_lap_num}? (Disp: {avail_ref}, Mejor: V{int(best_lap_row['Lap']) if best_lap_row is not None else 'N/A'}. 'C' cancelar): "
                            ref_choice = input(ref_prompt).strip().upper()
                            if ref_choice == 'C': continue
                            try:
                                ref_lap_num = int(ref_choice)
                                if ref_lap_num not in avail_ref: print("Error: Ref inválida."); continue
                                print(f"Generando: Dashboard (V{selected_lap_num} vs Ref V{ref_lap_num})...")
                                # --- LLAMADA CORREGIDA ---
                                plot_comparison_dashboard(df_cleaned, metadata, selected_lap_num, ref_lap_num)
                                print("Dashboard generado.")
                            except ValueError: print("Error: Entrada inválida.")
                            except Exception as e_d: print(f"Error dash: {e_d}"); traceback.print_exc()
                        elif report_choice == '5':
                            print("Generando TODOS individuales...");
                            try: plot_lap_speed_profile(df_lap, metadata, selected_lap_num)
                            except Exception as e1: print(f"Err plot 1: {e1}")
                            try: plot_lap_inputs(df_lap, metadata, selected_lap_num)
                            except Exception as e2: print(f"Err plot 2: {e2}")
                            try: plot_lap_engine(df_lap, metadata, selected_lap_num)
                            except Exception as e3: print(f"Err plot 3: {e3}")
                            print("Plots individuales generados.")
                        else: print("Opción inválida.")
                    except NameError as ne: print(f"Err plotter.py: {ne}"); traceback.print_exc()
                    except Exception as e_p: print(f"Err informe: {e_p}"); traceback.print_exc()
            except ValueError: print("Error: Entrada inválida.")
            except Exception as e: print(f"Error análisis: {e}"); traceback.print_exc()
        print("\nVolviendo a selección archivo...")
if __name__ == "__main__":
    main()