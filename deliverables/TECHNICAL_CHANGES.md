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
Formatting constants (colors, margins, table padding, array stretches, and font sizes) were scattered across `report_generator.py` and chapter modules (`chap1.py` through `chap9.py`). Making global design adjustments or maintaining consistency was error-prone and tedious.

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

---

## 2. Repeated Table Headers Across Page Breaks (Issue 1)

### Problem
Standard PyLaTeX tables or manual `longtable` blocks split across pages without `\endfirsthead` and `\endhead`. Consequently, when tables spanned multiple pages, subsequent pages displayed raw rows with no column context.

### Implementation
1. Implemented `build_longtable_header()` in `styles.py`:
   - Emits `\caption{...} \label{...} \\ \hline` followed by the initial column header row and `\endfirsthead`.
   - Emits a continuation header: `\multicolumn{N}{c}{\textit{Table \thetable{} (continued from previous page)}} \\ \hline` followed by the repeated column header row and `\endhead`.
   - Emits a bottom continuation marker: `\multicolumn{N}{r}{\textit{Continued on next page...}} \\ \endfoot`.
   - Emits a terminating rule: `\hline \endlastfoot`.
2. Implemented `enhance_longtables_in_tex(full_tex)`:
   - A document-level enhancer that scans all `\begin{longtable}` environments lacking `\endfirsthead` and injects complete two-tier header and footer structures.
   - Applied across all 29 tables in Chapter 5, Chapter 3, and Chapter 7.

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

## 4. Chapter 3 Load Table Refactoring (Issue 3)

### Problem
Vehicular live loads and footway loads were merged into a single table without clear unit columns, impact factor breakdowns, or braking force parameters.

### Resolution
Refactored `chap3.py` to produce two distinct, clearly formatted tables:
1. **Table 3.3: Vehicle Live Loads (LL) Parameters and Impact Factors**:
   - Dynamically populated strictly from UI loading tab selections (`KEY_LL_IRC_CLASS_A`, `KEY_LL_IRC_70R_WHEELED`, `KEY_LL_IRC_70R_TRACKED`, `KEY_LL_IRC_AA_*`, `KEY_LL_IRC_CLASS_SV`, etc.).
   - Explicit columns: `Vehicle Class`, `Configuration / Type`, `Impact Factor (1+IF)` (calculated per IRC 6:2017 Cl. 208), `Braking Force (kN)` (calculated per IRC 6:2017 Cl. 211), `Centrifugal Force (kN)`, and `Status`.
2. **Table 3.4: Footway and Pedestrian Live Loads**:
   - Distinct table detailing `Footway Live Load Intensity` ($4.000\text{ kN/m}^2$ or $5.000\text{ kN/m}^2$ per IRC 6 Cl. 206.1), `Pedestrian Railing Horizontal Load` ($1.500\text{ kN/m}$ per Cl. 206.3), and `Kerb / Verge Vertical Surcharge` ($4.000\text{ kN/m}^2$ per Cl. 206.2).
   - Dedicated unit columns and standard clause references.

---

## 5. Utilization Ratio Summary Visualizations (Issue 4)

### Implementation
Created `osdagbridge.core.reports.plots`:
- **Function:** `generate_utilization_ratio_plot(checks_summary, output_path)`
- **Plot Specifications:**
  - Y-Axis: Categorized structural components (Girder Flexure ULS, Girder Shear ULS, Girder LTB, Deck Mid-Span Sagging, Deck Overhang, Deck Punching Shear, Deck One-Way Shear, Cross Bracing Tension/Compression, End Diaphragms).
  - X-Axis: Utilization Ratio ($\text{UR} = \text{Demand} / \text{Capacity}$).
  - **Threshold Reference Line:** Distinct red dashed vertical line at $\text{UR} = 1.0$ labeled `Threshold (UR = 1.0)`.
  - **Caution Reference Line:** Dotted amber line at $\text{UR} = 0.85$.
  - **Dynamic Bar Coloring:**
    - Green (`#2E7D32`): Passing and efficient ($\text{UR} \le 0.85$).
    - Amber (`#F57C00`): Acceptable but near capacity ($0.85 < \text{UR} \le 1.0$).
    - Crimson Red (`#C62828`): Overstressed / failing ($\text{UR} > 1.0$).
  - **Placement:** Dynamically embedded into **Section 5.5 (Overall Design Check Summary)** directly before Table 5.22.

---

## 6. Material Quantity Bar Charts (Issue 5)

