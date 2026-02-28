"""
Akkermansia Analyzer Agent: Extracts and compares Akkermansia metrics across products.
"""

import pandas as pd
import numpy as np
from typing import Optional
from dataclasses import dataclass

from agents.data_loader import load_abundance_table, get_product_samples


@dataclass
class ProductAkkermansiaMetrics:
    """Akkermansia metrics for a single product."""

    product: str
    n_samples: int
    akkermansia_total_mean: float
    akkermansia_total_std: float
    akkermansia_muciniphila_mean: float
    akkermansia_muciniphila_std: float
    purity_pct: float  # % of microbiota that is Akkermansia
    rank: int


def filter_akkermansia_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Filter dataframe to only Akkermansia genus rows."""
    return df[df.index.str.contains("g__Akkermansia", case=False, na=False)]


def analyze_akkermansia(df: pd.DataFrame) -> dict:
    """
    Analyze Akkermansia abundance across all products.
    Returns metrics for total Akkermansia and key strain (A. muciniphila).
    """
    akk_df = filter_akkermansia_rows(df)
    if akk_df.empty:
        return {}

    product_samples = get_product_samples(df)

    # Competitor products only (exclude Control for comparison)
    competitor_products = [
        p for p in product_samples.keys()
        if p not in ("Control", "Unknown")
    ]

    results = {}
    for product in competitor_products:
        samples = product_samples.get(product, [])
        if not samples:
            continue

        # Total Akkermansia (sum of all Akkermansia species per sample)
        total_per_sample = akk_df[samples].sum(axis=0)
        total_mean = total_per_sample.mean()
        total_std = total_per_sample.std() if len(samples) > 1 else 0.0

        # A. muciniphila specifically (reference strain - most clinically relevant)
        # Match "muciniphila" at end of string, excluding muciniphila_A, muciniphila_B etc.
        muciniphila_rows = akk_df[
            akk_df.index.str.contains("muciniphila", na=False)
            & ~akk_df.index.str.contains("muciniphila_", na=False)
        ]
        if muciniphila_rows.empty:
            muciniphila_rows = akk_df[akk_df.index.str.contains("muciniphila", case=False, na=False)]
        muciniphila_per_sample = muciniphila_rows[samples].sum(axis=0)
        muciniphila_mean = muciniphila_per_sample.mean()
        muciniphila_std = muciniphila_per_sample.std() if len(samples) > 1 else 0.0

        # Purity: % of total microbiota that is Akkermansia
        total_community = df[samples].sum(axis=0)
        purity = (total_per_sample / total_community.replace(0, np.nan)).mean() * 100

        results[product] = ProductAkkermansiaMetrics(
            product=product,
            n_samples=len(samples),
            akkermansia_total_mean=total_mean,
            akkermansia_total_std=total_std,
            akkermansia_muciniphila_mean=muciniphila_mean,
            akkermansia_muciniphila_std=muciniphila_std,
            purity_pct=purity,
            rank=0,
        )

    # Rank by A. muciniphila proportion (primary quality metric)
    sorted_products = sorted(
        results.keys(),
        key=lambda p: results[p].akkermansia_muciniphila_mean,
        reverse=True,
    )
    for i, product in enumerate(sorted_products, 1):
        results[product].rank = i

    return results


def get_detailed_akkermansia_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    """Get per-species breakdown of Akkermansia for each product."""
    akk_df = filter_akkermansia_rows(df)
    if akk_df.empty:
        return pd.DataFrame()

    product_samples = get_product_samples(df)
    competitor_products = [
        p for p in product_samples.keys()
        if p not in ("Control", "Unknown")
    ]

    rows = []
    for product in competitor_products:
        samples = product_samples.get(product, [])
        if not samples:
            continue
        for taxon in akk_df.index:
            species_name = taxon.split(";")[-1].replace("s__", "") if ";" in taxon else taxon
            mean_abun = akk_df.loc[taxon, samples].mean()
            rows.append({
                "Product": product,
                "Taxon": species_name,
                "Mean_Relative_Abundance": mean_abun,
                "Mean_Percent": mean_abun * 100,
            })

    return pd.DataFrame(rows)
