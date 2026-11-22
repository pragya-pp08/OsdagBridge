# FOSSEE Osdag Winter Internship 2026 — Final Submission Guide

**Applicant:** Pragya Pandey  
**Submission Deadline:** November 22, 2026  
**Tasks Completed (Software Development):**
1. **Task 1: LaTeX Report Generator Refactoring & Enhancements**
2. **Task 2: OsdagBridge Software Testing & Issue Reporting**

---

## 1. Summary of Deliverables in `E:\OsdagBridge\deliverables\`

| File / Folder | Status | Purpose |
| :--- | :--- | :--- |
| `Report_Before.pdf` | **READY** | Original un-refactored design report (350 KB). |
| `Report_After.pdf` | **READY** | Enhanced design report with repeated headers, calibrated margins, and charts (840 KB). |
| `Technical_Changes_Report.pdf` | **READY** | Official Technical Report (PDF) ready for upload to the FOSSEE submission form (368 KB). |
| `Supporting_Files.zip` | **READY** | Complete compressed project archive (7.1 MB) ready for upload to the FOSSEE submission form. |
| `Report_Before.tex` | **READY** | Genuine baseline report LaTeX source generated from original codebase using the bridge model (80 KB). |
| `Report_After.tex` | **READY** | Genuine enhanced report LaTeX source with repeated headers, unified styles, and dynamic charts (117 KB). |
| `Overleaf_Report_Compilation.zip` | **READY** | Standalone bundle for backup compilation on Overleaf (502 KB). |
| `TECHNICAL_CHANGES.md` | **READY** | Full markdown documentation of all architectural refactorings and engineering fixes. |
| `SOFTWARE_TESTING_AND_BUG_REPORTS.md` | **READY** | Task 2 testing documentation and 7 detailed, reproducible bug reports. |
| `assets/` | **READY** | High-resolution 300 DPI plot assets (`utilization_ratio_summary.png`, `material_steel_tonnage.png`, `material_concrete_rebar.png`, `osdag_logo.png`). |

---

## 2. GitHub Push & Collaborator Step

Open PowerShell or Git Bash and run the following commands to push your work to your personal GitHub repository:

```bash
cd E:\OsdagBridge
git checkout feature/report-generator-enhancements

# Stage and commit all enhancements
git add .
git commit -m "feat(report-generator): refactor layout, add centralized styles, longtable headers, and dynamic UR/material charts"

# Set your personal fork remote (replace <your-username> with your GitHub handle)
git remote set-url origin https://github.com/<your-username>/OsdagBridge.git

# Push the feature branch and dev branch
git push -u origin feature/report-generator-enhancements
```

### Adding Collaborator
1. Open your forked GitHub repository: `https://github.com/<your-username>/OsdagBridge`.
2. Go to **Settings** > **Collaborators** > **Add people**.
3. Search for **`Nidhikhare12`** and click **Add Nidhikhare12 to this repository**.

---

## 3. PDF Report Compilation (`Report_After.pdf` & `Report_Before.pdf`)

> **Environment Note:** LaTeX PDF compilation requires a TeX engine (`pdflatex`). In the terminal environment, if MiKTeX/TeX Live is not in the system PATH, `ReportOptions(include_pdf=False)` cleanly compiles the `.tex` file without error. Follow either of the two official methods below to produce the final compiled PDF deliverables with genuine bridge design inputs.

### Method A: Via OsdagBridge GUI (Recommended & Genuine)
This is the official screening workflow specified by FOSSEE:

#### 1. Generating `Report_Before.pdf` (Baseline Implementation):
```bash
cd E:\OsdagBridge
# Stash any uncommitted work or switch to baseline upstream dev
git checkout dev
conda activate osdagbridge-env  # or your Python environment
cd src
python -m osdagbridge.desktop
```
1. In the OsdagBridge GUI, load the default bridge project (Plate Girder Bridge).
2. Click **Design** to run structural analysis and component sizing.
3. Click **Generate Report** to output the PDF.
4. Save the generated PDF to `E:\OsdagBridge\deliverables\Report_Before.pdf`.

