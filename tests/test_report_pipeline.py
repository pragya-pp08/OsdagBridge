# =============================================================================
# OsdagBridge — Automated Report Generator Pipeline Test & Verification Suite
# =============================================================================

import os
import sys
import shutil
import pytest

# Ensure src is on sys.path
SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from osdagbridge.core.reports.report_generator import (
    ReportMetadata,
    ReportOptions,
    ReportRequest,
    ReportFigures,
    ReportPayload,
    ReportDataBridge,
    build_report_payload,
    generate_report,
)
from osdagbridge.core.reports.styles import (
    PALETTE,
    GEOMETRY,
    TABLE_STYLE,
    get_latex_color_definitions,
    build_page_styles,
    build_longtable_header,
    enhance_longtables_in_tex,
)
from osdagbridge.core.reports.plots import (
    generate_utilization_ratio_plot,
    generate_material_quantity_plots,
)
from osdagbridge.core.reports.chap3 import ch3_loads
from osdagbridge.core.reports.chap5 import extract_design_checks_summary, ch5_design_checks
from osdagbridge.core.utils.common import (
    KEY_SPAN,
    KEY_TS_NO_OF_GIRDERS,
    KEY_TS_GIRDER_SPACING,
    KEY_TS_DECK_THICKNESS,
    KEY_TS_DECK_OVERHANG,
    KEY_LL_IRC_CLASS_A,
    KEY_LL_IRC_70R_WHEELED,
    KEY_LL_FOOTPATH_PRESSURE_MODE,
    KEY_LL_FOOTPATH_PRESSURE_VALUE,
    KEY_WC_MATERIAL,
    KEY_WC_THICKNESS,
    KEY_CB_LOAD,
    KEY_RL_LOAD_VALUE,
    KEY_MATERIAL_GIRDER_DENSITY,
    KEY_MATERIAL_DECK_DENSITY,
    KEY_PL_SELF_WEIGHT_FACTOR,
)


