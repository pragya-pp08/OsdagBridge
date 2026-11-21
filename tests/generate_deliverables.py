import os
import sys
import shutil

SRC_DIR = r'D:\OsdagBridge\src'
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from osdagbridge.core.reports.report_generator import (
    ReportMetadata,
    ReportOptions,
    ReportRequest,
    build_report_payload,
    generate_report,
)
from osdagbridge.core.reports.plots import (
    generate_utilization_ratio_plot,
    generate_material_quantity_plots,
)
from osdagbridge.core.boq.boq_generator import calculate_material_quantities
from test_report_pipeline import get_sample_bridge_data

def generate_deliverable_report():
    deliverables_dir = r'D:\OsdagBridge\deliverables'
    assets_dir = os.path.join(deliverables_dir, 'assets')
    os.makedirs(assets_dir, exist_ok=True)

    inputs, outputs = get_sample_bridge_data()

    # Generate persistent high-res assets in deliverables/assets/
    quantities = calculate_material_quantities(inputs, outputs)
    inputs.update(quantities)

    steel_p, conc_p = generate_material_quantity_plots(quantities, assets_dir)
    ur_p = os.path.join(assets_dir, "utilization_ratio_summary.png")
    generate_utilization_ratio_plot([], ur_p)

    # Copy logos if available
    osdag_logo_src = os.path.join(SRC_DIR, 'osdagbridge', 'core', 'data', 'ResourceFiles', 'vectors', 'Osdag Logo.png')
    if os.path.exists(osdag_logo_src):
        shutil.copy2(osdag_logo_src, os.path.join(assets_dir, 'osdag_logo.png'))

    meta = ReportMetadata(
        project_name="Four-Lane Highway Bridge over River Crossing (NH-48)",
        project_location="Pune, Maharashtra (Latitude: 18.52 N, Longitude: 73.85 E)",
        designer="Structural Design Engineer, Bridge Division",
        client="National Highways Authority of India (NHAI)",
        company="FOSSEE OsdagBridge Engineering Team",
        job_number="OB-NH48-30M-REV1",
        subtitle="Detailed Engineering Calculation & Design Verification Report",
        additional_comments="Designed in full compliance with IRC:6-2017, IRC:22-2014, IRC:24-2010, and IS 800:2007 (Limit State Method).",
        report_date="2026-11-20",
        reviewer="Chief Bridge Engineer, FOSSEE / IIT Bombay",
    )

    options = ReportOptions(
        sections=['loads', 'analysis', 'design_checks', 'drawings'],
        include_figures=True,
        include_toc=True,
        include_pdf=True,
    )

    request = ReportRequest(
        metadata=meta,
        options=options,
        output_dir=deliverables_dir,
        file_stem="Report_After",
    )

    payload = build_report_payload(request, inputs, outputs)
    result = generate_report(payload, request)

    print("Generated Report TeX:", result.tex_path)
    print("Assets saved to:", assets_dir)
    print("Asset files:", os.listdir(assets_dir))

if __name__ == '__main__':
    generate_deliverable_report()