### Implementation
In `osdagbridge.core.reports.plots`:
- **Function:** `generate_material_quantity_plots(quantities, output_dir)`
- **Visualizations Generated:**
  1. **Figure 7.1: Structural Steel Take-off Breakdown (MT)**:
     - Component breakdown: Main Girders, Cross Bracing Chords & Diagonals, Shear Stud Connectors.
     - Tonnage labeled on each bar with percentage share of total structural steel.
  2. **Figure 7.2: Concrete Volume ($\text{m}^3$) vs. Reinforcement Steel Weight (MT)**:
     - Dual-axis grouped bar chart comparing Deck Slab concrete volume, Crash Barrier concrete volume, and Total Structure volume against Rebar tonnage (MT).
- **Placement:** Embedded into Chapter 7 (**Material Take-off & Quantity Summary**) via PyLaTeX Figure environment (`fig:material_steel` and `fig:material_concrete_rebar`).

---

## 7. Additional Engineering Bug Fix: Lazy OpenSees Import

During verification, an undocumented runtime crash was discovered:
- **Location:** `osdagbridge.core.bridge_types.plate_girder.results_data` line 17.
- **Defect:** A hard top-level `import openseespy.opensees as ops` caused all report generation attempts to fail with `ModuleNotFoundError: No module named 'openseespy'` if the OpenSees binary was not locally installed, even though report generation only required dictionary formatting helpers (`_extract_osdag_summary`).
- **Fix:** Converted `openseespy` to a lazy, graceful import:
  ```python
  try:
      import openseespy.opensees as ops
  except ImportError:
      ops = None
  ```
- **Impact:** Decoupled post-processing report compilation from the raw FEM solver binary, increasing robustness and portability.

---

## 8. Verification & Test Suite

An automated test suite was developed at `E:\OsdagBridge\tests\test_report_pipeline.py` and validated with `pytest`:

```
============================= test session starts =============================
platform win32 -- Python 3.14.3, pytest-9.2.0, pluggy-1.7.0
rootdir: E:\OsdagBridge

tests/test_report_pipeline.py::test_styles_engine PASSED               [ 33%]
tests/test_report_pipeline.py::test_plot_generation PASSED            [ 66%]
tests/test_report_pipeline.py::test_full_report_tex_pipeline PASSED   [100%]

============================== 3 passed in 3.47s ==============================
```

All 3 automated tests passed with 100% assertions satisfied.

---

## 9. Summary of Altered Files

| File Path | Nature of Alteration | Key Enhancements |
| :--- | :--- | :--- |
| `src/osdagbridge/core/reports/styles.py` | **NEW FILE** | Single source of truth for color palette, geometry, table padding, `build_longtable_header`, and `enhance_longtables_in_tex`. |
| `src/osdagbridge/core/reports/plots.py` | **NEW FILE** | Programmatic Matplotlib 300 DPI chart generation for UR summary and Material Quantities (Steel MT, Concrete $\text{m}^3$, Rebar MT). |
| `src/osdagbridge/core/reports/chap3.py` | **REFACTORED** | Separated vehicle live loads and footway loads into distinct tables with unit columns and repeated `longtable` headers. |
| `src/osdagbridge/core/reports/chap5.py` | **REFACTORED** | Injected repeated headers across all 29 tables; embedded UR bar chart and threshold description into Section 5.5. |
| `src/osdagbridge/core/reports/chap7.py` | **REFACTORED** | Embedded Structural Steel and Concrete vs Rebar figures; updated BOM table with repeated headers. |
| `src/osdagbridge/core/reports/report_generator.py` | **REFACTORED** | Wired `styles.py` into preamble; integrated plot generation pipeline; passed `fig_paths` to Chapters 5 & 7; invoked document-wide table header enhancer. |
| `src/osdagbridge/core/bridge_types/plate_girder/results_data.py` | **BUG FIX** | Made `openseespy` import lazy/graceful to prevent report generator crashes on machines without OpenSees. |
| `tests/test_report_pipeline.py` | **NEW TEST SUITE**| Pytest automated end-to-end pipeline verification test suite. |
| `deliverables/Report_After.tex` | **DELIVERABLE** | Complete, compiled, refactored 9-chapter design report source (101 KB). |
| `deliverables/assets/` | **DELIVERABLE** | High-resolution plot assets (`utilization_ratio_summary.png`, `material_steel_tonnage.png`, `material_concrete_rebar.png`). |
