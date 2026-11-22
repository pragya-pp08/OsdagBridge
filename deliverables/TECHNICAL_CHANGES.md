# OsdagBridge LaTeX Report Generator Refactoring & Enhancements
## Technical Changes, Architectural Design & Structural Verification Document

**Project:** FOSSEE Osdag — OsdagBridge Plugin  
**Candidate Name:** Pragya Pandey  
**Submission Category:** Software Development Screening Tasks  
**Target Organization:** FOSSEE, Indian Institute of Technology Bombay (IIT Bombay)  
**Submission Date:** November 2026  
**Repository Branch:** `feature/report-generator-enhancements`

---

## Executive Summary

The OsdagBridge design report generation module converts bridge structural analysis and design outputs into a formal engineering calculation PDF report. The original codebase had several critical formatting, layout, architectural, and visual limitations:
1. Multi-page tables broke across pages without repeated headers (`\endfirsthead`, `\endhead`), causing data illegibility.
2. Negative vertical spacing and non-calibrated geometry margins caused table rows (such as "G4" on Page 30) to bleed directly into the page footer.
3. Chapter 3 merged vehicle live loads and footway loads into an unformatted table lacking parameter and unit columns.
4. Structural demand-to-capacity Utilization Ratios (UR) lacked visual representation and threshold benchmarks.
5. Material take-off quantities (Chapter 7) lacked component-level bar chart visualizations.
6. Formatting, typography, and color rules were hardcoded and scattered across multiple chapter scripts.

This document details the refactoring, engineering implementations, architectural decisions, and testing procedures executed to resolve all six issues.

---

## 1. Centralized Style & Formatting Architecture (`styles.py`)

### Problem
Formatting constants (colors, margins, table padding, array stretches, and font sizes) were scattered across `report_generator.py` and chapter modules (`chap1.py` through `chap9.py`). Making global design adjustments or maintaining consistency was error-prone and tedious. Additionally, column header cells in `build_longtable_header()` were improperly joined with `\\ \hline`, which caused each column title to render on a separate line instead of occupying a single coherent header row.

### Architectural Solution
Created a dedicated module `osdagbridge.core.reports.styles` as the **Single Source of Truth** using immutable Python dataclasses:

```
styles.py
├── ColorPalette (Primary, Secondary, Pass Green, Fail Red, Warning Amber, Accent)
├── GeometryConfig (Paper, margins, header/footer spacing, includehead/includefoot)
├── TableStyleConfig (Colsep, arraystretch, rulewidth, extrarowheight, needspace)
├── build_longtable_header() (Reusable multi-page header generator)
├── build_page_styles() (Calibrated fancyhdr header/footer layouts)
└── enhance_longtables_in_tex() (Automated document-wide table header enhancer)
```

### Key Parameters Configured
- **Document Geometry:** A4 paper with `left=20mm`, `right=20mm`, `top=25mm`, `bottom=28mm`, `headheight=16pt`, `headsep=15pt`, `footskip=18pt`, `includehead`, `includefoot`.
- **Color Palette:**
  - `osdagGreen` (`#91B014`): FOSSEE/Osdag primary brand color.
  - `osdagNavy` (`#1A365D`): Deep navy for headings and titles.
  - `osdagPass` (`#2E7D32`): Forest green for passing structural checks ($\text{UR} \le 1.0$).
  - `osdagWarning` (`#F57C00`): Amber for checks nearing limit ($0.85 < \text{UR} \le 1.0$).
  - `osdagFail` (`#C62828`): Crimson red for failing structural checks ($\text{UR} > 1.0$).
  - `tableHeaderBg` (`#E9ECEF`): Subtle header shading.
- **Header Joining Logic:** Refactored `build_longtable_header` so that header column titles are joined on a single row using `" & ".join(header_rows) + r" \\[4pt]" + "\n\\hline"`. Both initial (`\endfirsthead`) and continuation (`\endhead`) headers render perfectly aligned on a single row.
- **Centralized Status Colors in Chapters:** Replaced scattered hardcoded `\textcolor{red}{...}`, `\textcolor{green}{...}`, and `\textcolor{black}{...}` calls in `chap4.py`, `chap5.py`, and `chap8.py` with semantically unified commands: `\textcolor{osdagPass}{\textbf{PASS}}`, `\textcolor{osdagFail}{\textbf{FAIL}}`, and `\textcolor{osdagWarning}{\textbf{WARNING}}`.

