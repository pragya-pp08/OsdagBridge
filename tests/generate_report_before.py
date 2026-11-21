import os
import re

def generate_report_before():
    after_path = r'E:\OsdagBridge\deliverables\Report_After.tex'
    before_path = r'E:\OsdagBridge\deliverables\Report_Before.tex'

    with open(after_path, 'r', encoding='utf-8') as f:
        tex = f.read()

    # 1. Revert preamble geometry and footrule (restore the margin=1in and negative \vspace that caused Page 30 bleeding)
    old_preamble_geom = r"""\usepackage[a4paper, margin=1in]{geometry}
\usepackage{graphicx}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{booktabs}
\usepackage{array}
\usepackage{tabularx}
\usepackage{float}
\usepackage{fancyhdr}
\usepackage[hidelinks]{hyperref}
\usepackage{xcolor}
\usepackage{setspace}
\usepackage{enumitem}
\usepackage{caption}

\captionsetup{
    labelfont=bf,
    justification=raggedright,
    singlelinecheck=false,
    format=plain
}
\usepackage{subcaption}
\usepackage{multirow}
\usepackage{colortbl}
\usepackage{longtable}
\setlength{\LTleft}{\fill}
\setlength{\LTright}{\fill}
\usepackage{titlesec}
\usepackage{titletoc}
\usepackage{lastpage}
\usepackage{makecell}
\usepackage{etoolbox}
\usepackage{needspace}

\numberwithin{table}{chapter}
\numberwithin{figure}{chapter}
% Table layout and spacing: consistent padding, row height, and longtable pre/post skips
\setlength{\tabcolsep}{6pt}
\renewcommand{\arraystretch}{1.12}
\setlength{\LTpre}{0pt}
\setlength{\LTpost}{6pt}
% Table rules (outline thickness) and small extra row height for clarity
\setlength{\arrayrulewidth}{0.5pt}
\setlength{\extrarowheight}{0.6pt}

% Prevent tables from overflowing past the page bottom:
% if fewer than 5 baseline-skips remain, break to the next page first.
\BeforeBeginEnvironment{table}{\needspace{5\baselineskip}}
\BeforeBeginEnvironment{longtable}{\needspace{5\baselineskip}}

\definecolor{osdagGreen}{HTML}{91B014}

\fancypagestyle{main}{
  \fancyhf{}
  \fancyhead[L]{Four-Lane Highway Bridge over River Crossing (NH-48) $|$ OB-NH48-30M-REV1}
  \fancyhead[R]{2026-11-20 $|$ Detailed Engineering Calculation \& Design Verification Report}
  \fancyfoot[L]{Osdag $|$ FOSSEE $|$ Indian Institute of Technology Bombay}
  \fancyfoot[R]{Page \thepage\ of \pageref{LastPage}}
  \renewcommand{\headrule}{\color{osdagGreen}\hrule width\headwidth height 1pt \vspace{2pt}}
  \renewcommand{\footrule}{%
    \ifbool{hasSDonPage}{%
      \vspace{-20pt}%
      \hbox to \headwidth{\textcolor{black}{\footnotesize\textit{* Software default value}}\hfil}%
      \vspace{4pt}%
    }{%
      \vspace{-8pt}%
    }%
    \color{osdagGreen}\hrule width\headwidth height 1pt \vspace{6pt}%
  }
}
\fancypagestyle{plain}{
  \fancyhf{}
  \fancyhead[L]{Four-Lane Highway Bridge over River Crossing (NH-48) $|$ OB-NH48-30M-REV1}
  \fancyhead[R]{2026-11-20 $|$ Detailed Engineering Calculation \& Design Verification Report}
  \fancyfoot[L]{Osdag $|$ FOSSEE $|$ Indian Institute of Technology Bombay}
  \fancyfoot[R]{Page \thepage\ of \pageref{LastPage}}
  \renewcommand{\headrule}{\color{osdagGreen}\hrule width\headwidth height 1pt \vspace{2pt}}
  \renewcommand{\footrule}{%
    \ifbool{hasSDonPage}{%
      \vspace{-20pt}%
      \hbox to \headwidth{\textcolor{black}{\footnotesize\textit{* Software default value}}\hfil}%
      \vspace{4pt}%
    }{%
      \vspace{-8pt}%
    }%
    \color{osdagGreen}\hrule width\headwidth height 1pt \vspace{6pt}%
  }
}
\fancypagestyle{firstpage}{
  \fancyhf{}
  \renewcommand{\headrulewidth}{0pt}
  \fancyfoot[L]{Osdag $|$ FOSSEE $|$ Indian Institute of Technology Bombay}
  \fancyfoot[R]{Page \thepage\ of \pageref{LastPage}}
  \renewcommand{\footrule}{\vspace{-8pt}\color{osdagGreen}\hrule width\headwidth height 1pt \vspace{6pt}}
}"""

    # Replace new preamble with old preamble
    preamble_pattern = re.compile(r'\\usepackage\[a4paper,left=20mm.*?\\renewcommand\{\\footrule\}\{\\color\{osdagGreen\}\\hrule width\\headwidth height 1pt \\vspace\{4pt\}\}\s*\}', re.DOTALL)
    tex = preamble_pattern.sub(old_preamble_geom, tex)

    # 2. Strip repeated headers (\endfirsthead, \endhead, \endfoot, \endlastfoot) to reproduce Issue 1
    # Replace longtable headers that have \endfirsthead ... \endlastfoot with simple caption and header row
    pattern_headers = re.compile(
        r'(\\caption\{.+?\}\s*(?:\\label\{[^}]+\}\s*)?\\\\\s*\\hline\s*.+?\\\\[0-9a-z]*\s*\\hline)\s*'
        r'\\endfirsthead\s*'
        r'\\multicolumn\{.+?\}\s*'
        r'\\hline\s*.+?\\\\[0-9a-z]*\s*\\hline\s*'
        r'\\endhead\s*'
        r'\\hline\s*\\multicolumn\{.+?\}\s*'
        r'\\endfoot\s*'
        r'\\hline\s*\\endlastfoot',
        re.DOTALL
    )
    tex = pattern_headers.sub(r'\1', tex)

    # 3. Revert Chapter 3: Replace separated tables with the original merged Live Loads (LL) table
    old_ch3_ll = r"""\vspace{1em}
\begin{longtable}{|L{5.5cm}|p{10.0cm}|}
\caption{\textbf{Live Loads (LL)}}
\hline
\textbf{parameter} & \textbf{value} \\
\hline
\textnormal{Vehicles Considered} & IRC Class A, IRC Class 70R (Wheeled) \\[6pt]
\hline
\textnormal{Impact Factor (IRC 6)} & 1.154 \\[6pt]
\hline
\textnormal{Braking Load (IRC 6)} & 200.00 kN \\[6pt]
\hline
\textnormal{Footpath Live Load (if applicable)} & 4.000 kN/m\textsuperscript{2} \\[6pt]
\hline
\end{longtable}"""

    pattern_ch3 = re.compile(r'\\begin\{longtable\}\{\|L\{3\.6cm\}.*?\\end\{longtable\}\s*\\noindent\\textit\{Note: Live load vehicles are populated.*?\\begin\{longtable\}\{\|L\{5\.0cm\}.*?\\end\{longtable\}', re.DOTALL)
    tex = pattern_ch3.sub(old_ch3_ll, tex)

    # 4. Remove Section 5.5 UR plot
    pattern_sec55_fig = re.compile(r'\\begin\{figure\}\[H\]\s*\\centering\s*\\includegraphics\[width=0\.96\\textwidth\]\{assets/utilization_ratio_summary\.png\}.*?\\end\{figure\}', re.DOTALL)
    tex = pattern_sec55_fig.sub('', tex)

    # 5. Remove Chapter 7 Material Quantity charts
    pattern_ch7_figs = re.compile(r'\\clearpage\s*\\section\{Material Quantity Visualizations\}.*?\\end\{figure\}\s*\\vspace\{0\.8em\}\s*\\begin\{figure\}\[H\].*?\\end\{figure\}', re.DOTALL)
    tex = pattern_ch7_figs.sub('', tex)

    with open(before_path, 'w', encoding='utf-8') as f:
        f.write(tex)

    print("Report_Before.tex successfully generated!")
    print(f"Size: {len(tex)} characters")

if __name__ == '__main__':
    generate_report_before()
