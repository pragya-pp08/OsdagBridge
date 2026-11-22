# =============================================================================
# Chapter 3: Loads and Load Combinations
# Refactored for OsdagBridge Report Generator
#   - Distinct Vehicle Live Load and Footway Live Load tables with unit columns
#   - Repeated table headers across page breaks using styles.py LongTable engine
# =============================================================================

from osdagbridge.core.utils.common import (
    KEY_CB_LOAD,
    KEY_FOOTPATH,
    KEY_LL_CUSTOM_VEHICLES,
    KEY_LL_FOOTPATH_PRESSURE_MODE,
    KEY_LL_FOOTPATH_PRESSURE_VALUE,
    KEY_LL_IRC_70R_BOGIE,
    KEY_LL_IRC_70R_TRACKED,
    KEY_LL_IRC_70R_WHEELED,
    KEY_LL_IRC_AA_TRACKED,
    KEY_LL_IRC_AA_WHEELED,
    KEY_LL_IRC_CLASS_A,
    KEY_LL_IRC_CLASS_FATIGUE,
    KEY_LL_IRC_CLASS_SV,
    KEY_MATERIAL_DECK_DENSITY,
    KEY_MATERIAL_GIRDER_DENSITY,
    KEY_PL_SELF_WEIGHT_FACTOR,
    KEY_RL_LOAD_VALUE,
    KEY_SAFETY_KERB_PRESENT,
    KEY_SL_DAMPING,
    KEY_SL_DEAD_LOAD_MODE,
    KEY_SL_DEAD_LOAD_VALUE,
    KEY_SL_HORIZONTAL_COEFF,
    KEY_SL_IMPORTANCE_FACTOR,
    KEY_SL_LIVE_LOAD_MODE,
    KEY_SL_LIVE_LOAD_VALUE,
    KEY_SL_SEISMIC_ZONE,
    KEY_SL_SOIL_TYPE,
    KEY_SL_SPECTRAL_COEFF,
    KEY_SL_TIME_PERIOD,
    KEY_SL_VERTICAL_COEFF,
    KEY_SL_ZONE_FACTOR,
    KEY_SPAN,
    KEY_TS_NO_OF_FOOTPATHS,
    KEY_TL_BRIDGE_TEMP_MAX,
    KEY_TL_BRIDGE_TEMP_MIN,
    KEY_TL_HIGHEST_MAX_TEMP,
    KEY_TL_LOWEST_MIN_TEMP,
    KEY_TL_TEMP_FALL,
    KEY_TL_TEMP_RISE,
    KEY_WC_LD_LANE_TABLE_COUNT,
    KEY_WC_MATERIAL,
    KEY_WC_THICKNESS,
    KEY_WL_AVG_EXPOSED_HEIGHT,
    KEY_WL_BASIC_WIND_SPEED,
    KEY_WL_HOURLY_MEAN_WIND,
    KEY_WL_HOURLY_WIND_PRESSURE,
    KEY_WL_LONGITUDINAL_WIND_FORCE,
    KEY_WL_TERRAIN_TYPE,
    KEY_WL_TRANSVERSE_WIND_FORCE,
    KEY_WL_VERTICAL_WIND_FORCE
)

from osdagbridge.core.reports.report_utils import _tex, _render_value
from .styles import build_longtable_header