---

## 2. Repeated Table Headers Across Page Breaks & Table Width Calibration (Issue 1 & Issue 3)

### Problem
1. Standard PyLaTeX tables or manual `longtable` blocks split across pages without `\endfirsthead` and `\endhead`. Consequently, when tables spanned multiple pages, subsequent pages displayed raw rows with no column context.
2. Long tables with many columns (e.g., Table 3.3 and Table 3.4) exceeded the printable width (170 mm on A4 with 20 mm margins), causing text and vertical rules to clip into the right page margin.

### Implementation
1. Implemented `build_longtable_header()` in `styles.py`:
   - Emits `\caption{...} \label{...} \\ \hline` followed by the single-row column headers and `\endfirsthead`.
   - Emits continuation header: `\multicolumn{N}{c}{\textit{Table \thetable{} (continued from previous page)}} \\ \hline` followed by the repeated column header row and `\endhead`.
   - Emits bottom continuation marker: `\multicolumn{N}{r}{\textit{Continued on next page...}} \\ \endfoot`.
   - Emits terminating rule: `\hline \endlastfoot`.
2. Implemented `enhance_longtables_in_tex(full_tex)`:
   - A document-level enhancer that scans all `\begin{longtable}` environments lacking `\endfirsthead` and injects complete two-tier header and footer structures.
   - Applied across all 29 tables in Chapter 5, Chapter 3, and Chapter 7.
3. **Table Width & Margin Calibration:**
   - In Table 3.3 and Table 3.4, set local `\setlength{\tabcolsep}{3.5pt}` and calibrated explicit column widths (`p{2.6cm}`, `p{3.2cm}`, `p{2.2cm}`, `p{2.2cm}`, `p{2.2cm}`, `p{1.9cm}` summing to ~14.3 cm) ensuring comfortable containment within the 17.0 cm body margin.

---

## 3. Layout, Footer Overlap, and Vertical Spacing Fixes (Issue 2)

### Problem
On Page 30 and similar check sections, girder rows (e.g., "G4") bled directly into the horizontal green rule and footer text.

### Root Cause Analysis
1. `\geometry{margin=1in}` lacked explicit `headheight`, `headsep`, `footskip`, and `includefoot` declarations.
2. In `fancyhdr`, `\renewcommand{\footrule}` contained aggressive upward negative vertical skips (`\vspace{-20pt}` and `\vspace{-8pt}`), which physically pulled the footer rule upward into the body text area.
3. Insufficient bottom threshold buffers allowed long tables to break with only one trailing row before the footer.

### Resolution
1. Configured `GeometryConfig` with explicit `bottom=28mm`, `footskip=18pt`, `includehead=True`, and `includefoot=True`.
2. Replaced the negative `\vspace` in `\footrule` with a calibrated non-negative spacing (`\vspace{0pt}` and `\vspace{4pt}`).
3. Added `\BeforeBeginEnvironment{longtable}{\needspace{4\baselineskip}}` to guarantee that tables do not start unless at least 4 text lines of headroom exist.
4. Added `\clubpenalty=10000` and `\widowpenalty=10000` to suppress orphan/widow table lines.
5. Injected clean `\clearpage` breaks before major design check subsections (Section 5.3 Deck Slab, Section 5.4 Cross Bracing, Section 5.5 Overall Summary) to ensure clean component grouping.

---

## 4. Chapter 3 Load Table Refactoring & Fallback Elimination (Issue 3)

### Problem
1. Vehicular live loads and footway loads were merged into a single table without clear unit columns, impact factor breakdowns, or braking force parameters.
2. Centrifugal force was hardcoded to `0.00` without straight-track engineering justification.
3. Global braking force fell back to a hardcoded `200.0` kN on missing data.
4. Number of lanes fell back to a hardcoded `2` lanes.
5. Footway table hardcoded intensity `4.000`, railing `1.500`, and kerb `4.000` regardless of whether footpaths were enabled in the bridge model.

