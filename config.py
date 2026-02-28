"""
Configuration for the Akkermansia Supplement Comparative Analysis.
"""

from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent
ZYMO_DATA_ROOT = PROJECT_ROOT / "zr25501.250902"

# Primary abundance table path (optional; use --abundance to override)
ABUNDANCE_TABLE_PATH = (
    ZYMO_DATA_ROOT
    / "01.Pendulum.vs.Others.illumina.pe"
    / "All"
    / "Heatmaps_Subgroup1"
    / "5.Species"
    / "new_abun_table.tsv"
)

# Sample ID to product mapping (letter suffix convention)
PRODUCT_ABBREVIATIONS = {
    "P": "Pendulum",
    "K": "Ketrophy",
    "L": "Lifeatlas",
    "W": "Wsidche",
    "CTL": "Control",
}

# Report output
REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"

# Optional: path to sample metadata
SAMPLE_METADATA_PATH = PROJECT_ROOT / "data" / "sample_metadata.csv"
SAMPLE_DESCRIPTION_XLSX = PROJECT_ROOT / "akkermansia sample ID description.xlsx"
