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
      - Primary structural elements: Steel Girders, Concrete Deck Slab, Cross Bracing, End Diaphragms.
      - Vertical bars with Y-axis representing Utilization Ratio (UR = Demand / Capacity).
      - Horizontal reference threshold line at UR = 1.0 (Red dashed line: axhline).
      - Dynamic color coding: Green (Passing <= 0.85), Amber (0.85 < UR <= 1.0), Red (Failing > 1.0).
      - Non-overlapping, readable labels with clear orientation.
      - Honest representation: Missing/unavailable values are marked N/A; never fabricated.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Filter out entries and handle empty/missing data honestly
    valid_items = []
    if checks_summary:
        for item in checks_summary:
            el_name = item.get("element", "Unknown")
            ur_val = item.get("ur")
            if ur_val is not None:
                try:
                    f_val = float(ur_val)
                    valid_items.append((el_name, f_val, item.get("group", "")))
                except (ValueError, TypeError):
                    valid_items.append((el_name, None, item.get("group", "")))
            else:
                valid_items.append((el_name, None, item.get("group", "")))

    fig, ax = plt.subplots(figsize=(11.0, 5.5), dpi=300)

    # If completely empty, render an honest empty state with threshold line
    if not valid_items or all(v[1] is None for v in valid_items):
        ax.axhline(1.0, color='red', linestyle='--', linewidth=1.8, label="Threshold (UR = 1.0)")
        ax.set_ylim(0, 1.3)
        ax.set_xlim(-0.5, 3.5)
        ax.set_ylabel("Utilization Ratio (UR = Demand / Capacity)", fontsize=10.5, fontweight="bold")
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12, color=PALETTE.SECONDARY)
        ax.text(1.5, 0.5, "Design Check Data Not Available (N/A)\n(Run Bridge Analysis to compute UR)",
                ha='center', va='center', fontsize=11, fontweight="bold", color="#757575",
                bbox=dict(boxstyle='round,pad=0.8', facecolor='#F5F5F5', edgecolor='#BDBDBD'))
        ax.legend(loc="upper right", frameon=True, facecolor="white", edgecolor="#CFD8DC", fontsize=9)
        plt.tight_layout()
        fig.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close(fig)
        return output_path

    # Extract labels and numeric URs for elements
    labels = [v[0] for v in valid_items]
    numeric_urs = [v[1] if v[1] is not None else 0.0 for v in valid_items]
    has_ur = [v[1] is not None for v in valid_items]

    # Bar colors based on threshold
    colors = []
    for ur, exists in zip(numeric_urs, has_ur):
        if not exists:
            colors.append("#CFD8DC")  # Grey for N/A
        elif ur > 1.0:
            colors.append(PALETTE.FAIL)
        elif ur > 0.85:
            colors.append(PALETTE.WARNING)
        else:
            colors.append(PALETTE.PASS)

    x_pos = np.arange(len(labels))
    bars = ax.bar(x_pos, numeric_urs, width=0.55, color=colors, edgecolor="#37474F", linewidth=0.8, zorder=3)

    # Red dashed horizontal threshold line at UR = 1.0
    ax.axhline(1.0, color='red', linestyle='--', linewidth=1.8, label="Threshold (UR = 1.0)", zorder=4)
    
    # Optional 0.85 caution line
    ax.axhline(0.85, color=PALETTE.WARNING, linestyle=":", linewidth=1.2, alpha=0.8, label="Caution (UR = 0.85)", zorder=4)

    # Annotate bar values on top of vertical bars
    max_ur = max([u for u, e in zip(numeric_urs, has_ur) if e] or [1.0])
    y_limit = max(1.25, max_ur * 1.18)

    for i, (bar, ur, exists) in enumerate(zip(bars, numeric_urs, has_ur)):
        if exists:
            status_txt = "\nFAIL" if ur > 1.0 else ""
            label_text = f"{ur:.2f}{status_txt}"
            font_weight = "bold" if ur > 0.85 else "normal"
            text_color = PALETTE.FAIL if ur > 1.0 else "#263238"
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.02, label_text,
                    va='bottom', ha='center', fontsize=8.0, fontweight=font_weight, color=text_color)
        else:
            ax.text(bar.get_x() + bar.get_width() / 2, 0.03, "N/A",
                    va='bottom', ha='center', fontsize=8.0, fontweight="bold", color="#757575")

    ax.set_xticks(x_pos)
    ax.set_xticklabels(labels, fontsize=8.5, fontweight="500", rotation=40, ha='right')
    ax.set_ylabel("Utilization Ratio (UR = Demand / Capacity)", fontsize=10.5, fontweight="bold", labelpad=8)
    ax.set_ylim(0, y_limit)
    ax.set_title(title, fontsize=12, fontweight="bold", pad=12, color=PALETTE.SECONDARY)
    
    # Grid and styling
    ax.grid(axis='y', linestyle='--', alpha=0.5, zorder=0)
    ax.set_axisbelow(True)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#90A4AE')
    ax.spines['bottom'].set_color('#90A4AE')
    ax.legend(loc="upper right", frameon=True, facecolor="white", edgecolor="#CFD8DC", fontsize=9)

    plt.tight_layout()
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

    def _to_float(v: Any, default: float = 0.0) -> float:
        if v is None:
            return default
        try:
            val = float(str(v).replace("MT", "").replace("m³", "").strip())
            return val
        except (ValueError, TypeError):
            return default

    # 1. Structural Steel Tonnage Breakdown:
    # Categories: Girders, Cross Bracing, End Diaphragms (per project requirements)
    girders_wt = _to_float(quantities.get("steel_girders_wt_total"), 0.0)
    
    # Cross bracing total (either pre-aggregated or sum of chord + diagonal components)
    bracing_total = _to_float(quantities.get("steel_bracing_wt_total"), None)
    if bracing_total is None or bracing_total == 0.0:
        bracing_top = _to_float(quantities.get("bracing_top_wt_total"), 0.0)
        bracing_bot = _to_float(quantities.get("bracing_bot_wt_total"), 0.0)
        bracing_diag = _to_float(quantities.get("bracing_diag_wt_total"), 0.0)
        bracing_total = bracing_top + bracing_bot + bracing_diag

    end_diaphragm_wt = _to_float(quantities.get("end_diaphragm_wt_total"), 0.0)

    items = ["Girders", "Cross Bracing", "End Diaphragms"]
    tonnages = [girders_wt, bracing_total, end_diaphragm_wt]
    total_steel = sum(tonnages)

    fig, ax = plt.subplots(figsize=(7.5, 4.4), dpi=300)
    bar_colors = [PALETTE.PRIMARY, PALETTE.ACCENT, "#7E57C2"]
    bars = ax.bar(items, tonnages, width=0.48, color=bar_colors, edgecolor="#37474F", linewidth=0.8, zorder=3)

    for bar, wt in zip(bars, tonnages):
        pct = (wt / total_steel * 100) if total_steel > 0 else 0
        h_offset = (max(tonnages) * 0.03) if max(tonnages) > 0 else 0.1
        label_text = f"{wt:.2f} MT\n({pct:.1f}%)" if wt > 0 else "N/A / 0.00 MT"
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + h_offset,
                label_text, ha='center', va='bottom', fontsize=8.5, fontweight="bold")

    ax.set_ylabel("Structural Steel Weight (Metric Tonnes, MT)", fontsize=10, fontweight="bold")
    ax.set_title(f"Structural Steel Take-off Breakdown (Total: {total_steel:.2f} MT)",
                 fontsize=11.5, fontweight="bold", pad=12, color=PALETTE.SECONDARY)
    ax.set_ylim(0, max(tonnages) * 1.25 if max(tonnages) > 0 else 1.0)
    ax.grid(axis='y', linestyle='--', alpha=0.5, zorder=0)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.tight_layout()
    fig.savefig(steel_path, dpi=300, bbox_inches='tight')
    plt.close(fig)

    # 2. Concrete Volume vs Rebar Weight Plot
    concrete_vol = _to_float(quantities.get("concrete_deck_vol_total"), 0.0)
    rebar_wt = _to_float(quantities.get("rebar_deck_wt_total"), 0.0)
    barrier_vol = _to_float(quantities.get("crash_barrier_vol_total"), 0.0)
    total_concrete = concrete_vol + barrier_vol

    fig, ax1 = plt.subplots(figsize=(7.5, 4.4), dpi=300)
    
    categories = ["Deck Slab", "Crash Barrier", "Total Structure"]
    c_vols = [concrete_vol, barrier_vol, total_concrete]
    
    x = np.arange(len(categories))
    width = 0.36

    bars1 = ax1.bar(x - width/2, c_vols, width, label='Concrete Volume (m³)',
                    color="#455A64", edgecolor="#263238", linewidth=0.8, zorder=3)

    ax1.set_ylabel("Concrete Volume (m³)", fontsize=10, fontweight="bold", color="#455A64")
    ax1.tick_params(axis='y', labelcolor="#455A64")
    ax1.set_xticks(x)
    ax1.set_xticklabels(categories, fontsize=9.5, fontweight="bold")
    ax1.set_ylim(0, max(c_vols) * 1.25 if max(c_vols) > 0 else 1.0)
    ax1.grid(axis='y', linestyle='--', alpha=0.5, zorder=0)

    for bar, val in zip(bars1, c_vols):
        h_offset = 0.8 if max(c_vols) > 10 else 0.05
        ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + h_offset,
                 f"{val:.1f} m³", ha='center', va='bottom', fontsize=8.5, fontweight="bold", color="#263238")

    # Secondary Y-Axis for Rebar Weight
    ax2 = ax1.twinx()
    rebar_vals = [rebar_wt, 0.0, rebar_wt]
    bars2 = ax2.bar(x + width/2, rebar_vals, width, label='Reinforcement Steel (MT)',
                    color="#D84315", edgecolor="#BF360C", linewidth=0.8, zorder=3)
    ax2.set_ylabel("Reinforcement Steel (MT)", fontsize=10, fontweight="bold", color="#D84315")
    ax2.tick_params(axis='y', labelcolor="#D84315")
    ax2.set_ylim(0, max(rebar_vals) * 1.35 if max(rebar_vals) > 0 else 1.0)
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