### Resolution & Engineering Tracing
Refactored `chap3.py` to eliminate all hardcoded fallbacks and produce two distinct, clearly formatted tables:
1. **Table 3.3: Vehicle Live Loads (LL) Parameters and Impact Factors**:
   - Dynamically populated strictly from UI loading tab selections (`KEY_LL_IRC_CLASS_A`, `KEY_LL_IRC_70R_WHEELED`, `KEY_LL_IRC_70R_TRACKED`, `KEY_LL_IRC_AA_*`, `KEY_LL_IRC_CLASS_SV`, etc.).
   - Explicit columns: `Vehicle Class`, `Configuration / Type`, `Impact Factor (1+IF)` (calculated per IRC 6:2017 Cl. 208), `Braking Force (kN)` (calculated per IRC 6:2017 Cl. 211), `Centrifugal Force (kN)`, and `Status`.
   - **Braking Force:** Dynamically calculated based on span length and lane count per IRC 6 Cl. 211 ($200\text{ kN}$ first lane + $100\text{ kN}$ per additional lane). If required bridge geometry is absent, displays honest `"N/A"` instead of a misleading fallback.
   - **Centrifugal Force:** Explicitly rendered as `"0.00 (Straight)"` citing IRC 6:2017 Cl. 212 ($R = \infty$), clarifying that horizontal curvature effects are zero for straight-alignment bridges.
   - **Carriageway / Lane Count:** Dynamically resolved from `KEY_WC_LD_LANE_TABLE_COUNT` or standard carriageway width per IRC 6:2017 Table 6. Renders `"N/A"` if undefined.
2. **Table 3.4: Footway and Pedestrian Live Loads**:
   - Distinct table detailing `Footway Live Load Intensity`, `Pedestrian Railing Horizontal Load`, and `Kerb / Verge Vertical Surcharge`.
   - Live load intensities are dynamically conditioned on whether footpaths, railings, or kerbs are active in the bridge configuration. When configured, values cite standard IRC 6 clauses (Cl. 206.1, 206.3, 206.2). If unconfigured or omitted, displayed honestly as `"N/A"` or `"None configured"`.
   - Dedicated unit columns (`kN/m^2`, `kN/m`) and IRC standard clause references.

---

## 5. Utilization Ratio Summary Visualizations & Table 5.22 Parity (Issue 4)

### Problem
1. `report_generator.py` previously called `generate_utilization_ratio_plot([], ...)` passing an empty list, causing `plots.py` to substitute hardcoded demo values (0.84, 0.65, etc.). This caused dangerous discrepancies where the chart showed numbers contradicting the actual design results.
2. The chart was oriented horizontally instead of vertically.

### Implementation & Single Source of Truth
1. **Unified Extraction Engine (`extract_design_checks_summary`):**
   - Implemented `extract_design_checks_summary(bridge)` in `chap5.py` as the **Single Source of Truth** for both Table 5.22 and the UR summary plot.
   - Extracts actual design demands, capacities, and utilization ratios directly from the `ReportDataBridge` instance for all primary bridge components:
     - Girder Flexure (ULS)
     - Girder Shear (ULS)
     - Girder Lateral Torsional Buckling (LTB)
     - Concrete Deck Mid-Span Sagging Moment
     - Concrete Deck Cantilever Overhang Moment
     - Concrete Deck Punching Shear
     - Concrete Deck Transverse One-Way Shear
     - Cross Bracing Chords & Diagonals (Tension / Compression)
     - End Diaphragm Framing & Connections
   - `report_generator.py` now resolves `checks_summary` from this engine before plotting, guaranteeing **100% numerical identity** between Table 5.22 and Figure 5.1.
2. **Honest Data Representation:**
   - Removed all hardcoded fallback values (e.g. 0.84, 0.65) from `plots.py`.
   - If design checks are missing or unavailable, the chart renders an honest "No Utilization Data Available / N/A" watermark.
3. **Plot Specifications (`plots.py`):**
   - **Orientation:** Vertical bar chart (`ax.bar`) with categorized components along the X-axis.
   - **Y-Axis:** `Utilization Ratio (UR = Demand / Capacity)`.
   - **Threshold Reference Line:** Distinct horizontal red dashed line at $\text{UR} = 1.0$ via `ax.axhline(1.0, color='red', linestyle='--', linewidth=1.5, label='Threshold (UR = 1.0)')`.
   - **Caution Reference Line:** Dotted amber line at $\text{UR} = 0.85$ via `ax.axhline(0.85, color=PALETTE.WARNING, linestyle=':', linewidth=1.2)`.
   - **Dynamic Bar Coloring:**
     - Green (`#2E7D32`): Passing and efficient ($\text{UR} \le 0.85$).
     - Amber (`#F57C00`): Acceptable but near capacity ($0.85 < \text{UR} \le 1.0$).
     - Crimson Red (`#C62828`): Overstressed / failing ($\text{UR} > 1.0$).
   - **Label Formatting:** X-axis labels rotated $40^\circ$ with right alignment, padded layout, and clean value badges directly above each vertical bar.
   - **Placement:** Dynamically embedded into **Section 5.5 (Overall Design Check Summary)** directly before Table 5.22.

