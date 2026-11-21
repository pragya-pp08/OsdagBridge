# OsdagBridge Software Testing, Functional Verification & Issue Reporting
## Screening Task Deliverable: Software Development / Quality Assurance

**Project:** FOSSEE Osdag — OsdagBridge Plugin  
**Candidate Name:** Pragya Pandey  
**Submission Category:** Area of Interest: Software Development  
**Target Organization:** FOSSEE, Indian Institute of Technology Bombay (IIT Bombay)  
**Submission Date:** November 2026  
**Repository Branch:** `feature/report-generator-enhancements`

---

## 1. Overview & Testing Strategy

This report constitutes the second screening task deliverable under the **Software Development** category for the FOSSEE Osdag Winter Internship 2026. 

Our testing strategy combined:
1. **Automated Unit & Regression Testing:** Created test suites under `tests/` leveraging `pytest` for headless continuous integration.
2. **Boundary & Edge-Case Analysis:** Evaluating numerical stability across edge-case spans ($L \le 0$, extreme aspect ratios, minimum/maximum temperature limits).
3. **Module Decoupling & Import Fault Injection:** Analyzing runtime dependencies to eliminate unnecessary hard crashes.
4. **Visual & Layout Inspection:** Auditing compiled LaTeX reports for typography, margin collisions, and pagination integrity.

---

## 2. Automated Test Suite (`tests/test_report_pipeline.py`)

An automated test suite was developed and executed on the virtual environment:

```python
# test_styles_engine: Validates geometry, color definitions, and table padding
def test_styles_engine(): ...

# test_plot_generation: Validates 300 DPI image generation for UR and BOM charts
def test_plot_generation(tmp_path): ...

# test_full_report_tex_pipeline: Validates end-to-end 9-chapter document assembly
def test_full_report_tex_pipeline(tmp_path): ...
```

### Execution Log
```
============================= test session starts =============================
platform win32 -- Python 3.14.3, pytest-9.2.0, pluggy-1.7.0
rootdir: E:\OsdagBridge

tests/test_report_pipeline.py::test_styles_engine PASSED               [ 33%]
tests/test_report_pipeline.py::test_plot_generation PASSED            [ 66%]
tests/test_report_pipeline.py::test_full_report_tex_pipeline PASSED   [100%]

============================== 3 passed in 3.47s ==============================
```

---

## 3. Detailed Bug & Issue Reports

### Issue Report #1: Unhandled Top-Level `openseespy` Import Crashes Report Generator
- **Component:** `osdagbridge.core.bridge_types.plate_girder.results_data`
- **Severity:** High / Blocker (P1)
- **Description:** 
  When a user attempts to generate a design report without OpenSees installed locally, the process crashes completely with `ModuleNotFoundError: No module named 'openseespy'`.
- **Root Cause:**
  `executive_summary.py` imports a dictionary-formatting helper `_extract_osdag_summary` from `results_data.py`. However, `results_data.py` had an unshielded top-level `import openseespy.opensees as ops` at line 17, even though `ops` is only used inside mesh visualization.
- **Steps to Reproduce:**
  1. Set up an environment without `openseespy`.
  2. Populate bridge design inputs and outputs.
  3. Invoke `generate_report(payload, request)`.
  4. System raises `ModuleNotFoundError`.
- **Proposed & Implemented Fix:**
  Convert the import to a lazy/graceful import:
  ```python
  try:
      import openseespy.opensees as ops
  except ImportError:
      ops = None
  ```

---

### Issue Report #2: Table Headers Truncated Across Page Transitions
- **Component:** `osdagbridge.core.reports` (`chap5.py`, `chap3.py`, `chap7.py`)
- **Severity:** Medium / Usability (P2)
- **Description:**
  Multi-page tables in Chapter 5 (Tables 5.1 to 5.30) split across page breaks without repeating column headers on subsequent pages. Readers cannot identify which values correspond to which girder or check.
- **Root Cause:**
  PyLaTeX tables and raw `longtable` blocks lacked `\endfirsthead` and `\endhead` declarations.
- **Proposed & Implemented Fix:**
  Implemented `build_longtable_header()` and `enhance_longtables_in_tex()` in `styles.py` to automatically inject two-tier headers (`\endfirsthead`, `\endhead`, `\endfoot`, `\endlastfoot`) across all 29 tables in Chapter 5.

---

### Issue Report #3: Page 30 Text & Table Rows Bleeding into Footer Margin
- **Component:** `osdagbridge.core.reports.report_generator` (Preamble & Fancyhdr)
- **Severity:** Medium / Visual Polish (P2)
- **Description:**
  On Page 30 and similar check sections, table rows (e.g., girder check `G4`) bleed directly over the green footer rule and page number.
- **Root Cause:**
  In `fancyhdr`, `\renewcommand{\footrule}` included negative vertical skips (`\vspace{-20pt}` and `\vspace{-8pt}`). This physically pulled the footer rule upward into the body text area. Furthermore, `\usepackage[margin=1in]{geometry}` lacked explicit `headheight`, `headsep`, `footskip`, and `includefoot`.
- **Proposed & Implemented Fix:**
  1. Configured `GeometryConfig` with `bottom=28mm`, `footskip=18pt`, `includehead=True`, and `includefoot=True`.
  2. Removed negative `\vspace` in `\footrule`.
  3. Added `\BeforeBeginEnvironment{longtable}{\needspace{4\baselineskip}}` to ensure clean page breaks.

---

### Issue Report #4: Division by Zero on Zero / Negative Bridge Span in BOQ Engine
- **Component:** `osdagbridge.core.boq.boq_generator`
- **Severity:** Low-Medium (P3)
- **Description:**
  In `calculate_material_quantities()`, calculating rebar area via `rebar_area = rebar_vol / span` without prior guard conditions could trigger a `ZeroDivisionError` if `span <= 0` was passed in test fixtures or malformed project inputs.
- **Proposed & Implemented Fix:**
  Added defensive verification:
  ```python
  if span <= 0 or n_girders <= 0:
      return quantities
  rebar_area = rebar_vol / span if span > 0 else 0.0
  ```

---

### Issue Report #5: Merged Vehicular & Footpath Live Loads in Chapter 3
- **Component:** `osdagbridge.core.reports.chap3`
- **Severity:** Medium / Technical Standards (P2)
- **Description:**
  Vehicular live load parameters and footway loads were merged into a single table without parameter or unit columns, violating standard IRC 6 documentation practices.
- **Proposed & Implemented Fix:**
  Refactored Chapter 3 into two distinct tables:
  1. Table 3.3: Vehicular Live Loads (LL) with Vehicle Class, Impact Factor (Cl. 208), Braking Force (Cl. 211), and Centrifugal Force.
  2. Table 3.4: Footway and Pedestrian Live Loads (Cl. 206) with design intensity ($4\text{ kN/m}^2$) and standard references.

---

## 4. Conclusion & Impact

Through systematic testing, we:
- Eliminated runtime crash vectors (`openseespy` lazy import).
- Upgraded 40+ engineering tables to professional multi-page standards.
- Eliminated margin collisions and footer bleeding.
- Enhanced reporting compliance with Indian Road Congress (IRC) and Indian Standards (IS 800:2007).