def get_sample_bridge_data():
    """Construct representative 30m composite plate girder bridge data."""
    inputs = {
        KEY_SPAN: "30.0",
        KEY_TS_NO_OF_GIRDERS: "4",
        KEY_TS_GIRDER_SPACING: "2.8",
        KEY_TS_DECK_THICKNESS: "250",
        KEY_TS_DECK_OVERHANG: "1.2",
        "typical_section.overall_bridge_width": "11.5",
        "typical_section.carriageway_width": "7.5",
        "typical_section.lane_details.lane_table_count": "2",
        KEY_WC_MATERIAL: "Bituminous Concrete",
        KEY_WC_THICKNESS: "75",
        KEY_CB_LOAD: "0.85",
        KEY_RL_LOAD_VALUE: "0.40",
        KEY_MATERIAL_GIRDER_DENSITY: "78.5",
        KEY_MATERIAL_DECK_DENSITY: "25.0",
        KEY_PL_SELF_WEIGHT_FACTOR: "1.0",
        KEY_LL_IRC_CLASS_A: True,
        KEY_LL_IRC_70R_WHEELED: True,
        KEY_LL_FOOTPATH_PRESSURE_MODE: "As per IRC 6",
        KEY_LL_FOOTPATH_PRESSURE_VALUE: "4.0",
        "geometry.footpath": "Both Sides",
        "wind_speed": "44",
        "seismic_zone": "IV",
        "shade_temp_max": "45",
        "shade_temp_min": "-5",
        # Girder dimensions (G1..G4)
        "member_properties.girder_details.section_input.web_depth": "1800",
        "member_properties.girder_details.section_input.web_thickness": "14",
        "member_properties.girder_details.section_input.top_flange_width": "500",
        "member_properties.girder_details.section_input.top_flange_thickness": "32",
        "member_properties.girder_details.section_input.bottom_flange_width": "600",
        "member_properties.girder_details.section_input.bottom_flange_thickness": "40",
        "member_properties.girder_details.section_properties.area": "0.0684",
        "member_properties.girder_details.section_properties.mass": "536.94",
        "typical_section.crash_barrier.area": "250000",
        "member_properties.end_diaphragm_details.end_diaphragm_type": "Cross Bracing",
        "member_properties.end_diaphragm_details.section_properties.mass": "45.0",
    }

    outputs = {
        "steeldesign.details.shear.longitudinal_spacing": "150",
        "steeldesign.details.shear.studs_per_section": "3",
        "steeldesign.details.shear.diameter": "22",
        "steeldesign.details.shear.height": "150",
        "crossbracing_forces_dict": {
            "brace_type": "X",
            "geometry": {
                "alpha_deg": 42.5,
                "diagonal_length_m": 3.45,
                "horiz_proj_m": 2.8,
                "cb_spacing_m": 5.0,
            },
            "pairs": {
                "G1-G2": {
                    "diag_tension_kN": 145.2,
                    "diag_compression_kN": -162.8,
                    "chord_tension_kN": 55.4,
                    "chord_compression_kN": -62.1,
                },
                "G2-G3": {
                    "diag_tension_kN": 120.5,
                    "diag_compression_kN": -135.0,
                    "chord_tension_kN": 45.0,
                    "chord_compression_kN": -50.2,
                },
                "G3-G4": {
                    "diag_tension_kN": 145.2,
                    "diag_compression_kN": -162.8,
                    "chord_tension_kN": 55.4,
                    "chord_compression_kN": -62.1,
                },
            },
        },
        "crossbracing_design_results": {
            "G1-G2": {
                "diagonal": {
                    "compression": {
                        "section": "ISA 100 x 100 x 10",
                        "capacity_kN": 210.5,
                        "efficiency": 0.773,
                        "slenderness": 112.4,
                        "connection": "Welded",
                    },
                    "tension": {
                        "section": "ISA 100 x 100 x 10",
                        "capacity_kN": 285.0,
                        "efficiency": 0.509,
                        "slenderness": 112.4,
                        "connection": "Welded",
                    },
                },
                "chord": {
                    "compression": {
                        "section": "ISA 90 x 90 x 8",
                        "capacity_kN": 145.0,
                        "efficiency": 0.428,
                        "slenderness": 95.0,
                        "connection": "Welded",
                    },
                    "tension": {
                        "section": "ISA 90 x 90 x 8",
                        "capacity_kN": 195.0,
                        "efficiency": 0.284,
                        "slenderness": 95.0,
                        "connection": "Welded",
                    },
                },
            },
        },
        "design_results": {
            "per_girder": {
                "G1": {
                    "checks": [
                        {"check_id": 1, "demand": 4200.0, "capacity": 5100.0, "dcr": 0.824, "demand_unit": "kN-m", "capacity_unit": "kN-m"},
                        {"check_id": 2, "demand": 950.0, "capacity": 1500.0, "dcr": 0.633, "demand_unit": "kN", "capacity_unit": "kN"},
                        {"check_id": 5, "demand": 3800.0, "capacity": 5000.0, "dcr": 0.760, "demand_unit": "kN-m", "capacity_unit": "kN-m"},
                        {"check_id": 11, "demand": 210.0, "capacity": 250.0, "dcr": 0.840, "demand_unit": "MPa", "capacity_unit": "MPa"},
                    ],
                    "per_lc": {
                        "ULS 1": {
                            "checks": [
                                {"id": 1, "demand": 4200.0, "capacity": 5100.0, "dcr": 0.824},
                                {"id": 2, "demand": 950.0, "capacity": 1500.0, "dcr": 0.633},
                            ]
                        },
                        "SLS 1": {
                            "checks": [
                                {"id": 13, "demand": 24.5, "capacity": 37.5, "dcr": 0.653},
                            ]
                        }
                    }
                }
            }
        },
        "deck_design_results": {
            "rebar_bottom_area": 1250,
            "rebar_top_area": 1050,
        },
        "deck_report_values": {
            "deck_design.moment.m_uls_sag": 145.0,
            "deck_design.moment.mu_bot": 195.0,
            "deck_design.moment.m_uls_hog": 120.0,
            "deck_design.moment.mu_top": 180.0,
            "deck_design.crack.wk_bot": 0.18,
            "deck_design.crack.wk_top": 0.15,
            "deck_design.crack.limit": 0.25,
        }
    }
    return inputs, outputs


def test_styles_engine_and_headers():
    """Verify centralized styling configuration and longtable header joining."""
    assert PALETTE.PRIMARY == "#91B014"
    assert PALETTE.PASS == "#2E7D32"
    assert PALETTE.FAIL == "#C62828"

    geo_tex = GEOMETRY.to_latex_geometry()
    assert "left=20mm" in geo_tex
    assert "bottom=28mm" in geo_tex
    assert "footskip=18pt" in geo_tex

    tbl_tex = TABLE_STYLE.to_latex_preamble_block()
    assert "\\tabcolsep" in tbl_tex
    assert "\\needspace" in tbl_tex

    colors_tex = get_latex_color_definitions()
    assert "definecolor{osdagGreen}" in colors_tex
    assert "definecolor{osdagPass}" in colors_tex
    assert "definecolor{osdagFail}" in colors_tex

    # Verify build_longtable_header joins columns with " & " (Issue 3 fix)
    cols = [r"\textbf{Col 1}", r"\textbf{Col 2}", r"\textbf{Col 3}"]
    hdr = build_longtable_header("Test Table", cols, num_cols=3)
    assert r"\textbf{Col 1} & \textbf{Col 2} & \textbf{Col 3}" in hdr
    assert "\\endfirsthead" in hdr
    assert "\\endhead" in hdr
    assert "\\endfoot" in hdr
    assert "\\endlastfoot" in hdr
    # Verify column headers are NOT on separate stacked rows
    assert r"\textbf{Col 1} \\" not in hdr.split("&")[0]