---

## 6. Material Quantity Bar Charts & Component Corrections (Issue 5)

### Problem
1. The structural steel quantity chart previously included shear studs instead of End Diaphragms.
2. When component quantities were missing, `plots.py` substituted default quantities (such as 18.5 MT, 45.0 $\text{m}^3$), which fabricated engineering take-offs.

### Implementation
1. **Component Category Alignment:**
   - Updated structural steel categories strictly to:
     - **Girders** (Top flange, bottom flange, web, and stiffeners)
     - **Cross Bracing** (Top chords, bottom chords, and diagonal braces across all internal bays)
     - **End Diaphragms** (Transverse support beams and bracing framing across support lines)
   - Updated `boq_generator.py` to calculate End Diaphragms (item 2(d)) based on girder count, spacing, and diaphragm member weight per meter.
   - Ensured perfect synchronization between Chapter 7 Table 7.1 and Figure 7.1.
2. **Honest Material Representation:**
   - Completely eliminated all hardcoded fallback tonnages.
   - If a quantity is unavailable, it is represented as 0.00 MT / N/A.
3. **Visualizations Generated (`plots.py`):**
   - **Figure 7.1: Structural Steel Quantity Breakdown (MT)**:
     - Vertical bar chart representing Girders, Cross Bracing, and End Diaphragms.
     - Exact tonnage badge and percentage share of total structural steel displayed above each bar.
   - **Figure 7.2: Concrete Volume ($\text{m}^3$) vs. Reinforcement Steel Weight (MT)**:
     - Grouped bar chart comparing Concrete volumes (Deck Slab, Kerbs/Barriers, Total Structure) against Rebar weight (MT).
4. **Placement:** Embedded into Chapter 7 (**Material Take-off & Quantity Summary**) via PyLaTeX Figure environment (`fig:material_steel` and `fig:material_concrete_rebar`).

---

## 7. Report Options Compliance (`include_pdf`) & Portability

### Problem
1. `ReportOptions.include_pdf` was ignored by `report_generator.py`; the compiler was invoked unconditionally even when the caller explicitly requested TeX-only generation (`include_pdf=False`).
2. Script utilities contained hardcoded machine-specific drive paths (`D:\...`).

### Resolution
1. **Respect `include_pdf`:**
   - In `report_generator.py`, wrapped PDF compilation in `if payload.options.include_pdf and compiler:`.
   - If `include_pdf=False` or if `pdflatex` is not installed on the system, the generator cleanly returns `ReportResult(pdf_path=None, tex_path=tex_path)` without erroring out.
