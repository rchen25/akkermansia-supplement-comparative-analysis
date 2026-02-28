"""
Chart generation for Akkermansia quality report.
"""

from pathlib import Path
from typing import Optional

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from agents.data_loader import get_short_sample_label, get_samples_ordered_by_product, extract_product_from_sample_id
from agents.akkermansia_analyzer import filter_akkermansia_rows


# Publication-style defaults
plt.rcParams.update({
    "font.size": 10,
    "axes.titlesize": 11,
    "axes.labelsize": 10,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 9,
    "figure.dpi": 150,
})


def _product_order(metrics: dict) -> list[str]:
    """Return product names ordered by rank (Pendulum first)."""
    return sorted(metrics.keys(), key=lambda p: metrics[p].rank)


def plot_muciniphila_comparison(
    metrics: dict,
    output_path: Path,
) -> Path:
    """
    Bar chart: A. muciniphila relative abundance (%) by product.
    """
    order = _product_order(metrics)
    products = [order[i] for i in range(len(order))]
    means = [metrics[p].akkermansia_muciniphila_mean * 100 for p in products]
    stds = [metrics[p].akkermansia_muciniphila_std * 100 for p in products]
    colors = ["#2b6cb0" if p == "Pendulum" else "#718096" for p in products]

    fig, ax = plt.subplots(figsize=(5, 3.5))
    x = np.arange(len(products))
    bars = ax.bar(x, means, yerr=stds, capsize=4, color=colors, edgecolor="black", linewidth=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(products, rotation=15, ha="right")
    ax.set_ylabel("A. muciniphila relative abundance (%)")
    ax.set_xlabel("Product")
    ax.set_title("Akkermansia muciniphila content by product")
    ax.set_ylim(0, 105)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output_path, bbox_inches="tight", dpi=150)
    plt.close()
    return output_path


def plot_strain_breakdown(
    breakdown_df: pd.DataFrame,
    output_path: Path,
    product_order: Optional[list[str]] = None,
) -> Path:
    """
    Stacked bar chart: Akkermansia strain composition by product.
    """
    if breakdown_df.empty:
        return Path(output_path)

    pivot = breakdown_df.pivot_table(
        index="Taxon", columns="Product", values="Mean_Percent", aggfunc="first"
    ).fillna(0)
    if product_order:
        pivot = pivot[[p for p in product_order if p in pivot.columns]]
    products = list(pivot.columns)
    taxa = list(pivot.index)

    # Colors for strains (distinct)
    strain_colors = {
        "Akkermansia muciniphila": "#2b6cb0",
        "Akkermansia muciniphila_A": "#718096",
        "Akkermansia sp905200945": "#a0aec0",
    }
    colors = [strain_colors.get(t, "#cbd5e0") for t in taxa]

    fig, ax = plt.subplots(figsize=(5.5, 3.5))
    x = np.arange(len(products))
    width = 0.6
    bottom = np.zeros(len(products))

    for i, taxon in enumerate(taxa):
        vals = pivot.loc[taxon].values
        ax.bar(x, vals, width, bottom=bottom, label=taxon, color=colors[i % len(colors)])
        bottom += vals

    ax.set_xticks(x)
    ax.set_xticklabels(products, rotation=15, ha="right")
    ax.set_ylabel("Relative abundance (%)")
    ax.set_xlabel("Product")
    ax.set_title("Akkermansia strain composition by product")
    ax.legend(loc="upper right", frameon=True, fancybox=False, edgecolor="gray")
    ax.set_ylim(0, 105)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output_path, bbox_inches="tight", dpi=150)
    plt.close()
    return output_path


def _classify_akkermansia_taxon(taxon_name: str) -> str:
    """Map taxon index to segment label: A. muciniphila (ref), A. muciniphila_A, A. sp905200945, or Other."""
    if "muciniphila" in taxon_name and "muciniphila_" not in taxon_name:
        return "A. muciniphila"
    if "muciniphila_A" in taxon_name:
        return "A. muciniphila_A"
    if "sp905200945" in taxon_name:
        return "A. sp905200945"
    return "Other Akkermansia"


