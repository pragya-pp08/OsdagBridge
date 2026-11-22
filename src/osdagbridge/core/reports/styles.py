# =============================================================================
# OsdagBridge — Centralized Report Styling & Formatting Engine
# Single Source of Truth for Layout, Geometry, Colors, Tables, and Typography
# =============================================================================

import re
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Union


@dataclass(frozen=True)
class ColorPalette:
    """Hex color codes used across the LaTeX document and generated figures."""
    PRIMARY: str = "#91B014"         # Osdag Green
    PRIMARY_DARK: str = "#6A820E"    # Dark Osdag Green
    SECONDARY: str = "#1A365D"       # Deep Navy / Header text
    PASS: str = "#2E7D32"            # Success Green (UR <= 1.0)
    PASS_LIGHT: str = "#E8F5E9"      # Light Green tint
    WARNING: str = "#F57C00"         # Warning Amber (0.85 < UR <= 1.0)
    FAIL: str = "#C62828"            # Danger / Failure Red (UR > 1.0)
    FAIL_LIGHT: str = "#FFEBEE"      # Light Red tint
    ACCENT: str = "#0288D1"          # Sky Blue (Secondary bars / accents)
    TEXT: str = "#212121"            # Off-black body text
    TEXT_MUTED: str = "#757575"      # Grey annotations
    BG_LIGHT: str = "#F8F9FA"        # Light background for table alternating rows
    TABLE_HEADER_BG: str = "#E9ECEF" # Subtle grey header fill
    BORDER: str = "#B0BEC5"          # Table grid borders


@dataclass(frozen=True)
class GeometryConfig:
    """Page geometry and margin configuration."""
    PAPER: str = "a4paper"
    LEFT_MARGIN_MM: int = 20
    RIGHT_MARGIN_MM: int = 20
    TOP_MARGIN_MM: int = 25
    BOTTOM_MARGIN_MM: int = 28
    HEAD_HEIGHT_PT: int = 24
    HEAD_SEP_PT: int = 14
    FOOT_SKIP_PT: int = 18
    INCLUDE_HEAD: bool = True
    INCLUDE_FOOT: bool = True

    def to_latex_geometry(self) -> str:
        head_opt = "includehead," if self.INCLUDE_HEAD else ""
        foot_opt = "includefoot," if self.INCLUDE_FOOT else ""
        return (
            rf"\usepackage[{self.PAPER},"
            rf"left={self.LEFT_MARGIN_MM}mm,"
            rf"right={self.RIGHT_MARGIN_MM}mm,"
            rf"top={self.TOP_MARGIN_MM}mm,"
            rf"bottom={self.BOTTOM_MARGIN_MM}mm,"
            rf"headheight={self.HEAD_HEIGHT_PT}pt,"
            rf"headsep={self.HEAD_SEP_PT}pt,"
            rf"footskip={self.FOOT_SKIP_PT}pt,"
            rf"{head_opt}{foot_opt}]{{geometry}}"
        )


@dataclass(frozen=True)
class TableStyleConfig:
    """Standard table layout and spacing parameters."""
    TABCOLSEP_PT: float = 5.5
    ARRAYSTRETCH: float = 1.18
    ARRAYRULEWIDTH_PT: float = 0.5
    EXTRAROWHEIGHT_PT: float = 0.8
    LTPRE_PT: float = 0.0
    LTPOST_PT: float = 6.0
    NEEDSPACE_LINES: int = 4

    def to_latex_preamble_block(self) -> str:
        return f"""% Table layout and spacing (Single Source of Truth from styles.py)
\\setlength{{\\tabcolsep}}{{{self.TABCOLSEP_PT}pt}}
\\renewcommand{{\\arraystretch}}{{{self.ARRAYSTRETCH}}}
\\setlength{{\\LTpre}}{{{self.LTPRE_PT}pt}}
\\setlength{{\\LTpost}}{{{self.LTPOST_PT}pt}}
\\setlength{{\\arrayrulewidth}}{{{self.ARRAYRULEWIDTH_PT}pt}}
\\setlength{{\\extrarowheight}}{{{self.EXTRAROWHEIGHT_PT}pt}}
\\BeforeBeginEnvironment{{table}}{{\\needspace{{{self.NEEDSPACE_LINES}\\baselineskip}}}}
\\BeforeBeginEnvironment{{longtable}}{{\\needspace{{{self.NEEDSPACE_LINES}\\baselineskip}}}}
"""


