import re

def enhance_longtables_in_tex(tex: str) -> str:
    """
    Transforms longtable environments without \\endfirsthead into fully-featured
    multi-page tables with repeated column headers on every page break.
    """
    # Find all \begin{longtable} blocks
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

        # If already has endfirsthead, skip
        if r'\endfirsthead' in full_match:
            return full_match

        # Count columns from header row
        num_cols = header_row.count('&') + 1

        # Clean trailing newline or \\[...pt] from header_row
        clean_header = re.sub(r'\\\\\s*(\[[^\]]*\])?\s*$', '', header_row).strip()

        lbl_code = f"\\label{{{label}}} " if label else ""

        # Build replacement block with \endfirsthead, \endhead, \endfoot, \endlastfoot
        replacement = (
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
        return replacement

    return pattern.sub(replacer, tex)

if __name__ == '__main__':
    with open(r'D:\OsdagBridge\src\osdagbridge\core\reports\chap5.py', 'r', encoding='utf-8') as f:
        src = f.read()

    enhanced = enhance_longtables_in_tex(src)
    count_before = src.count(r'\endfirsthead')
    count_after = enhanced.count(r'\endfirsthead')
    print(f"endfirsthead before: {count_before}, after: {count_after}")
