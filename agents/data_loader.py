"""
Data Loader Agent: Discovers and loads Zymo microbiome data.
"""

import pandas as pd
from pathlib import Path
from typing import Optional
import re

from config import (
    ABUNDANCE_TABLE_PATH,
    PRODUCT_ABBREVIATIONS,
    SAMPLE_METADATA_PATH,
    SAMPLE_DESCRIPTION_XLSX,
)


def _load_sample_mapping_from_file() -> Optional[dict[str, str]]:
    """Load sample_id -> product mapping from CSV or Excel."""
    # Try CSV first
    if SAMPLE_METADATA_PATH.exists():
        df = pd.read_csv(SAMPLE_METADATA_PATH)
        if "sample_id" in df.columns and "product" in df.columns:
            return dict(zip(df["sample_id"].astype(str), df["product"].astype(str)))
    # Try Excel (from akkermansia sample ID description.xlsx)
    if SAMPLE_DESCRIPTION_XLSX.exists():
        try:
            df = pd.read_excel(SAMPLE_DESCRIPTION_XLSX)
            # Expect columns like Sample ID / sample_id and Product / product
            id_col = next((c for c in df.columns if "sample" in str(c).lower() or "id" in str(c).lower()), df.columns[0])
            prod_col = next((c for c in df.columns if "product" in str(c).lower()), df.columns[1] if len(df.columns) > 1 else None)
            if prod_col is not None:
                return dict(zip(df[id_col].astype(str), df[prod_col].astype(str)))
        except Exception:
            pass
    return None


_CUSTOM_SAMPLE_MAPPING: Optional[dict[str, str]] = None


def extract_product_from_sample_id(sample_id: str) -> str:
    """
    Extract product name from Zymo sample ID.
    Uses custom mapping from Excel/CSV if available; otherwise infers from suffix.
    Format: NUMBERS.LETTER+NUM (e.g., 238322001677.P1, 236191002863.CTL1)
    """
    global _CUSTOM_SAMPLE_MAPPING
    if _CUSTOM_SAMPLE_MAPPING is None:
        _CUSTOM_SAMPLE_MAPPING = _load_sample_mapping_from_file()
    if _CUSTOM_SAMPLE_MAPPING and str(sample_id) in _CUSTOM_SAMPLE_MAPPING:
        return _CUSTOM_SAMPLE_MAPPING[str(sample_id)]
    match = re.search(r"\.([A-Za-z]+)(\d*)$", sample_id)
    if match:
        abbrev = match.group(1)
        return PRODUCT_ABBREVIATIONS.get(abbrev, abbrev)
    return "Unknown"


def load_abundance_table(path: Optional[Path] = None) -> pd.DataFrame:
    """Load the species abundance table from Zymo TSV."""
    path = path or ABUNDANCE_TABLE_PATH
    if not path.exists():
        raise FileNotFoundError(f"Abundance table not found: {path}")

    df = pd.read_csv(path, sep="\t", index_col=0)
    return df


def load_sample_metadata(path: Optional[Path] = None) -> Optional[pd.DataFrame]:
    """Load sample metadata from CSV (if exported from Excel)."""
    path = path or SAMPLE_METADATA_PATH
    if path.exists():
        return pd.read_csv(path)
    return None


def get_short_sample_label(sample_id: str) -> str:
    """Extract short label from Zymo sample ID (e.g. 238322001677.P1 -> P1, 236191002863.CTL1 -> CTL1)."""
    match = re.search(r"\.([A-Za-z]+)(\d*)$", sample_id)
    if match:
        return match.group(1) + (match.group(2) or "")
    return str(sample_id)


def get_product_samples(df: pd.DataFrame) -> dict[str, list[str]]:
    """Map product names to their sample column IDs."""
    product_samples = {}
    for col in df.columns:
        product = extract_product_from_sample_id(col)
        product_samples.setdefault(product, []).append(col)
    return product_samples


def get_samples_ordered_by_product(
    df: pd.DataFrame,
    product_order: Optional[list[str]] = None,
) -> list[str]:
    """Return list of sample column IDs ordered by product then by sample number (P1,P2,...,K1,K2,...,CTL1,CTL2)."""
    product_samples = get_product_samples(df)
    if product_order is None:
        product_order = ["Pendulum", "Ketrophy", "Lifeatlas", "Wsidche", "Control"]
    ordered = []
    for product in product_order:
        if product not in product_samples:
            continue
        cols = product_samples[product]
        # Sort by short label so P1, P2, P3, P4
        cols = sorted(cols, key=lambda c: (get_short_sample_label(c), c))
        ordered.extend(cols)
    return ordered