# Global singletons
PALETTE = ColorPalette()
GEOMETRY = GeometryConfig()
TABLE_STYLE = TableStyleConfig()


def get_latex_color_definitions() -> str:
    r"""Return LaTeX \definecolor commands for all palette entries."""
    def hex_to_latex(name: str, hex_val: str) -> str:
        clean = hex_val.lstrip("#")
        return f"\\definecolor{{{name}}}{{HTML}}{{{clean}}}"

    return "\n".join([
        hex_to_latex("osdagGreen", PALETTE.PRIMARY),
        hex_to_latex("osdagGreenDark", PALETTE.PRIMARY_DARK),
        hex_to_latex("osdagNavy", PALETTE.SECONDARY),
        hex_to_latex("osdagPass", PALETTE.PASS),
        hex_to_latex("osdagFail", PALETTE.FAIL),
        hex_to_latex("osdagWarning", PALETTE.WARNING),
        hex_to_latex("osdagAccent", PALETTE.ACCENT),
        hex_to_latex("tableHeaderBg", PALETTE.TABLE_HEADER_BG),
    ])


def build_longtable_header(
    caption: str,
    header_rows: Union[List[str], List[List[str]]],
    label: Optional[str] = None,
    num_cols: int = 2,
    short_caption: Optional[str] = None
) -> str:
    """
    Generate robust, multi-page LaTeX LongTable headers with \\endfirsthead and \\endhead.
    
    Ensures:
      - First page displays caption, optional label, and header row.
      - Every subsequent page repeated header displays caption (continued) and identical header row.
      - Page bottoms have standard continuation indicators via \\endfoot and \\endlastfoot.
      - Header columns in the same row are joined using " & ".
    """
    lbl_tex = f"\\label{{{label}}}" if label else ""
    short_cap = f"[{short_caption}]" if short_caption else ""
    cap_text = f"\\textbf{{{caption}}}"
    
    if not header_rows:
        header_content = ""
    elif isinstance(header_rows[0], (list, tuple)):
        # List of rows, each being a list of column strings
        row_lines = [" & ".join(row) + r" \\[4pt]" for row in header_rows]
        header_content = "\n\\hline\n".join(row_lines) + "\n\\hline"
    elif any("&" in str(r) for r in header_rows):
        # Already joined row strings
        row_lines = [r.rstrip(r" \t\n\\") + r" \\[4pt]" for r in header_rows]
        header_content = "\n\\hline\n".join(row_lines) + "\n\\hline"
    else:
        # A single row given as a list of column header cells
        header_content = " & ".join(header_rows) + r" \\[4pt]" + "\n\\hline"

    return f"""\\caption{short_cap}{{{cap_text}}}{lbl_tex} \\\\
\\hline
{header_content}
\\endfirsthead

\\multicolumn{{{num_cols}}}{{c}}{{\\small\\textit{{Table \\thetable{{}} (continued from previous page)}}}} \\\\[4pt]
\\hline
{header_content}
\\endhead

\\hline
\\multicolumn{{{num_cols}}}{{r}}{{\\footnotesize\\textit{{Continued on next page...}}}} \\\\
\\endfoot

\\hline
\\endlastfoot
"""


