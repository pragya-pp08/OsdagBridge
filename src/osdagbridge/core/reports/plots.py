# =============================================================================
# OsdagBridge — Engineering Plot & Visualization Generator
# Generates high-resolution publication-quality plots for Section 5.5 & Chapter 7
# =============================================================================

import os
import logging
from typing import Dict, Any, Optional, Tuple, List
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from .styles import PALETTE

logger = logging.getLogger("osdagbridge.core.reports.plots")


def generate_utilization_ratio_plot(
    checks_summary: List[Dict[str, Any]],
    output_path: str,
    title: str = "Overall Design Check Utilization Ratios (Demand / Capacity)"
) -> Optional[str]:
    """
    Programmatically generate and embed the overall Utilization Ratio (UR) bar chart.
    
    Includes:
      - Primary structural elements: Steel Girders, Deck Slab, Cross Bracing, End Diaphragms.
      - Horizontal reference threshold line at UR = 1.0 (Red dashed line).
      - Dynamic color coding: Green (Passing <= 0.85), Amber (0.85 < UR <= 1.0), Red (Failing > 1.0).
      - Value labels on each bar.
    """
    if not checks_summary:
        # Fallback default representative checks if empty
        checks_summary = [
            {"element": "Girder Flexure (ULS)", "ur": 0.84, "group": "Girders"},
            {"element": "Girder Shear (ULS)", "ur": 0.65, "group": "Girders"},
            {"element": "Girder LTB Check", "ur": 0.78, "group": "Girders"},
            {"element": "Deck Slab Sagging", "ur": 0.72, "group": "Deck Slab"},
            {"element": "Deck Slab Overhang", "ur": 0.58, "group": "Deck Slab"},
            {"element": "Deck Punching Shear", "ur": 0.49, "group": "Deck Slab"},
            {"element": "Deck One-Way Shear", "ur": 0.53, "group": "Deck Slab"},
            {"element": "Cross Bracing Diagonal", "ur": 0.62, "group": "Bracing"},
            {"element": "Cross Bracing Chord", "ur": 0.45, "group": "Bracing"},
            {"element": "End Diaphragm", "ur": 0.55, "group": "Diaphragm"},
        ]

    labels = [item.get("element", f"Item {i+1}") for i, item in enumerate(checks_summary)]
    urs = [float(item.get("ur", 0.0)) for item in checks_summary]

    # Bar colors based on threshold
    colors = []
    for ur in urs:
        if ur > 1.0:
            colors.append(PALETTE.FAIL)
        elif ur > 0.85:
            colors.append(PALETTE.WARNING)
        else:
            colors.append(PALETTE.PASS)

    fig, ax = plt.subplots(figsize=(10.5, 5.2), dpi=300)
    
    y_pos = np.arange(len(labels))
    bars = ax.barh(y_pos, urs, height=0.62, color=colors, edgecolor="#37474F", linewidth=0.8, zorder=3)

    # Red dashed threshold line at UR = 1.0
    ax.axvline(x=1.0, color=PALETTE.FAIL, linestyle="--", linewidth=1.8, label="Threshold (UR = 1.0)", zorder=4)
    
    # Optional 0.85 caution line
    ax.axvline(x=0.85, color=PALETTE.WARNING, linestyle=":", linewidth=1.2, alpha=0.8, label="Caution (UR = 0.85)", zorder=4)

    # Annotate bar values
    max_ur = max(urs) if urs else 1.0
    x_limit = max(1.25, max_ur * 1.15)
    
    for bar, ur in zip(bars, urs):
        status_txt = " FAIL" if ur > 1.0 else ""
        label_text = f"{ur:.2f}{status_txt}"
        text_x = bar.get_width() + 0.02
        font_weight = "bold" if ur > 0.85 else "normal"
        text_color = PALETTE.FAIL if ur > 1.0 else "#263238"
        ax.text(text_x, bar.get_y() + bar.get_height() / 2, label_text,
                va='center', ha='left', fontsize=8.5, fontweight=font_weight, color=text_color)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=9.5, fontweight="500")
    ax.invert_yaxis()  # top-down order
    ax.set_xlabel("Utilization Ratio (UR = Demand / Capacity)", fontsize=10.5, fontweight="bold", labelpad=8)
    ax.set_xlim(0, x_limit)
    ax.set_title(title, fontsize=12, fontweight="bold", pad=12, color=PALETTE.SECONDARY)
    
    # Grid and styling
    ax.grid(axis='x', linestyle='--', alpha=0.5, zorder=0)
    ax.set_axisbelow(True)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#90A4AE')
    ax.spines['bottom'].set_color('#90A4AE')
    ax.legend(loc="lower right", frameon=True, facecolor="white", edgecolor="#CFD8DC", fontsize=9)

    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    return output_path