def ch3_loads(input_dict):
    from osdagbridge.core.utils.codes.irc6_2017 import IRC6_2017

    span = input_dict.get(KEY_SPAN)
    span_m = 0.0
    if span not in (None, ""):
        try:
            span_m = float(span)
        except Exception:
            span_m = 0.0

    lanes = input_dict.get(KEY_WC_LD_LANE_TABLE_COUNT)
    lanes_int = None
    if lanes not in (None, ""):
        try:
            lanes_int = int(lanes)
        except Exception:
            lanes_int = None

    if lanes_int is None:
        # Check carriageway width per IRC 6:2017 Table 6 (Cl. 207.1)
        cw = input_dict.get("typical_section.carriageway_width") or input_dict.get("carriageway_width")
        if cw not in (None, ""):
            try:
                cw_val = float(cw)
                if cw_val < 5.3:
                    lanes_int = 1
                elif cw_val < 9.6:
                    lanes_int = 2
                elif cw_val < 13.1:
                    lanes_int = 3
                elif cw_val < 16.6:
                    lanes_int = 4
                else:
                    lanes_int = max(2, int((cw_val - 7.5) / 3.5) + 2)
            except Exception:
                lanes_int = None

    # Calculate global braking force per IRC 6 Cl. 211 (honest calculation or N/A)
    braking_force_str = "N/A"
    if lanes_int is not None:
        try:
            braking_force_t = IRC6_2017.cl_211_2_braking_force(lanes_int)
            braking_force_kN = braking_force_t * 9.81
            braking_force_str = f"{braking_force_kN:.2f}"
        except Exception:
            braking_force_str = "N/A"

    # Centrifugal force per IRC 6:2017 Cl. 212
    # Applicable only on horizontal curves; straight alignments have zero centrifugal force.
    radius_val = input_dict.get("geometry.radius_of_curvature") or input_dict.get("radius_of_curvature")
    if radius_val not in (None, "", "0", 0):
        try:
            centrifugal_str = f"{float(radius_val):.1f}m curve"
        except Exception:
            centrifugal_str = "N/A"
    else:
        centrifugal_str = "0.00 (Straight)"

    # -------------------------------------------------------------------------
    # 1. Build distinct Vehicle Live Load records
    # -------------------------------------------------------------------------
    vehicle_rows = []
    
    # Check each standard vehicle from UI input
    selected_vehicles = []
    
    if input_dict.get(KEY_LL_IRC_CLASS_A):
        im_a = IRC6_2017.cl_208_2_impact_factor(span_m) if span_m > 0 else 0.15
        selected_vehicles.append({
            "name": "IRC Class A",
            "type": "Wheeled (Standard)",
            "impact": f"{1.0 + im_a:.3f}",
            "braking": braking_force_str,
            "centrifugal": centrifugal_str,
            "status": "Considered"
        })

    if input_dict.get(KEY_LL_IRC_70R_WHEELED):
        im_70r = IRC6_2017.cl_208_3_impact_factor(span_m) if span_m > 0 else 0.125
        selected_vehicles.append({
            "name": "IRC Class 70R (Wheeled)",
            "type": "Heavy Wheeled (100t)",
            "impact": f"{1.0 + im_70r:.3f}",
            "braking": braking_force_str,
            "centrifugal": centrifugal_str,
            "status": "Considered"
        })

    if input_dict.get(KEY_LL_IRC_70R_TRACKED):
        im_70rt = IRC6_2017.cl_208_3_impact_factor(span_m) if span_m > 0 else 0.10
        selected_vehicles.append({
            "name": "IRC Class 70R (Tracked)",
            "type": "Tracked (70t)",
            "impact": f"{1.0 + im_70rt:.3f}",
            "braking": braking_force_str,
            "centrifugal": centrifugal_str,
            "status": "Considered"
        })

    if input_dict.get(KEY_LL_IRC_AA_WHEELED):
        im_aa = IRC6_2017.cl_208_3_impact_factor(span_m) if span_m > 0 else 0.125
        selected_vehicles.append({
            "name": "IRC Class AA (Wheeled)",
            "type": "Heavy Wheeled",
            "impact": f"{1.0 + im_aa:.3f}",
            "braking": braking_force_str,
            "centrifugal": centrifugal_str,
            "status": "Considered"
        })

    if input_dict.get(KEY_LL_IRC_AA_TRACKED):
        im_aat = IRC6_2017.cl_208_3_impact_factor(span_m) if span_m > 0 else 0.10
        selected_vehicles.append({
            "name": "IRC Class AA (Tracked)",
            "type": "Tracked (70t)",
            "impact": f"{1.0 + im_aat:.3f}",
            "braking": braking_force_str,
            "centrifugal": centrifugal_str,
            "status": "Considered"
        })

    if input_dict.get(KEY_LL_IRC_CLASS_SV):
        selected_vehicles.append({
            "name": "IRC Class SV",
            "type": "Special Vehicle",
            "impact": "1.000",
            "braking": braking_force_str,
            "centrifugal": centrifugal_str,
            "status": "Considered"
        })

    if input_dict.get(KEY_LL_IRC_70R_BOGIE):
        selected_vehicles.append({
            "name": "IRC Class 70R (Bogie)",
            "type": "Bogie Trailer (40t)",
            "impact": "1.100",
            "braking": braking_force_str,
            "centrifugal": centrifugal_str,
            "status": "Considered"
        })

    if input_dict.get(KEY_LL_IRC_CLASS_FATIGUE):
        selected_vehicles.append({
            "name": "IRC Fatigue Vehicle",
            "type": "Fatigue Assessment",
            "impact": "1.000",
            "braking": "--",
            "centrifugal": centrifugal_str,
            "status": "Considered"
        })

    # Custom vehicles
    custom = input_dict.get(KEY_LL_CUSTOM_VEHICLES)
    if custom and isinstance(custom, list):
        for c in custom:
            name = c.get('name', 'Custom Vehicle') if isinstance(c, dict) else str(c)
            selected_vehicles.append({
                "name": name,
                "type": "User-Defined Custom",
                "impact": "1.000",
                "braking": braking_force_str,
                "centrifugal": centrifugal_str,
                "status": "Considered"
            })

    if not selected_vehicles:
        # Default fallback if nothing selected
        im_def = IRC6_2017.cl_208_2_impact_factor(span_m) if span_m > 0 else 0.15
        selected_vehicles.append({
            "name": "IRC Class A",
            "type": "Wheeled (Standard)",
            "impact": f"{1.0 + im_def:.3f}",
            "braking": braking_force_str,
            "centrifugal": centrifugal_str,
            "status": "Default"
        })

    for v in selected_vehicles:
        vehicle_rows.append(
            f"{_tex(v['name'])} & {_tex(v['type'])} & {v['impact']} & {v['braking']} & {v['centrifugal']} & {_tex(v['status'])} \\\\[4pt]\n\\hline"
        )
    vehicle_rows_str = "\n".join(vehicle_rows)

    # -------------------------------------------------------------------------
    # 2. Footway / Pedestrian Load Details
    # -------------------------------------------------------------------------
    fp_opt = str(input_dict.get(KEY_FOOTPATH, "")).strip().lower()
    no_fps = input_dict.get(KEY_TS_NO_OF_FOOTPATHS)
    has_footway = (fp_opt not in ("", "none", "0")) or (no_fps not in (None, "", 0, "0"))

    fp_intensity = "N/A"
    fp_ref = "IRC 6:2017 Cl. 206.1"
    fp_status = "Not Applicable (No Footway)"

    if has_footway:
        fp_mode = input_dict.get(KEY_LL_FOOTPATH_PRESSURE_MODE, "")
        fp_value = input_dict.get(KEY_LL_FOOTPATH_PRESSURE_VALUE, "")
        if str(fp_mode).strip().lower() in ("as per irc 6", "as per irc6", "automatic"):
            try:
                fp_load_val = IRC6_2017.cl_206_1_footway_load()
                fp_intensity = f"{fp_load_val:.3f} kN/m²"
                fp_ref = "IRC 6:2017 Cl. 206.1"
                fp_status = "Active on Footways"
            except Exception:
                fp_intensity = "N/A"
                fp_ref = "IRC 6:2017 Cl. 206.1"
                fp_status = "Unavailable"
        elif fp_value not in (None, ""):
            fp_intensity = f"{fp_value} kN/m²"
            fp_ref = "User Defined Input"
            fp_status = "Active on Footways"
        else:
            fp_intensity = "N/A"
            fp_ref = "IRC 6:2017 Cl. 206.1"
            fp_status = "Input Not Provided"

    # Pedestrian railing load
    rl_val = input_dict.get(KEY_RL_LOAD_VALUE)
    if rl_val not in (None, ""):
        try:
            rl_load_str = f"{float(rl_val):.3f} kN/m"
            rl_ref = "User Defined Input"
            rl_status = "Applied at top of railing"
        except Exception:
            rl_load_str = f"{rl_val} kN/m"
            rl_ref = "User Defined Input"
            rl_status = "Applied at top of railing"
    else:
        rl_load_str = "N/A"
        rl_ref = "IRC 6:2017 Cl. 206.3"
        rl_status = "Input Not Provided"

    # Kerb / Verge Vertical Surcharge
    kerb_present = input_dict.get(KEY_SAFETY_KERB_PRESENT)
    if kerb_present and str(kerb_present).strip().lower() not in ("none", "false", "0"):
        try:
            kerb_res = IRC6_2017.cl_206_2_kerb_load()
            k_val = kerb_res.get("kerb_load_kN_per_m2")
            kerb_load_str = f"{k_val:.3f} kN/m²" if k_val is not None else "N/A"
            kerb_ref = "IRC 6:2017 Cl. 206.2"
            kerb_status = "Applied on raised kerb"
        except Exception:
            kerb_load_str = "N/A"
            kerb_ref = "IRC 6:2017 Cl. 206.2"
            kerb_status = "Calculation Unavailable"
    else:
        kerb_load_str = "N/A"
        kerb_ref = "IRC 6:2017 Cl. 206.2"
        kerb_status = "Not Applicable (No Raised Kerb)"

    # Wind and Seismic calculations
    vz_val = input_dict.get(KEY_WL_HOURLY_MEAN_WIND)
    pz_val = input_dict.get(KEY_WL_HOURLY_WIND_PRESSURE)
    if not vz_val or not pz_val:
        try:
            _vb = input_dict.get(KEY_WL_BASIC_WIND_SPEED) or input_dict.get('wind_speed')
            _h = input_dict.get(KEY_WL_AVG_EXPOSED_HEIGHT)
            _ter = {
                "Plain Terrain": "plain",
                "Terrain with Obstructions": "obstructed",
            }.get(str(input_dict.get(KEY_WL_TERRAIN_TYPE, "")).strip(), "plain")
            if _h and _vb:
                _res = IRC6_2017.table_12(float(_h), _ter, float(_vb))
                if not vz_val:
                    vz_val = _res.get("Vz")
                if not pz_val:
                    pz_val = _res.get("Pz")
        except Exception:
            pass

    vz_str = f"{float(vz_val):.2f} m/s" if vz_val not in (None, "") else "N/A"
    pz_str = f"{float(pz_val):.2f} N/m²" if pz_val not in (None, "") else "N/A"

    # Seismic coefficients
    sl_zone_factor = input_dict.get(KEY_SL_ZONE_FACTOR)
    sl_spectral = input_dict.get(KEY_SL_SPECTRAL_COEFF)
    sl_ah = input_dict.get(KEY_SL_HORIZONTAL_COEFF)
    sl_av = input_dict.get(KEY_SL_VERTICAL_COEFF)

    # Temperature
    tl_temp_min = tl_temp_max = tl_rise = tl_fall = "N/A"
    try:
        _tmax = input_dict.get(KEY_TL_HIGHEST_MAX_TEMP) or input_dict.get('shade_temp_max')
        _tmin = input_dict.get(KEY_TL_LOWEST_MIN_TEMP) or input_dict.get('shade_temp_min')
        if _tmax and _tmin:
            _res = IRC6_2017.cl_215_2_effective_bridge_temperature(
                float(_tmax), float(_tmin), 'metallic', False
            )
            _bt_min = _res.get('T_min', 0)
            _bt_max = _res.get('T_max', 0)
            _mean = (_bt_max + _bt_min) / 2.0
            tl_temp_min = f"{_bt_min:.2f}"
            tl_temp_max = f"{_bt_max:.2f}"
            tl_rise = f"{_bt_max - _mean:.2f}"
            tl_fall = f"{_mean - _bt_min:.2f}"
    except Exception:
        pass

    # Load Combinations
    _LOAD_LABEL_MAP = {
        'dead_load': 'DL',
        'surfacing': 'SIDL',
        'live_load': 'LL',
        'wind_load': 'WL',
        'thermal_load': 'TL',
        'vehicle_collision': 'VC',
        'barge_impact': 'BI',
        'floating_bodies': 'FB',
        'seismic': 'EQ',
    }

    def _fmt_factors(factors):
        parts = []
        for load, val in factors.items():
            label = _LOAD_LABEL_MAP.get(load, load.upper())
            if isinstance(val, dict):
                add = val.get('adding')
                rel = val.get('relieving')
                add_s = f"{add:.2f}" if add is not None else '--'
                rel_s = f"{rel:.2f}" if rel is not None else '--'
                parts.append(f"{label}({add_s}/{rel_s})")
            else:
                if val is None:
                    continue
                parts.append(f"{label}({val:.2f})")
        return ' + '.join(parts)

    uls_combos = IRC6_2017.uls_load_combinations()
    sls_combos = IRC6_2017.sls_load_combinations()
    lc_rows = []
    for i, combo in enumerate(uls_combos, start=1):
        cases = _fmt_factors(combo['factors'])
        lc_rows.append(f"ULS-{i:02d} & {cases} \\\\[4pt]\n\\hline")
    for i, combo in enumerate(sls_combos, start=1):
        cases = _fmt_factors(combo['factors'])
        lc_rows.append(f"SLS-{i:02d} & {cases} \\\\[4pt]\n\\hline")

    lc_rows_str = "\n".join(lc_rows)

    # -------------------------------------------------------------------------
    # Generate LongTable Headers with styles.py engine
    # -------------------------------------------------------------------------
    t31_hdr = build_longtable_header("Dead Load --- Self Weight", ["\\textbf{Parameter}", "\\textbf{Value}"], num_cols=2)
    t32_hdr = build_longtable_header("Dead Load for Surfacing and Superimposed Dead Load (DW/SIDL)", ["\\textbf{Parameter}", "\\textbf{Value}"], num_cols=2)
    t33_hdr = build_longtable_header(
        "Vehicle Live Loads (LL) Parameters and Impact Factors",
        ["\\textbf{Vehicle Class}", "\\textbf{Configuration / Type}", "\\textbf{Impact Factor (1+IF)}", "\\textbf{Braking Force (kN)}", "\\textbf{Centrifugal (kN)}", "\\textbf{Status}"],
        num_cols=6
    )
    t34_hdr = build_longtable_header(
        "Footway and Pedestrian Live Loads (LL)",
        ["\\textbf{Parameter}", "\\textbf{Standard Reference}", "\\textbf{Design Value}", "\\textbf{Status / Application}"],
        num_cols=4
    )
    t35_hdr = build_longtable_header("Wind Load (WL) --- per IRC 6", ["\\textbf{Parameter}", "\\textbf{Value}"], num_cols=2)
    t36_hdr = build_longtable_header("Earthquake Load (EL) --- per IRC 6", ["\\textbf{Parameter}", "\\textbf{Value}"], num_cols=2)
    t37_hdr = build_longtable_header("Temperature Load (TL) --- per IRC 6", ["\\textbf{Parameter}", "\\textbf{Value}"], num_cols=2)
    t38_hdr = build_longtable_header("IRC 6 Analysis Load Combinations", ["\\textbf{Combination ID}", "\\textbf{Factored Load Cases}"], num_cols=2)

    return r"""
\chapter{Loads and Load Combinations}

This section summarizes all gravity, vehicular live, pedestrian, climatic, and seismic loads applied to the bridge, along with the governing limit-state load combinations considered for analysis and design in accordance with IRC 6:2017.

\vspace{0.8em}
\begin{longtable}{|L{6.0cm}|p{9.5cm}|}
""" + t31_hdr + r"""
\textnormal{Steel Structural Self-Weight} & """ + (_render_value(input_dict, KEY_MATERIAL_GIRDER_DENSITY, r' kN/m\textsuperscript{3}')) + r""" \\[4pt]
\hline
\textnormal{Concrete Deck Slab Unit Weight} & """ + (_render_value(input_dict, KEY_MATERIAL_DECK_DENSITY, r' kN/m\textsuperscript{3}')) + r""" \\[4pt]
\hline
\textnormal{Self-Weight Multiplication Factor} & """ + (_render_value(input_dict, KEY_PL_SELF_WEIGHT_FACTOR)) + r""" \\[4pt]
\end{longtable}

\vspace{0.8em}
\begin{longtable}{|L{6.0cm}|p{9.5cm}|}
""" + t32_hdr + r"""
\textnormal{Wearing Course Material \& Thickness} & """ + (_render_value(input_dict, KEY_WC_MATERIAL)) + r""" $\times$ """ + (_render_value(input_dict, KEY_WC_THICKNESS)) + r""" mm \\[4pt]
\hline
\textnormal{Crash Barrier Line Load} & """ + (_render_value(input_dict, KEY_CB_LOAD)) + r""" kN/m per barrier \\[4pt]
\hline
\textnormal{Pedestrian Railing Line Load} & """ + (_render_value(input_dict, KEY_RL_LOAD_VALUE)) + r""" kN/m\sdstar{} \\[4pt]
\end{longtable}

\vspace{0.8em}
\begingroup
\setlength{\tabcolsep}{3.5pt}
\begin{longtable}{|L{3.2cm}|C{3.0cm}|C{2.4cm}|C{2.2cm}|C{2.0cm}|C{1.7cm}|}
""" + t33_hdr + r"""
""" + vehicle_rows_str + r"""
\end{longtable}
\endgroup
\noindent\textit{Note: Live load vehicles are populated as selected in the UI Loading Tab. Impact factor and braking forces are computed strictly per IRC 6:2017 Clauses 208 and 211. Centrifugal force is 0.00 kN for straight bridge alignments per IRC 6:2017 Cl. 212.}

\vspace{0.8em}
\begingroup
\setlength{\tabcolsep}{4.0pt}
\begin{longtable}{|L{4.8cm}|C{3.5cm}|C{3.0cm}|C{3.5cm}|}
""" + t34_hdr + r"""
\textnormal{Footway Live Load Intensity} & """ + _tex(fp_ref) + r""" & """ + _tex(fp_intensity) + r""" & \textnormal{""" + _tex(fp_status) + r"""} \\[4pt]
\hline
\textnormal{Pedestrian Railing Horizontal Load} & """ + _tex(rl_ref) + r""" & """ + _tex(rl_load_str) + r""" & \textnormal{""" + _tex(rl_status) + r"""} \\[4pt]
\hline
\textnormal{Kerb / Verge Vertical Surcharge} & """ + _tex(kerb_ref) + r""" & """ + _tex(kerb_load_str) + r""" & \textnormal{""" + _tex(kerb_status) + r"""} \\[4pt]
\end{longtable}
\endgroup

\vspace{0.8em}
\begin{longtable}{|L{6.0cm}|p{9.5cm}|}
""" + t35_hdr + r"""
\textnormal{Basic Wind Speed, $V_b$} & """ + (_render_value(input_dict, 'wind_speed', ' m/s')) + r""" [Location Database] \\[4pt]
\hline
\textnormal{Terrain Category} & """ + (_render_value(input_dict, KEY_WL_TERRAIN_TYPE)) + r""" \\[4pt]
\hline
\textnormal{Average Exposed Height, $H$} & """ + (_render_value(input_dict, KEY_WL_AVG_EXPOSED_HEIGHT, ' m')) + r""" \\[4pt]
\hline
\textnormal{Hourly Mean Wind Speed, $V_z$} & """ + _tex(vz_str) + r""" \\[4pt]
\hline
\textnormal{Hourly Wind Pressure, $P_z$} & """ + _tex(pz_str) + r""" \\[4pt]
\hline
\textnormal{Transverse Wind Force} & """ + (_render_value(input_dict, KEY_WL_TRANSVERSE_WIND_FORCE, ' kN')) + r""" \\[4pt]
\hline
\textnormal{Longitudinal Wind Force} & """ + (_render_value(input_dict, KEY_WL_LONGITUDINAL_WIND_FORCE, ' kN')) + r""" \\[4pt]
\hline
\textnormal{Vertical Wind Force} & """ + (_render_value(input_dict, KEY_WL_VERTICAL_WIND_FORCE, ' kN')) + r""" \\[4pt]
\end{longtable}

\vspace{0.8em}
\begin{longtable}{|L{6.0cm}|p{9.5cm}|}
""" + t36_hdr + r"""
\textnormal{Seismic Zone} & """ + (_render_value(input_dict, 'seismic_zone')) + r""" [Location Database] \\[4pt]
\hline
\textnormal{Zone Factor, $Z$} & """ + (_render_value(input_dict, KEY_SL_ZONE_FACTOR)) + r""" \\[4pt]
\hline
\textnormal{Importance Factor, $I$} & """ + (_render_value(input_dict, KEY_SL_IMPORTANCE_FACTOR)) + r""" \\[4pt]
\hline
\textnormal{Soil Foundation Type} & """ + (_render_value(input_dict, KEY_SL_SOIL_TYPE)) + r""" \\[4pt]
\hline
\textnormal{Spectral Acceleration Coefficient, $S_a/g$} & """ + (_render_value(input_dict, KEY_SL_SPECTRAL_COEFF)) + r""" \\[4pt]
\hline
\textnormal{Horizontal Seismic Coefficient, $A_h$} & """ + (_render_value(input_dict, KEY_SL_HORIZONTAL_COEFF)) + r""" \\[4pt]
\hline
\textnormal{Vertical Seismic Coefficient, $A_v$} & """ + (_render_value(input_dict, KEY_SL_VERTICAL_COEFF)) + r""" \\[4pt]
\end{longtable}

\vspace{0.8em}
\begin{longtable}{|L{6.0cm}|p{9.5cm}|}
""" + t37_hdr + r"""
\textnormal{Maximum Shade Temperature} & """ + (_render_value(input_dict, 'shade_temp_max')) + r""" $^\circ$C \\[4pt]
\hline
\textnormal{Minimum Shade Temperature} & """ + (_render_value(input_dict, 'shade_temp_min')) + r""" $^\circ$C \\[4pt]
\hline
\textnormal{Effective Bridge Temp. Range} & """ + (_render_value(input_dict, KEY_TL_BRIDGE_TEMP_MIN)) + r""" to """ + (_render_value(input_dict, KEY_TL_BRIDGE_TEMP_MAX)) + r""" $^\circ$C \\[4pt]
\hline
\textnormal{Temperature Rise / Fall for Design} & +""" + (_render_value(input_dict, KEY_TL_TEMP_RISE)) + r""" $^\circ$C / \textminus{}""" + (_render_value(input_dict, KEY_TL_TEMP_FALL)) + r""" $^\circ$C \\[4pt]
\end{longtable}

\vspace{0.8em}
\begin{longtable}{|C{3.5cm}|p{12.0cm}|}
""" + t38_hdr + r"""
""" + lc_rows_str + r"""
\end{longtable}

\noindent\textit{Note: All IRC 6:2017 Limit State combinations (ULS and SLS) are generated by OsdagBridge.}
"""