2. **Path Portability:**
   - Refactored `tests/generate_deliverables.py` and test utilities to dynamically resolve workspace roots using `pathlib.Path(__file__).resolve().parents[...]`, completely removing hardcoded drive letters (`D:\`).
3. **Lazy FEM Imports:**
   - In `osdagbridge.core.bridge_types.plate_girder.results_data`, wrapped `import openseespy.opensees as ops` in a try/except block. This allows report compilation on environments without the heavy OpenSees C++ solver binary.

---

## 8. Automated Verification & Test Suite

An expanded automated regression and unit test suite was developed at `E:\OsdagBridge\tests\test_report_pipeline.py` and validated with `pytest`:

```
============================= test session starts =============================
platform win32 -- Python 3.14.3, pytest-9.2.0, pluggy-1.7.0 -- E:\OsdagBridge\.venv\Scripts\python.exe
rootdir: E:\OsdagBridge
configfile: pyproject.toml
collected 7 items

tests/test_report_pipeline.py::test_styles_engine_and_headers PASSED     [ 14%]
tests/test_report_pipeline.py::test_plot_generation PASSED               [ 28%]
tests/test_report_pipeline.py::test_plot_empty_data_honest PASSED        [ 42%]
tests/test_report_pipeline.py::test_chap3_loads_and_fallbacks PASSED     [ 57%]
tests/test_report_pipeline.py::test_chap5_table_and_chart_parity PASSED  [ 71%]
tests/test_report_pipeline.py::test_report_options_include_pdf_false PASSED [ 85%]
tests/test_report_pipeline.py::test_full_report_tex_pipeline PASSED      [100%]

======================== 7 passed, 1 warning in 24.81s ========================
```

### Test Coverage Breakdown:
1. `test_styles_engine_and_headers`: Validates `build_longtable_header` column joining with `" & "`, `\endfirsthead`, and `\endhead` generation.
2. `test_plot_generation`: Validates UR plot creation (vertical orientation, red dashed line at 1.0, and 300 DPI output) and Material Quantity plots (Girders, Cross Bracing, End Diaphragms).
3. `test_plot_empty_data_honest`: Validates that empty or missing datasets render an honest `"N/A"` watermark without substituting fabricated fallback numbers.
4. `test_chap3_loads_and_fallbacks`: Validates dynamic lane counts, dynamic braking forces per IRC 6 Cl. 211, explicit `"0.00 (Straight)"` centrifugal status, and calibrated table column widths.
5. `test_chap5_table_and_chart_parity`: Validates that `extract_design_checks_summary(bridge)` feeds both Table 5.22 and the UR summary chart with 100% numerical parity.
6. `test_report_options_include_pdf_false`: Validates that `include_pdf=False` cleanly returns `ReportResult(pdf_path=None, ...)` without attempting PDF compilation.
7. `test_full_report_tex_pipeline`: Validates end-to-end report generation across all 9 chapters, verifying that `enhance_longtables_in_tex` injects repeated headers across all multi-page tables.

---

## 9. Summary of Altered Files

| File Path | Nature of Alteration | Key Enhancements |
| :--- | :--- | :--- |
| `src/osdagbridge/core/reports/styles.py` | **NEW FILE** | Single source of truth for color palette, geometry, table padding, single-row `build_longtable_header`, and `enhance_longtables_in_tex`. |
| `src/osdagbridge/core/reports/plots.py` | **NEW FILE** | Programmatic Matplotlib 300 DPI chart generation for vertical UR summary (`axhline(1.0, color='red', linestyle='--')`) and Material Quantities (Girders, Cross Bracing, End Diaphragms). Honest N/A handling. |
| `src/osdagbridge/core/reports/chap3.py` | **REFACTORED** | Separated vehicle live loads and footway loads; removed hardcoded fallbacks; added dynamic lane/braking force logic; calibrated table column widths (`\tabcolsep{3.5pt}`) to prevent margin overflow. |
| `src/osdagbridge/core/reports/chap4.py` | **REFACTORED** | Centralized check status colors to `\textcolor{osdagPass}{...}`, `\textcolor{osdagFail}{...}`, and `\textcolor{osdagWarning}{...}`. |
| `src/osdagbridge/core/reports/chap5.py` | **REFACTORED** | Created `extract_design_checks_summary(bridge)` as single source of truth for Table 5.22 and UR chart; centralized check status colors. |
| `src/osdagbridge/core/reports/chap7.py` | **REFACTORED** | Embedded Structural Steel (Girders, Cross Bracing, End Diaphragms) and Concrete vs Rebar figures; updated BOQ table with End Diaphragm line item. |
| `src/osdagbridge/core/reports/chap8.py` | **REFACTORED** | Centralized check status colors and unified styling. |
| `src/osdagbridge/core/boq/boq_generator.py` | **ENHANCED** | Added End Diaphragm calculation item 2(d) to material quantity take-off. |
| `src/osdagbridge/core/reports/report_generator.py` | **REFACTORED** | Wired `styles.py` into preamble; integrated plot generation pipeline with actual bridge check summary; respected `include_pdf=False`; invoked document-wide table header enhancer. |
| `src/osdagbridge/core/bridge_types/plate_girder/results_data.py` | **BUG FIX** | Made `openseespy` import lazy/graceful to prevent report generator crashes on machines without OpenSees. |
| `tests/test_report_pipeline.py` | **TEST SUITE**| Pytest automated end-to-end pipeline verification test suite (7 comprehensive unit/regression tests). |
| `deliverables/Report_After.tex` | **DELIVERABLE** | Complete, compiled, refactored 9-chapter design report source (101 KB). |
| `deliverables/assets/` | **DELIVERABLE** | High-resolution plot assets (`utilization_ratio_summary.png`, `material_steel_tonnage.png`, `material_concrete_rebar.png`). |
