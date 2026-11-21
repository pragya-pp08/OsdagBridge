import re

def update_chap5():
    file_path = r'D:\OsdagBridge\src\osdagbridge\core\reports\chap5.py'
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Normalize line endings to LF
    content = content.replace('\r\n', '\n')

    # 1. Update signature if not already updated
    if 'def ch5_design_checks(checks_data, bridge, fig_paths=None)' not in content:
        content = content.replace(
            'def ch5_design_checks(checks_data, bridge) -> str:',
            'def ch5_design_checks(checks_data, bridge, fig_paths=None) -> str:'
        )

    # 2. Update Section 5.5
    old_sec55 = """% ===========================
\\section{Overall Design Check Summary}
\\label{sec:overall-summary}
% ===========================

\\vspace{1em}
\\begin{longtable}{|C{3.4cm}|L{4.5cm}|C{2.3cm}|C{2.3cm}|>{\\centering\\arraybackslash}p{1.6cm}|}
\\caption{\\textbf{Overall Design Check Summary --- All Members}}
\\hline
\\textbf{Member / Check} & \\textbf{Governing Load Combo} & \\textbf{Demand} & \\textbf{Capacity} & \\textbf{UR} \\\\[6pt]
\\hline
\"\"\" + t522_content + r\"\"\"
\\end{longtable}
\\noindent\\textit{Note: UR = Demand / Capacity. All values $\\leq 1.0$ indicate passing checks. The governing check for each component is highlighted in the individual design check sections above.}"""

    new_sec55 = """% ===========================
\\clearpage
\\section{Overall Design Check Summary}
\\label{sec:overall-summary}
% ===========================

This section summarizes the governing demand-to-capacity Utilization Ratios (UR) across all primary superstructure components (steel plate girders, concrete deck slab, cross bracing, and end diaphragms) under the critical limit state load combinations.

\\begin{figure}[H]
\\centering
\\includegraphics[width=0.96\\textwidth]{"\"\" + (fig_paths.get('ur_summary', 'assets/utilization_ratio_summary.png') if fig_paths else 'assets/utilization_ratio_summary.png') + r\"\""}
\\caption{\\textbf{Governing Utilization Ratio (Demand / Capacity) Summary Across Primary Members}}
\\label{fig:overall_ur_summary}
\\end{figure}

\\vspace{0.8em}
\\begin{longtable}{|C{3.4cm}|L{4.5cm}|C{2.3cm}|C{2.3cm}|>{\\centering\\arraybackslash}p{1.6cm}|}
\\caption{\\textbf{Overall Design Check Summary --- All Members}} \\label{tab:overall-summary} \\\\
\\hline
\\textbf{Member / Check} & \\textbf{Governing Load Combo} & \\textbf{Demand} & \\textbf{Capacity} & \\textbf{UR} \\\\[4pt]
\\hline
\\endfirsthead

\\multicolumn{5}{c}{\\small\\textit{Table \\thetable{} (continued from previous page)}} \\\\[4pt]
\\hline
\\textbf{Member / Check} & \\textbf{Governing Load Combo} & \\textbf{Demand} & \\textbf{Capacity} & \\textbf{UR} \\\\[4pt]
\\hline
\\endhead

\\hline
\\multicolumn{5}{r}{\\footnotesize\\textit{Continued on next page...}} \\\\
\\endfoot

\\hline
\\endlastfoot
\"\"\" + t522_content + r\"\"\"
\\end{longtable}
\\noindent\\textit{Note: UR = Demand / Capacity. All values $\\leq 1.0$ indicate passing checks per IS 800:2007 and IRC 22:2014. The governing check for each component is highlighted in the individual design check sections above.}"""

    if old_sec55 in content:
        content = content.replace(old_sec55, new_sec55)
        print("Section 5.5 successfully updated!")
    else:
        print("Warning: old_sec55 not found verbatim, checking partial...")
        pattern_sec55 = re.compile(
            r'% ===========================\s*\\section\{Overall Design Check Summary\}.*?\\end\{longtable\}\s*\\noindent\\textit\{Note: UR = Demand / Capacity.*?\n\"\"\"',
            re.DOTALL
        )
        content = pattern_sec55.sub(new_sec55 + '\n"""', content)
        print("Section 5.5 updated via regex!")

    # 3. Enhance all other longtables to have \endfirsthead and \endhead
    pattern = re.compile(
        r'(\\begin\{longtable\}\{(.+?)\}\s*'
        r'\\caption\{(.+?)\}\s*(?:\\label\{([^}]+)\}\s*)?'
        r'\\hline\s*'
        r'(.+?)\s*'
        r'\\hline)',
        re.DOTALL
    )

    def replacer(match):
        full_match = match.group(1)
        col_spec = match.group(2)
        caption = match.group(3)
        label = match.group(4)
        header_row = match.group(5).strip()

        if r'\endfirsthead' in full_match:
            return full_match

        num_cols = header_row.count('&') + 1
        clean_header = re.sub(r'\\\\\s*(\[[^\]]*\])?\s*$', '', header_row).strip()
        lbl_code = f"\\label{{{label}}} " if label else ""

        return (
            f"\\begin{{longtable}}{{{col_spec}}}\n"
            f"\\caption{{{caption}}} {lbl_code}\\\\\n"
            f"\\hline\n"
            f"{clean_header} \\\\[4pt]\n"
            f"\\hline\n"
            f"\\endfirsthead\n\n"
            f"\\multicolumn{{{num_cols}}}{{c}}{{\\small\\textit{{Table \\thetable{{}} (continued from previous page)}}}} \\\\[4pt]\n"
            f"\\hline\n"
            f"{clean_header} \\\\[4pt]\n"
            f"\\hline\n"
            f"\\endhead\n\n"
            f"\\hline\n"
            f"\\multicolumn{{{num_cols}}}{{r}}{{\\footnotesize\\textit{{Continued on next page...}}}} \\\\\n"
            f"\\endfoot\n\n"
            f"\\hline\n"
            f"\\endlastfoot"
        )

    content = pattern.sub(replacer, content)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"Chap5 updated successfully! Total \\endfirsthead: {content.count(r'\endfirsthead')}")

if __name__ == '__main__':
    update_chap5()