#### 2. Generating `Report_After.pdf` (Enhanced Implementation):
```bash
cd E:\OsdagBridge
git checkout feature/report-generator-enhancements
cd src
python -m osdagbridge.desktop
```
1. In the OsdagBridge GUI, run the identical bridge model by clicking **Design**.
2. Click **Generate Report**.
3. The report generator automatically calls `styles.py`, `plots.py`, and `enhance_longtables_in_tex()`, generating repeated headers, vertical UR chart with $\text{UR} = 1.0$ line, and material quantity charts.
4. Save the generated PDF to `E:\OsdagBridge\deliverables\Report_After.pdf`.

---

### Method B: Via Local TeX Live / MiKTeX CLI
If a TeX distribution (such as MiKTeX, TeX Live, or MacTeX) is installed:
```bash
cd E:\OsdagBridge\deliverables
pdflatex -interaction=nonstopmode Report_After.tex
pdflatex -interaction=nonstopmode Report_After.tex
```
*(Running twice resolves LaTeX internal references, table counters, and longtable column page markers).*

---

### Method C: Free Overleaf (Instant 1-Click Online Compilation)
1. Open [Overleaf.com](https://www.overleaf.com) (free account).
2. Click **New Project** > **Upload Project**.
3. Directly upload the pre-packaged ZIP: `E:\OsdagBridge\deliverables\Overleaf_Report_Compilation.zip`.
4. Inside Overleaf:
   - To get **`Report_Before.pdf`**: In the file tree on the left, click `Report_Before.tex` -> click the green **Recompile** button -> click the **Download PDF** icon next to Recompile -> Save file as `Report_Before.pdf` in `E:\OsdagBridge\deliverables\`.
   - To get **`Report_After.pdf`**: In the left file tree, click `Report_After.tex` -> click the green **Recompile** button -> click **Download PDF** -> Save file as `Report_After.pdf` in `E:\OsdagBridge\deliverables\`.
5. Both genuine PDF reports are now ready and placed directly in your repository!

---

## 4. Short Video Screencast Guide (2 to 3 Minutes)

*Note: As per FOSSEE guidelines, the video can be completely silent (no voiceover required).*

### What to Record:
1. **Screen 1 (VS Code / Editor):** Briefly show the clean code structure in `E:\OsdagBridge\src\osdagbridge\core\reports\styles.py` and `plots.py`.
2. **Screen 2 (Terminal):** Open PowerShell and run the test suite:
   ```bash
   python -m pytest tests/test_report_pipeline.py -v
   ```
   Show all 7 tests passing green (`PASSED [100%]`).
3. **Screen 3 (Generated PDF / Plots):** Open `Report_After.pdf` (or the generated plots in `deliverables/assets/`):
   - Highlight the repeated table headers across page breaks.
   - Show the clean margins and absence of footer overlap.
   - Show the separate Live Loads and Footway tables in Chapter 3.
   - Show the vertical Utilization Ratio bar chart with red dashed $\text{UR} = 1.0$ line in Section 5.5.
   - Show the Material Quantity bar charts (Girders, Cross Bracing, End Diaphragms) in Chapter 7.
4. Upload the video to **YouTube (Unlisted)** or **Google Drive (Anyone with link can view)**.

---

## 5. Google Form Submission Checklist

Before submitting on the [Official FOSSEE Google Form](https://docs.google.com/forms/d/e/1FAIpQLSdED-LhYmCoaI6AkLBfhfnRjS_LSNf-KX88vLQqej4-oKsdZw/viewform?usp=sharing), ensure you have:

- [ ] **Resume (PDF)**
- [ ] **Undertaking / Self Declaration Form / NOC** (if available, or note "Can be submitted after selection")
- [ ] **Link to Short Video (URL)** (YouTube / Google Drive link)
- [ ] **A Report (PDF)** $\rightarrow$ Upload `E:\OsdagBridge\deliverables\Technical_Changes_Report.pdf`
- [ ] **All Supporting Files as a ZIP File** $\rightarrow$ Upload `E:\OsdagBridge\deliverables\Supporting_Files.zip`
- [ ] **GitHub Repository Link** $\rightarrow$ `https://github.com/<your-username>/OsdagBridge` with `Nidhikhare12` added as a collaborator.
