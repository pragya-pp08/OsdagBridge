def update_report_generator():
    path = r'D:\OsdagBridge\src\osdagbridge\core\reports\report_generator.py'
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Normalize line endings
    content = content.replace('\r\n', '\n')

    # 1. Add imports
    old_imp = "from osdagbridge.core.reports.report_utils import _tex"
    new_imp = """from osdagbridge.core.reports.report_utils import _tex
from .styles import (
    GEOMETRY,
    TABLE_STYLE,
    PALETTE,
    get_latex_color_definitions,
    build_page_styles,
    enhance_longtables_in_tex,
)
from .plots import generate_material_quantity_plots, generate_utilization_ratio_plot"""

    if new_imp not in content:
        content = content.replace(old_imp, new_imp)

    # 2. Update preamble
    old_preamble = """def preamble(project_name, job_number, report_date, report_version='Rev 0'):
    pn = _tex(project_name)
    jn = _tex(job_number)
    rd = _tex(report_date)
    rv = _tex(report_version)
    return r\"\"\"
\\documentclass[12pt,a4paper]{report}

% Packages
\\usepackage[a4paper, margin=1in]{geometry}
\\usepackage{graphicx}
\\usepackage{amsmath}
\\usepackage{amssymb}
\\usepackage{booktabs}
\\usepackage{array}
\\usepackage{tabularx}
\\usepackage{float}
\\usepackage{fancyhdr}
\\usepackage[hidelinks]{hyperref}
\\usepackage{xcolor}
\\usepackage{setspace}
\\usepackage{enumitem}
\\usepackage{caption}

\\captionsetup{
    labelfont=bf,
    justification=raggedright,
    singlelinecheck=false,
    format=plain
}
\\usepackage{subcaption}
\\usepackage{multirow}
\\usepackage{colortbl}
\\usepackage{longtable}
\\setlength{\\LTleft}{\\fill}
\\setlength{\\LTright}{\\fill}
\\usepackage{titlesec}
\\usepackage{titletoc}
\\usepackage{lastpage}
\\usepackage{makecell}
\\usepackage{etoolbox}
\\usepackage{needspace}

\\numberwithin{table}{chapter}
\\numberwithin{figure}{chapter}
% Table layout and spacing: consistent padding, row height, and longtable pre/post skips
\\setlength{\\tabcolsep}{6pt}
\\renewcommand{\\arraystretch}{1.12}
\\setlength{\\LTpre}{0pt}
\\setlength{\\LTpost}{6pt}
% Table rules (outline thickness) and small extra row height for clarity
\\setlength{\\arrayrulewidth}{0.5pt}
\\setlength{\\extrarowheight}{0.6pt}

% Prevent tables from overflowing past the page bottom:
% if fewer than 5 baseline-skips remain, break to the next page first.
\\BeforeBeginEnvironment{table}{\\needspace{5\\baselineskip}}
\\BeforeBeginEnvironment{longtable}{\\needspace{5\\baselineskip}}

\\definecolor{osdagGreen}{HTML}{91B014}

\\fancypagestyle{main}{
  \\fancyhf{}
  \\fancyhead[L]{\"\"\" + pn + r\"\"\" $|$ \"\"\" + jn + r\"\"\"}
  \\fancyhead[R]{\"\"\" + rd + r\"\"\" $|$ \"\"\" + rv + r\"\"\"}
  \\fancyfoot[L]{Osdag $|$ FOSSEE $|$ Indian Institute of Technology Bombay}
  \\fancyfoot[R]{Page \\thepage\\ of \\pageref{LastPage}}
  \\renewcommand{\\headrule}{\\color{osdagGreen}\\hrule width\\headwidth height 1pt \\vspace{2pt}}
  \\renewcommand{\\footrule}{%
    \\ifbool{hasSDonPage}{%
      \\vspace{-20pt}%
      \\hbox to \\headwidth{\\textcolor{black}{\\footnotesize\\textit{* Software default value}}\\hfil}%
      \\vspace{4pt}%
    }{%
      \\vspace{-8pt}%
    }%
    \\color{osdagGreen}\\hrule width\\headwidth height 1pt \\vspace{6pt}%
  }
}
\\fancypagestyle{plain}{
  \\fancyhf{}
  \\fancyhead[L]{\"\"\" + pn + r\"\"\" $|$ \"\"\" + jn + r\"\"\"}
  \\fancyhead[R]{\"\"\" + rd + r\"\"\" $|$ \"\"\" + rv + r\"\"\"}
  \\fancyfoot[L]{Osdag $|$ FOSSEE $|$ Indian Institute of Technology Bombay}
  \\fancyfoot[R]{Page \\thepage\\ of \\pageref{LastPage}}
  \\renewcommand{\\headrule}{\\color{osdagGreen}\\hrule width\\headwidth height 1pt \\vspace{2pt}}
  \\renewcommand{\\footrule}{%
    \\ifbool{hasSDonPage}{%
      \\vspace{-20pt}%
      \\hbox to \\headwidth{\\textcolor{black}{\\footnotesize\\textit{* Software default value}}\\hfil}%
      \\vspace{4pt}%
    }{%
      \\vspace{-8pt}%
    }%
    \\color{osdagGreen}\\hrule width\\headwidth height 1pt \\vspace{6pt}%
  }
}
\\fancypagestyle{firstpage}{
  \\fancyhf{}
  \\renewcommand{\\headrulewidth}{0pt}
  \\fancyfoot[L]{Osdag $|$ FOSSEE $|$ Indian Institute of Technology Bombay}
  \\fancyfoot[R]{Page \\thepage\\ of \\pageref{LastPage}}
  \\renewcommand{\\footrule}{\\vspace{-8pt}\\color{osdagGreen}\\hrule width\\headwidth height 1pt \\vspace{6pt}}
}
\\pagestyle{main}
\\setstretch{1.15}

% Custom Commands
\\newcommand{\\placeholder}[1]{\\textit{\\textless #1\\textgreater}}
\\newcommand{\\todo}[1]{\\colorbox{yellow}{TODO: #1}}
\\newcolumntype{L}[1]{>{\\raggedright\\arraybackslash}p{#1}}
\\newcolumntype{C}[1]{>{\\centering\\arraybackslash}p{#1}}
\\newcolumntype{R}[1]{>{\\raggedleft\\arraybackslash}p{#1}}

% Software-default asterisk
\\newcommand{\\sdstar}{\\textsuperscript{*}}
\\newbool{hasSDonPage}
\\boolfalse{hasSDonPage}
\\newcommand{\\markSD}{\\global\\booltrue{hasSDonPage}}
\\renewcommand{\\sdstar}{\\textsuperscript{*}\\markSD{}}
\\AddToHook{shipout/before}{\\global\\boolfalse{hasSDonPage}}

\\title{\\Large\\textbf{OsdagBridge} \\\\ \\normalsize Open Source Software for Steel Girder Bridge Design \\\\ \\vspace{2cm} \\large Design Report}
\\author{}
\\date{}

\\begin{document}
\"\"\""""

    new_preamble = """def preamble(project_name, job_number, report_date, report_version='Rev 0'):
    pn = _tex(project_name)
    jn = _tex(job_number)
    rd = _tex(report_date)
    rv = _tex(report_version)
    return r\"\"\"
\\documentclass[12pt,a4paper]{report}

% Packages & Geometries from Centralized styles.py
\"\"\" + GEOMETRY.to_latex_geometry() + r\"\"\"
\\usepackage{graphicx}
\\usepackage{amsmath}
\\usepackage{amssymb}
\\usepackage{booktabs}
\\usepackage{array}
\\usepackage{tabularx}
\\usepackage{float}
\\usepackage{fancyhdr}
\\usepackage[hidelinks]{hyperref}
\\usepackage{xcolor}
\\usepackage{setspace}
\\usepackage{enumitem}
\\usepackage{caption}

\\captionsetup{
    labelfont=bf,
    justification=raggedright,
    singlelinecheck=false,
    format=plain
}
\\usepackage{subcaption}
\\usepackage{multirow}
\\usepackage{colortbl}
\\usepackage{longtable}
\\setlength{\\LTleft}{\\fill}
\\setlength{\\LTright}{\\fill}
\\usepackage{titlesec}
\\usepackage{titletoc}
\\usepackage{lastpage}
\\usepackage{makecell}
\\usepackage{etoolbox}
\\usepackage{needspace}

\\numberwithin{table}{chapter}
\\numberwithin{figure}{chapter}

\"\"\" + TABLE_STYLE.to_latex_preamble_block() + r\"\"\"

\"\"\" + get_latex_color_definitions() + r\"\"\"

\"\"\" + build_page_styles(pn, jn, rd, rv) + r\"\"\"
\\pagestyle{main}
\\setstretch{1.15}

% Prevent orphans and widows
\\clubpenalty=10000
\\widowpenalty=10000

% Custom Commands
\\newcommand{\\placeholder}[1]{\\textit{\\textless #1\\textgreater}}
\\newcommand{\\todo}[1]{\\colorbox{yellow}{TODO: #1}}
\\newcolumntype{L}[1]{>{\\raggedright\\arraybackslash}p{#1}}
\\newcolumntype{C}[1]{>{\\centering\\arraybackslash}p{#1}}
\\newcolumntype{R}[1]{>{\\raggedleft\\arraybackslash}p{#1}}

% Software-default asterisk
\\newcommand{\\sdstar}{\\textsuperscript{*}}
\\newbool{hasSDonPage}
\\boolfalse{hasSDonPage}
\\newcommand{\\markSD}{\\global\\booltrue{hasSDonPage}}
\\renewcommand{\\sdstar}{\\textsuperscript{*}\\markSD{}}
\\AddToHook{shipout/before}{\\global\\boolfalse{hasSDonPage}}

\\title{\\Large\\textbf{OsdagBridge} \\\\ \\normalsize Open Source Software for Steel Girder Bridge Design \\\\ \\vspace{2cm} \\large Design Report}
\\author{}
\\date{}

\\begin{document}
\"\"\""""

    if old_preamble in content:
        content = content.replace(old_preamble, new_preamble)
        print("Preamble updated successfully!")
    else:
        print("Preamble not found verbatim!")

    # 3. Update generation logic (plots + arguments)
    old_assembly = """            # Compute and inject quantities for Chapter 7
            quantities = calculate_material_quantities(payload.inputs, payload.output_dict)
            payload.inputs.update(quantities)

            # ── Assemble LaTeX document (fig_paths now has tmp_dir paths) ──
            bridge = ReportDataBridge(payload.output_dict, payload.inputs, payload)
            span_m = float(payload.inputs.get(KEY_SPAN, 0) or 0)

            doc_parts = []
            doc_parts.append(preamble(payload.metadata.project_name, payload.metadata.job_number, payload.metadata.report_date, payload.metadata.subtitle or 'Rev 0'))
            doc_parts.append(title_page(payload.metadata, osdag_logo_latex, org_logo_latex))

            if payload.options.include_toc:
                doc_parts.append(toc_section())

            # Chapter inclusion is driven by the canonical section keys
            # selected in the report-options dialog (TOC). The first three
            # chapters are locked in the UI, so they are always present.
            secs = payload.options.sections

            doc_parts.append(executive_summary(payload.inputs, payload.output_dict, fig_paths))
            doc_parts.append(ch1_project_info(payload.metadata))
            doc_parts.append(ch2_input_parameters(payload.metadata, payload.inputs, payload.output_dict))

            if 'loads' in secs:
                doc_parts.append(ch3_loads(payload.inputs))
            if 'analysis' in secs:
                doc_parts.append(ch4_analysis(payload.analysis_summary, fig_paths, bridge, span_m))
            if 'design_checks' in secs:
                doc_parts.append(ch5_design_checks(payload.design_checks, bridge))
            if 'drawings' in secs and payload.options.include_figures:
                doc_parts.append(ch6_drawings(fig_paths))

            doc_parts.append(ch7_quantities(payload.inputs))"""

    new_assembly = """            # Compute and inject quantities for Chapter 7
            quantities = calculate_material_quantities(payload.inputs, payload.output_dict)
            payload.inputs.update(quantities)

            # Generate dynamic data visualizations (Section 5.5 and Chapter 7)
            try:
                steel_plot, conc_plot = generate_material_quantity_plots(quantities, tmp_assets)
                fig_paths['material_steel'] = 'assets/' + os.path.basename(steel_plot)
                fig_paths['material_concrete_rebar'] = 'assets/' + os.path.basename(conc_plot)

                ur_plot = os.path.join(tmp_assets, 'utilization_ratio_summary.png')
                generate_utilization_ratio_plot([], ur_plot)
                fig_paths['ur_summary'] = 'assets/utilization_ratio_summary.png'
            except Exception as e:
                logger.warning(f"Error generating dynamic report plots: {e}")

            # ── Assemble LaTeX document (fig_paths now has tmp_dir paths) ──
            bridge = ReportDataBridge(payload.output_dict, payload.inputs, payload)
            span_m = float(payload.inputs.get(KEY_SPAN, 0) or 0)

            doc_parts = []
            doc_parts.append(preamble(payload.metadata.project_name, payload.metadata.job_number, payload.metadata.report_date, payload.metadata.subtitle or 'Rev 0'))
            doc_parts.append(title_page(payload.metadata, osdag_logo_latex, org_logo_latex))

            if payload.options.include_toc:
                doc_parts.append(toc_section())

            secs = payload.options.sections

            doc_parts.append(executive_summary(payload.inputs, payload.output_dict, fig_paths))
            doc_parts.append(ch1_project_info(payload.metadata))
            doc_parts.append(ch2_input_parameters(payload.metadata, payload.inputs, payload.output_dict))

            if 'loads' in secs:
                doc_parts.append(ch3_loads(payload.inputs))
            if 'analysis' in secs:
                doc_parts.append(ch4_analysis(payload.analysis_summary, fig_paths, bridge, span_m))
            if 'design_checks' in secs:
                doc_parts.append(ch5_design_checks(payload.design_checks, bridge, fig_paths))
            if 'drawings' in secs and payload.options.include_figures:
                doc_parts.append(ch6_drawings(fig_paths))

            doc_parts.append(ch7_quantities(payload.inputs, fig_paths))"""

    if old_assembly in content:
        content = content.replace(old_assembly, new_assembly)
        print("Assembly logic updated successfully!")
    else:
        print("Assembly logic not found verbatim!")

    # 4. Longtable enhancer call on full_tex
    old_full_tex = "full_tex = \"\\n\".join(doc_parts)"
    new_full_tex = """full_tex = \"\\n\".join(doc_parts)
            full_tex = enhance_longtables_in_tex(full_tex)"""
    if old_full_tex in content and "enhance_longtables_in_tex(full_tex)" not in content:
        content = content.replace(old_full_tex, new_full_tex)
        print("Added enhance_longtables_in_tex call to full_tex!")

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("report_generator.py written!")

if __name__ == '__main__':
    update_report_generator()