def test_plot_generation(tmp_path):
    """Verify programmatic generation of UR and Material Quantity plots (Issues 1 & 2)."""
    out_dir = str(tmp_path / "assets")
    os.makedirs(out_dir, exist_ok=True)

    # 1. Utilization Ratio plot with real values
    checks = [
        {"element": "Girder Moment", "ur": 0.82, "group": "Girders"},
        {"element": "Girder Shear", "ur": 0.64, "group": "Girders"},
        {"element": "Girder LTB", "ur": 0.76, "group": "Girders"},
        {"element": "Deck Slab Mid-Span", "ur": 0.69, "group": "Deck Slab"},
        {"element": "Cross Bracing", "ur": 0.77, "group": "Cross Bracing"},
        {"element": "End Diaphragm", "ur": 0.55, "group": "End Diaphragms"},
    ]
    ur_path = os.path.join(out_dir, "utilization_ratio_summary.png")
    res_ur = generate_utilization_ratio_plot(checks, ur_path)
    assert os.path.exists(res_ur)
    assert os.path.getsize(res_ur) > 1000

    # 2. Material Quantity plots with End Diaphragms (not shear studs)
    quantities = {
        "steel_girders_wt_total": "64.4",
        "steel_bracing_wt_total": "9.6",
        "end_diaphragm_wt_total": "3.2",
        "concrete_deck_vol_total": "86.25",
        "rebar_deck_wt_total": "10.35",
        "crash_barrier_vol_total": "15.0",
    }
    steel_p, conc_p = generate_material_quantity_plots(quantities, out_dir)
    assert os.path.exists(steel_p)
    assert os.path.getsize(steel_p) > 1000
    assert os.path.exists(conc_p)
    assert os.path.getsize(conc_p) > 1000


def test_plot_empty_data_honest(tmp_path):
    """Verify that empty check data does NOT inject fake/sample numbers like 0.84 (Issue 1)."""
    out_dir = str(tmp_path / "assets_empty")
    os.makedirs(out_dir, exist_ok=True)

    ur_path = os.path.join(out_dir, "ur_empty.png")
    # Must handle empty list honestly without fake values
    generate_utilization_ratio_plot([], ur_path)
    assert os.path.exists(ur_path)
    assert os.path.getsize(ur_path) > 1000

    # Material quantities with empty/missing data: should not fabricate 18.5, 45.0, etc.
    empty_quantities = {}
    steel_p, conc_p = generate_material_quantity_plots(empty_quantities, out_dir)
    assert os.path.exists(steel_p)
    assert os.path.exists(conc_p)


def test_chap3_loads_and_fallbacks():
    """Verify Chapter 3 load calculations, centrifugal 0.00 explanation, and footway (Issue 4)."""
    inputs, _ = get_sample_bridge_data()
    tex = ch3_loads(inputs)

    # 1. Straight bridge centrifugal force must be 0.00 (Straight)
    assert "0.00 (Straight)" in tex
    # 2. Vehicle Class & Impact factor
    assert "IRC Class A" in tex
    assert "IRC Class 70R" in tex
    # 3. Table widths and headers
    assert "Vehicle Live Loads (LL)" in tex
    assert "Footway and Pedestrian Live Loads" in tex


def test_chap5_table_and_chart_parity():
    """Verify that Chapter 5 Table 5.22 and the UR chart extract from the exact same data source (Issue 1)."""
    inputs, outputs = get_sample_bridge_data()
    meta = ReportMetadata(
        project_name="Test Bridge",
        project_location="Mumbai",
        designer="Engineer",
        client="Client",
        company="Company"
    )
    options = ReportOptions(
        sections=['design_checks'],
        include_figures=True,
        include_toc=True,
        include_pdf=False,
    )
    request = ReportRequest(
        metadata=meta,
        options=options,
        output_dir=".",
        file_stem="test_parity",
    )
    payload = build_report_payload(request, inputs, outputs)
    bridge = ReportDataBridge(payload.output_dict, payload.inputs, payload)

    t522_rows, checks_summary = extract_design_checks_summary(bridge)
    assert len(t522_rows) == 18
    assert len(checks_summary) == 18

    # Verify that Girder Moment UR in Table 5.22 matches checks_summary
    gm_check = next(c for c in checks_summary if c["element"] == "Girder Moment")
    assert gm_check["ur"] is not None
    assert round(gm_check["ur"], 2) == 0.82

    # Verify that Table 5.22 text contains "0.82"
    t522_text = "\n".join(t522_rows)
    assert "0.82" in t522_text