def build_page_styles(project_name: str, job_number: str, report_date: str, report_version: str) -> str:
    """
    Generate LaTeX fancyhdr page styles with calibrated vertical spacing
    preventing any footer/header overlap.
    """
    return f"""% Header and Footer Styling with Calibrated Margins
\\fancypagestyle{{main}}{{
  \\fancyhf{{}}
  \\fancyhead[L]{{\\parbox[b]{{0.62\\headwidth}}{{\\raggedright\\footnotesize\\textbf{{{project_name}}}\\\\[1pt]\\scriptsize {job_number}}}}}
  \\fancyhead[R]{{\\parbox[b]{{0.36\\headwidth}}{{\\raggedleft\\footnotesize {report_date}\\\\[1pt]\\scriptsize {report_version}}}}}
  \\fancyfoot[L]{{\\footnotesize Osdag $|$ FOSSEE $|$ Indian Institute of Technology Bombay}}
  \\fancyfoot[R]{{\\footnotesize Page \\thepage\\ of \\pageref{{LastPage}}}}
  \\renewcommand{{\\headrule}}{{\\color{{osdagGreen}}\\hrule width\\headwidth height 1pt \\vspace{{2pt}}}}
  \\renewcommand{{\\footrule}}{{%
    \\ifbool{{hasSDonPage}}{{%
      \\hbox to \\headwidth{{\\textcolor{{black}}{{\\scriptsize\\textit{{* Software default value}}}}\\hfil}}%
      \\vspace{{2pt}}%
    }}{{%
      \\vspace{{0pt}}%
    }}%
    \\color{{osdagGreen}}\\hrule width\\headwidth height 1pt \\vspace{{4pt}}%
  }}
}}
\\fancypagestyle{{plain}}{{
  \\fancyhf{{}}
  \\fancyhead[L]{{\\parbox[b]{{0.62\\headwidth}}{{\\raggedright\\footnotesize\\textbf{{{project_name}}}\\\\[1pt]\\scriptsize {job_number}}}}}
  \\fancyhead[R]{{\\parbox[b]{{0.36\\headwidth}}{{\\raggedleft\\footnotesize {report_date}\\\\[1pt]\\scriptsize {report_version}}}}}
  \\fancyfoot[L]{{\\footnotesize Osdag $|$ FOSSEE $|$ Indian Institute of Technology Bombay}}
  \\fancyfoot[R]{{\\footnotesize Page \\thepage\\ of \\pageref{{LastPage}}}}
  \\renewcommand{{\\headrule}}{{\\color{{osdagGreen}}\\hrule width\\headwidth height 1pt \\vspace{{2pt}}}}
  \\renewcommand{{\\footrule}}{{%
    \\ifbool{{hasSDonPage}}{{%
      \\hbox to \\headwidth{{\\textcolor{{black}}{{\\scriptsize\\textit{{* Software default value}}}}\\hfil}}%
      \\vspace{{2pt}}%
    }}{{%
      \\vspace{{0pt}}%
    }}%
    \\color{{osdagGreen}}\\hrule width\\headwidth height 1pt \\vspace{{4pt}}%
  }}
}}
\\fancypagestyle{{firstpage}}{{
  \\fancyhf{{}}
  \\renewcommand{{\\headrulewidth}}{{0pt}}
  \\fancyfoot[L]{{\\footnotesize Osdag $|$ FOSSEE $|$ Indian Institute of Technology Bombay}}
  \\fancyfoot[R]{{\\footnotesize Page \\thepage\\ of \\pageref{{LastPage}}}}
  \\renewcommand{{\\footrule}}{{\\color{{osdagGreen}}\\hrule width\\headwidth height 1pt \\vspace{{4pt}}}}
}}
"""


def enhance_longtables_in_tex(tex: str) -> str:
    """
    Transforms any longtable environment in the document lacking \\endfirsthead
    into a robust multi-page table with repeated column headers on every page break.
    """
    pattern = re.compile(
        r'(\\begin\{longtable\}\{(.+?)\}\s*'
        r'\\caption\{(.+?)\}\s*(?:\\label\{([^}]+)\}\s*)?'
        r'(?:\\\\)?\s*\\hline\s*'
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

    return pattern.sub(replacer, tex)
