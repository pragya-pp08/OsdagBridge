# =============================================================================
# Chapter 7: Material Take-off & Quantity Summary
# Refactored for OsdagBridge Report Generator
#   - Embedded Material Quantity Bar Charts (Structural Steel, Concrete vs Rebar)
#   - Repeated table headers across page breaks using styles.py LongTable engine
# =============================================================================

from .styles import build_longtable_header, PALETTE


def ch7_quantities(input_dict, fig_paths=None):
    fig_paths = fig_paths or {}
    
    # Header for Table 7.1
    t71_hdr = build_longtable_header(
        "Bill of Materials (Steel, Concrete, and Reinforcement Quantities)",
        ["\\textbf{S.N.}", "\\textbf{Item Description}", "\\textbf{Volume Formula}", "\\textbf{Qty}", "\\textbf{Total Volume}", "\\textbf{Weight (MT)}", "\\textbf{Total Weight (MT)}"],
        num_cols=7,
        label="tab:bom"
    )

    steel_fig_path = fig_paths.get("material_steel", "assets/material_steel_tonnage.png")
    steel_fig_latex = (
        r"\begin{figure}[H]" + "\n"
        r"\centering" + "\n"
        r"\includegraphics[width=0.88\textwidth]{" + steel_fig_path + "}\n"
        r"\caption{\textbf{Structural Steel Quantity Breakdown by Component (Metric Tonnes, MT)}}" + "\n"
        r"\label{fig:material_steel}" + "\n"
        r"\end{figure}"
    )

    concrete_rebar_path = fig_paths.get("material_concrete_rebar", "assets/material_concrete_rebar.png")
    concrete_rebar_fig_latex = (
        r"\begin{figure}[H]" + "\n"
        r"\centering" + "\n"
        r"\includegraphics[width=0.88\textwidth]{" + concrete_rebar_path + "}\n"
        r"\caption{\textbf{Concrete Volume (m\textsuperscript{3}) vs. Reinforcement Steel Weight (MT)}}" + "\n"
        r"\label{fig:material_concrete_rebar}" + "\n"
        r"\end{figure}"
    )

    return r"""
\chapter{Material Take-off \& Quantity Summary}
\label{ch:material-takeoff}

This chapter provides a detailed engineering Bill of Materials (BOM) and material take-off for the steel-concrete composite girder bridge superstructure. All calculated component quantities are based on the final structural design outputs.

\section{Bill of Materials Summary Table}

\begingroup
\setlength{\tabcolsep}{3.5pt}
\begin{longtable}{|C{1.0cm}|L{3.8cm}|C{2.6cm}|C{1.2cm}|C{1.8cm}|C{1.8cm}|C{1.8cm}|}
""" + t71_hdr + r"""
1 & Structural Steel (IS 2062) for Girders & """ + str(input_dict.get("steel_girders_vol_formula", "N.A.")) + r""" & """ + str(input_dict.get("steel_girders_qty", "N.A.")) + r""" & """ + str(input_dict.get("steel_girders_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("steel_girders_wt_single", "N.A.")) + r""" & """ + str(input_dict.get("steel_girders_wt_total", "N.A.")) + r""" \\[4pt]
\hline
2(a) & Cross Bracing --- Top Chord & """ + str(input_dict.get("bracing_top_vol_formula", "N.A.")) + r""" & """ + str(input_dict.get("bracing_top_qty", "N.A.")) + r""" & """ + str(input_dict.get("bracing_top_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("bracing_top_wt_single", "N.A.")) + r""" & """ + str(input_dict.get("bracing_top_wt_total", "N.A.")) + r""" \\[4pt]
\hline
2(b) & Cross Bracing --- Bottom Chord & """ + str(input_dict.get("bracing_bot_vol_formula", "N.A.")) + r""" & """ + str(input_dict.get("bracing_bot_qty", "N.A.")) + r""" & """ + str(input_dict.get("bracing_bot_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("bracing_bot_wt_single", "N.A.")) + r""" & """ + str(input_dict.get("bracing_bot_wt_total", "N.A.")) + r""" \\[4pt]
\hline
2(c) & Cross Bracing --- Diagonal Chord & """ + str(input_dict.get("bracing_diag_vol_formula", "N.A.")) + r""" & """ + str(input_dict.get("bracing_diag_qty", "N.A.")) + r""" & """ + str(input_dict.get("bracing_diag_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("bracing_diag_wt_single", "N.A.")) + r""" & """ + str(input_dict.get("bracing_diag_wt_total", "N.A.")) + r""" \\[4pt]
\hline
3 & Concrete (M40) for Deck Slab & """ + str(input_dict.get("concrete_deck_vol_formula", "N.A.")) + r""" & """ + str(input_dict.get("concrete_deck_qty", "N.A.")) + r""" & """ + str(input_dict.get("concrete_deck_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("concrete_deck_wt_single", "N.A.")) + r""" & """ + str(input_dict.get("concrete_deck_wt_total", "N.A.")) + r""" \\[4pt]
\hline
4 & Reinforcement Steel (Fe 500) & """ + str(input_dict.get("rebar_deck_vol_formula", "N.A.")) + r""" & """ + str(input_dict.get("rebar_deck_qty", "N.A.")) + r""" & """ + str(input_dict.get("rebar_deck_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("rebar_deck_wt_single", "N.A.")) + r""" & """ + str(input_dict.get("rebar_deck_wt_total", "N.A.")) + r""" \\[4pt]
\hline
5 & Shear Stud Connectors & """ + str(input_dict.get("shear_studs_vol_formula", "N.A.")) + r""" & """ + str(input_dict.get("shear_studs_qty", "N.A.")) + r""" & """ + str(input_dict.get("shear_studs_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("shear_studs_wt_single", "N.A.")) + r""" & """ + str(input_dict.get("shear_studs_wt_total", "N.A.")) + r""" \\[4pt]
\hline
6 & Crash Barrier (Reinforced Concrete) & """ + str(input_dict.get("crash_barrier_vol_formula", "N.A.")) + r""" & """ + str(input_dict.get("crash_barrier_qty", "N.A.")) + r""" & """ + str(input_dict.get("crash_barrier_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("crash_barrier_wt_single", "N.A.")) + r""" & """ + str(input_dict.get("crash_barrier_wt_total", "N.A.")) + r""" \\[4pt]
\end{longtable}
\endgroup

\clearpage
\section{Material Quantity Visualizations}

The following charts summarize the distribution of structural steel tonnage across components and the concrete-to-reinforcement balance for construction estimation.

""" + steel_fig_latex + r"""

\vspace{0.8em}

""" + concrete_rebar_fig_latex + r"""
"""
