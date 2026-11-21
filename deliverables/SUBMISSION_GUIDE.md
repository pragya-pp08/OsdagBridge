# FOSSEE Osdag Winter Internship 2026 — Final Submission Guide

**Applicant:** Pragya Pandey  
**Submission Deadline:** November 22, 2026  
**Tasks Completed (Software Development):**
1. **Task 1: LaTeX Report Generator Refactoring & Enhancements**
2. **Task 2: OsdagBridge Software Testing & Issue Reporting**

---

## 1. Summary of Deliverables in `E:\OsdagBridge\deliverables\`

| File / Folder | Purpose |
| :--- | :--- |
| `TECHNICAL_CHANGES.md` | Primary technical report detailing the 6 core refactorings, `styles.py` single source of truth, and architectural decisions. |
| `SOFTWARE_TESTING_AND_BUG_REPORTS.md` | Second task deliverable containing automated test suites and 5 comprehensive, reproducible bug reports. |
| `Report_After.tex` | The full compiled 9-chapter design report LaTeX source (101 KB). |
| `assets/` | Folder containing high-resolution 300 DPI plots (`utilization_ratio_summary.png`, `material_steel_tonnage.png`, `material_concrete_rebar.png`, `osdag_logo.png`). |

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

### Option A: Local MiKTeX / TeX Live
If you have MiKTeX or TeX Live installed on Windows:
```bash
cd E:\OsdagBridge\deliverables
pdflatex -interaction=nonstopmode Report_After.tex
pdflatex -interaction=nonstopmode Report_After.tex
```

### Option B: Free Overleaf (Instant 1-Click Online Compilation)
1. Open [Overleaf.com](https://www.overleaf.com) (free account).
2. Click **New Project** > **Upload Project**.
3. Upload a ZIP of the `E:\OsdagBridge\deliverables\` folder (containing `Report_After.tex` and the `assets/` folder).
4. Click **Recompile** in Overleaf.
5. Click **Download PDF** and save as `Report_After.pdf`!

---

## 4. Short Video Screencast Guide (2 to 3 Minutes)

*Note: As per FOSSEE guidelines, the video can be completely silent (no voiceover required).*

### What to Record:
1. **Screen 1 (VS Code / Editor):** Briefly show the clean code structure in `E:\OsdagBridge\src\osdagbridge\core\reports\styles.py` and `plots.py`.
2. **Screen 2 (Terminal):** Open PowerShell and run the test suite:
   ```bash
   python -m pytest tests/test_report_pipeline.py -v
   ```
   Show all 3 tests passing green (`[PASS]`).
3. **Screen 3 (Generated PDF / Plots):** Open `Report_After.pdf` (or the generated plots in `deliverables/assets/`):
   - Highlight the repeated table headers across page breaks.
   - Show the clean margins and absence of footer overlap.
   - Show the separate Live Loads and Footway tables in Chapter 3.
   - Show the Utilization Ratio bar chart with red dashed $\text{UR} = 1.0$ line in Section 5.5.
   - Show the Material Quantity bar charts in Chapter 7.
4. Upload the video to **YouTube (Unlisted)** or **Google Drive (Anyone with link can view)**.

---

## 5. Google Form Submission Checklist

Before submitting on the [Official FOSSEE Google Form](https://docs.google.com/forms/d/e/1FAIpQLSdED-LhYmCoaI6AkLBfhfnRjS_LSNf-KX88vLQqej4-oKsdZw/viewform?usp=sharing), ensure you have:

- [ ] **Resume (PDF)**
- [ ] **Undertaking / Self Declaration Form / NOC** (if available, or note "Can be submitted after selection")
- [ ] **Link to Short Video (URL)** (YouTube / Google Drive link)
- [ ] **A Report (PDF)** (Export `TECHNICAL_CHANGES.md` or merge with `SOFTWARE_TESTING_AND_BUG_REPORTS.md`)
- [ ] **All Supporting Files as a ZIP File** (Zip `E:\OsdagBridge` including `deliverables/`, `src/`, and `tests/`)
- [ ] **GitHub Repository Link** with `Nidhikhare12` added as a collaborator.