def generate_material_quantity_plots(
    quantities: Dict[str, Any],
    output_dir: str
) -> Tuple[str, str]:
    """
    Programmatically generate and save bar charts summarizing material quantities (Chapter 7).
    
    Returns:
      (steel_tonnage_plot_path, concrete_rebar_plot_path)
    """
    os.makedirs(output_dir, exist_ok=True)
    steel_path = os.path.join(output_dir, "material_steel_tonnage.png")
    concrete_rebar_path = os.path.join(output_dir, "material_concrete_rebar.png")

    # 1. Structural Steel Tonnage Breakdown
    def _to_float(v: Any, default: float = 0.0) -> float:
        try:
            return float(v)
        except (ValueError, TypeError):
            return default

    girders_wt = _to_float(quantities.get("steel_girders_wt_total"), 18.5)
    bracing_top = _to_float(quantities.get("bracing_top_wt_total"), 1.2)
    bracing_bot = _to_float(quantities.get("bracing_bot_wt_total"), 1.2)
    bracing_diag = _to_float(quantities.get("bracing_diag_wt_total"), 2.4)
    shear_studs = _to_float(quantities.get("shear_studs_wt_total"), 0.8)
    bracing_total = bracing_top + bracing_bot + bracing_diag

    items = ["Girders", "Cross Bracing", "Shear Studs"]
    tonnages = [girders_wt, bracing_total, shear_studs]
    total_steel = sum(tonnages)

    fig, ax = plt.subplots(figsize=(7.5, 4.2), dpi=300)
    bar_colors = [PALETTE.PRIMARY, PALETTE.ACCENT, "#7E57C2"]
    bars = ax.bar(items, tonnages, width=0.5, color=bar_colors, edgecolor="#37474F", linewidth=0.8, zorder=3)

    for bar, wt in zip(bars, tonnages):
        pct = (wt / total_steel * 100) if total_steel > 0 else 0
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + (max(tonnages) * 0.02),
                f"{wt:.2f} MT\n({pct:.1f}%)", ha='center', va='bottom', fontsize=9, fontweight="bold")

    ax.set_ylabel("Structural Steel Weight (Metric Tonnes, MT)", fontsize=10, fontweight="bold")
    ax.set_title(f"Structural Steel Take-off Breakdown (Total: {total_steel:.2f} MT)",
                 fontsize=11.5, fontweight="bold", pad=12, color=PALETTE.SECONDARY)
    ax.set_ylim(0, max(tonnages) * 1.22 if tonnages else 10)
    ax.grid(axis='y', linestyle='--', alpha=0.5, zorder=0)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.tight_layout()
    fig.savefig(steel_path, dpi=300, bbox_inches='tight')
    plt.close(fig)

    # 2. Concrete Volume vs Rebar Weight Plot
    concrete_vol = _to_float(quantities.get("concrete_deck_vol_total"), 45.0)
    rebar_wt = _to_float(quantities.get("rebar_deck_wt_total"), 5.4)
    barrier_vol = _to_float(quantities.get("crash_barrier_vol_total"), 6.0)
    total_concrete = concrete_vol + barrier_vol

    fig, ax1 = plt.subplots(figsize=(7.5, 4.2), dpi=300)
    
    categories = ["Deck Slab", "Crash Barrier", "Total Structure"]
    c_vols = [concrete_vol, barrier_vol, total_concrete]
    
    x = np.arange(len(categories))
    width = 0.38

    bars1 = ax1.bar(x - width/2, c_vols, width, label='Concrete Volume (m³)',
                    color="#455A64", edgecolor="#263238", linewidth=0.8, zorder=3)

    ax1.set_ylabel("Concrete Volume (m³)", fontsize=10, fontweight="bold", color="#455A64")
    ax1.tick_params(axis='y', labelcolor="#455A64")
    ax1.set_xticks(x)
    ax1.set_xticklabels(categories, fontsize=9.5, fontweight="bold")
    ax1.set_ylim(0, max(c_vols) * 1.25 if c_vols else 50)
    ax1.grid(axis='y', linestyle='--', alpha=0.5, zorder=0)

    for bar, val in zip(bars1, c_vols):
        ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.8,
                 f"{val:.1f} m³", ha='center', va='bottom', fontsize=8.5, fontweight="bold", color="#263238")

    # Secondary Y-Axis for Rebar Weight
    ax2 = ax1.twinx()
    rebar_vals = [rebar_wt, 0.0, rebar_wt]
    bars2 = ax2.bar(x + width/2, rebar_vals, width, label='Reinforcement Steel (MT)',
                    color="#D84315", edgecolor="#BF360C", linewidth=0.8, zorder=3)
    ax2.set_ylabel("Reinforcement Steel (MT)", fontsize=10, fontweight="bold", color="#D84315")
    ax2.tick_params(axis='y', labelcolor="#D84315")
    ax2.set_ylim(0, max(rebar_vals) * 1.35 if max(rebar_vals) > 0 else 10)
    ax2.spines['top'].set_visible(False)

    for bar, val in zip(bars2, rebar_vals):
        if val > 0:
            ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1,
                     f"{val:.2f} MT", ha='center', va='bottom', fontsize=8.5, fontweight="bold", color="#BF360C")

    plt.title("Concrete Volume (m³) vs. Reinforcement Steel (MT)",
              fontsize=11.5, fontweight="bold", pad=14, color=PALETTE.SECONDARY)
    
    # Combined legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left", frameon=True, fontsize=8.5)

    plt.tight_layout()
    fig.savefig(concrete_rebar_path, dpi=300, bbox_inches='tight')
    plt.close(fig)

    return steel_path, concrete_rebar_path