def plot_individual_abundance_stacked_hbar(
    df: pd.DataFrame,
    output_path: Path,
    product_order: Optional[list[str]] = None,
) -> Path:
    """
    Stacked horizontal bar chart: individual sample abundances of Akkermansia strains + Other.
    Y-axis = samples grouped by product (P1–P4, K1–K4, L1–L4, W1–W4, CTL1–CTL2); X-axis = 0–100%.
    """
    akk_df = filter_akkermansia_rows(df)
    if akk_df.empty:
        return Path(output_path)

    samples_ordered = get_samples_ordered_by_product(df, product_order=product_order)
    if not samples_ordered:
        return Path(output_path)

    # Segment order and colors (match reference: dark brown = ref strain, gray = A_, light blue = sp, light gray = Other)
    segment_order = ["A. muciniphila", "A. muciniphila_A", "A. sp905200945", "Other Akkermansia", "Other"]
    segment_colors = {
        "A. muciniphila": "#5c4033",
        "A. muciniphila_A": "#718096",
        "A. sp905200945": "#93c5fd",
        "Other Akkermansia": "#cbd5e0",
        "Other": "#e2e8f0",
    }

    # Build per-sample abundances for each segment
    n_samples = len(samples_ordered)
    segment_data = {seg: np.zeros(n_samples) for seg in segment_order}

    for j, col in enumerate(samples_ordered):
        total_akk = 0.0
        for taxon_idx in akk_df.index:
            val = akk_df.loc[taxon_idx, col]
            if isinstance(val, (int, float)) and val > 0:
                seg = _classify_akkermansia_taxon(taxon_idx)
                if seg not in segment_data:
                    seg = "Other Akkermansia"
                segment_data[seg][j] += val
                total_akk += val
        segment_data["Other"][j] = max(0.0, 1.0 - total_akk)

    # Y-axis labels: short sample IDs; group labels for spacing
    y_labels = [get_short_sample_label(c) for c in samples_ordered]
    product_samples = {}
    for col in samples_ordered:
        prod = extract_product_from_sample_id(col)
        product_samples.setdefault(prod, []).append(get_short_sample_label(col))

    fig, ax = plt.subplots(figsize=(7, 5))
    y_pos = np.arange(n_samples)[::-1]  # top = first sample
    left = np.zeros(n_samples)

    for seg in segment_order:
        vals = segment_data[seg] * 100
        ax.barh(y_pos, vals, left=left, height=0.7, label=seg, color=segment_colors.get(seg, "#cbd5e0"))
        left += vals

    ax.set_yticks(y_pos)
    ax.set_yticklabels(y_labels, fontsize=9)
    ax.set_xlim(0, 100)
    ax.set_xlabel("Relative abundance (%)")
    ax.set_ylabel("Sample")
    ax.set_title("Individual sample abundances: Akkermansia strains and other taxa")
    ax.legend(loc="lower right", ncol=2, fontsize=8, frameon=True, edgecolor="gray")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()

    # Add product group labels on the right
    if product_order is None:
        product_order = ["Pendulum", "Ketrophy", "Lifeatlas", "Wsidche", "Control"]
    group_colors = {"Pendulum": "#7c3aed", "Ketrophy": "#84cc16", "Lifeatlas": "#f97316", "Wsidche": "#2563eb", "Control": "#dc2626"}
    idx = 0
    for prod in product_order:
        if prod not in product_samples:
            continue
        n = len(product_samples[prod])
        y_lo = y_pos[idx + n - 1] - 0.35
        y_hi = y_pos[idx] + 0.35
        ax.axhspan(y_lo, y_hi, xmin=1.01, xmax=1.06, color=group_colors.get(prod, "#e2e8f0"), transform=ax.get_yaxis_transform(), clip_on=False)
        ax.text(1.035, (y_pos[idx] + y_pos[idx + n - 1]) / 2, prod, transform=ax.get_yaxis_transform(), fontsize=8, va="center", ha="left")
        idx += n

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, bbox_inches="tight", dpi=150)
    plt.close()
    return output_path


def generate_all_figures(
    metrics: dict,
    breakdown_df: pd.DataFrame,
    figures_dir: Path,
    abundance_df: Optional[pd.DataFrame] = None,
) -> dict[str, Optional[Path]]:
    """Generate all figures; return dict of figure label -> path (or None)."""
    figures_dir = Path(figures_dir)
    order = _product_order(metrics) if metrics else None

    path_muciniphila = figures_dir / "figure1_muciniphila_by_product.png"
    path_strain = figures_dir / "figure2_strain_breakdown.png"
    path_individual = figures_dir / "figure3_individual_sample_abundance.png"

    out = {"figure1": None, "figure2": None, "figure3": None}
    if metrics:
        plot_muciniphila_comparison(metrics, path_muciniphila)
        out["figure1"] = path_muciniphila
    if not breakdown_df.empty:
        plot_strain_breakdown(breakdown_df, path_strain, product_order=order)
        out["figure2"] = path_strain
    if abundance_df is not None and not abundance_df.empty:
        # Use default product order including Control (order from metrics excludes Control)
        plot_individual_abundance_stacked_hbar(abundance_df, path_individual, product_order=None)
        out["figure3"] = path_individual
    return out
