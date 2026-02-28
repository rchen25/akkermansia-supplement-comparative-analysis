#!/usr/bin/env python3
"""
Akkermansia supplement comparative analysis: load abundance table, analyze by product, generate reports.
"""

import argparse
from pathlib import Path

from config import PROJECT_ROOT
from agents.data_loader import load_abundance_table, get_product_samples
from agents.akkermansia_analyzer import analyze_akkermansia, get_detailed_akkermansia_breakdown
from agents.report_generator import generate_report, generate_pdf, generate_docx


def main():
    parser = argparse.ArgumentParser(
        description="Akkermansia supplement comparative analysis: generate quality report."
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=PROJECT_ROOT / "reports" / "akkermansia_quality_report.md",
        help="Output path for the report",
    )
    parser.add_argument(
        "--abundance",
        type=Path,
        default=None,
        help="Path to abundance TSV (default: Zymo path in config)",
    )
    parser.add_argument(
        "--no-report",
        action="store_true",
        help="Only run analysis, do not write report file",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("Akkermansia Supplement Comparative Analysis")
    print("=" * 60)

    print("\n[1/4] Loading abundance data...")
    df = load_abundance_table(args.abundance)
    product_samples = get_product_samples(df)
    print(f"      Loaded {len(df)} species, {len(df.columns)} samples")
    for product, samples in sorted(product_samples.items()):
        print(f"      - {product}: {len(samples)} samples")

    print("\n[2/4] Analyzing Akkermansia by product...")
    metrics = analyze_akkermansia(df)
    for product in sorted(metrics.keys(), key=lambda p: metrics[p].rank):
        m = metrics[product]
        print(f"      {product}: {m.akkermansia_muciniphila_mean * 100:.1f}% A. muciniphila (rank #{m.rank})")

    print("\n[3/4] Generating report...")
    report_path = None if args.no_report else args.report
    report_content = generate_report(output_path=report_path, abundance_path=args.abundance)

    if not args.no_report and report_path:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        pdf_path = report_path.with_suffix(".pdf")
        print("      Generating PDF...")
        try:
            generate_pdf(report_content, pdf_path, args.abundance)
            print(f"      PDF saved to: {pdf_path}")
        except Exception as e:
            print(f"      Warning: Could not generate PDF ({e})")
        docx_path = report_path.with_suffix(".docx")
        print("      Generating DOCX...")
        try:
            generate_docx(report_content, docx_path, args.abundance)
            print(f"      DOCX saved to: {docx_path}")
        except Exception as e:
            print(f"      Warning: Could not generate DOCX ({e})")

    print("\n[4/4] Done!")
    if pendulum := metrics.get("Pendulum"):
        print(f"\n  Pendulum ranks #1 with {pendulum.akkermansia_muciniphila_mean * 100:.2f}% A. muciniphila")
    if report_path:
        print(f"  Report: {report_path}")
        print(f"  PDF:    {report_path.with_suffix('.pdf')}")
        print(f"  DOCX:   {report_path.with_suffix('.docx')}")

    return 0


if __name__ == "__main__":
    exit(main())