def test_report_options_include_pdf_false(tmp_path):
    """Verify that include_pdf=False skips compiler execution and returns ReportResult(pdf_path=None) (Issue 5)."""
    output_dir = str(tmp_path / "deliverables_nopdf")
    os.makedirs(output_dir, exist_ok=True)

    inputs, outputs = get_sample_bridge_data()
    meta = ReportMetadata(
        project_name="No-PDF Test Bridge",
        project_location="Delhi",
        designer="Engineer",
        client="Client",
        company="Company"
    )
    options = ReportOptions(
        sections=['loads', 'design_checks', 'drawings'],
        include_figures=True,
        include_toc=True,
        include_pdf=False,  # Explicitly disabled
    )
    request = ReportRequest(
        metadata=meta,
        options=options,
        output_dir=output_dir,
        file_stem="Report_NoPDF",
    )

    payload = build_report_payload(request, inputs, outputs)
    result = generate_report(payload, request)

    assert result.tex_path is not None
    assert os.path.exists(result.tex_path)
    assert result.pdf_path is None  # Must NOT attempt to produce PDF when include_pdf is False


def test_full_report_tex_pipeline(tmp_path):
    """Verify end-to-end report assembly and LaTeX output."""
    output_dir = str(tmp_path / "deliverables")
    os.makedirs(output_dir, exist_ok=True)

    inputs, outputs = get_sample_bridge_data()

    meta = ReportMetadata(
        project_name="NH-48 Composite Steel Girder Bridge",
        project_location="Pune, Maharashtra",
        designer="FOSSEE Design Engineer",
        client="National Highways Authority of India (NHAI)",
        company="OsdagBridge Structural Group",
        job_number="OB-2026-30M",
        subtitle="Detailed Design Verification Report",
    )

    options = ReportOptions(
        sections=['loads', 'analysis', 'design_checks', 'drawings'],
        include_figures=True,
        include_toc=True,
        include_pdf=False,
    )

    request = ReportRequest(
        metadata=meta,
        options=options,
        output_dir=output_dir,
        file_stem="Report_After",
    )

    payload = build_report_payload(request, inputs, outputs)
    result = generate_report(payload, request)

    assert result.tex_path is not None
    assert os.path.exists(result.tex_path)

    with open(result.tex_path, 'r', encoding='utf-8') as f:
        tex = f.read()

    # 1. Repeated table headers
    assert "\\endfirsthead" in tex
    assert "\\endhead" in tex
    assert "\\endfoot" in tex
    assert "\\endlastfoot" in tex
    assert tex.count("\\endfirsthead") >= 20

    # 2. Centralized styles
    assert "left=20mm" in tex
    assert "bottom=28mm" in tex
    assert "\\definecolor{osdagGreen}" in tex

    # 3. Chapter 3 Refactoring
    assert "Vehicle Live Loads (LL)" in tex
    assert "IRC Class A" in tex
    assert "IRC Class 70R" in tex
    assert "Footway and Pedestrian Live Loads" in tex
    assert "0.00 (Straight)" in tex

    # 4. Section 5.5 UR Visualization
    assert "Overall Design Check Summary" in tex
    assert "utilization_ratio_summary.png" in tex

    # 5. Chapter 7 Material Quantity Visualizations & End Diaphragms
    assert "Material Quantity Visualizations" in tex
    assert "material_steel_tonnage.png" in tex
    assert "material_concrete_rebar.png" in tex
    assert "End Diaphragms" in tex

    # 6. Centralized status color verification
    assert r"\textcolor{osdagPass}{\textbf{PASS}}" in tex

    print("\n[SUCCESS] All LaTeX Report Generator enhancements verified!")


if __name__ == "__main__":
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        from pathlib import Path
        p = Path(td)
        test_styles_engine_and_headers()
        print("[PASS] Styles Engine verified")
        test_plot_generation(p)
        print("[PASS] Plot Generation verified")
        test_plot_empty_data_honest(p)
        print("[PASS] Empty Data Honesty verified")
        test_chap3_loads_and_fallbacks()
        print("[PASS] Chapter 3 Loads verified")
        test_chap5_table_and_chart_parity()
        print("[PASS] Chapter 5 Parity verified")
        test_report_options_include_pdf_false(p)
        print("[PASS] include_pdf=False verified")
        test_full_report_tex_pipeline(p)
        print("[PASS] Full Report Pipeline verified")
