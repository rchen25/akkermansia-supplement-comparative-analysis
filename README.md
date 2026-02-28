# Akkermansia Supplement Comparative Analysis

Compares *Akkermansia muciniphila* content across supplement products using species-level abundance tables. Produces Markdown, PDF, and DOCX reports.

**Default data (in repo):**  
`zr25501.250902/01.Pendulum.vs.Others.illumina.pe/All/Heatmaps_Subgroup1/5.Species/new_abun_table.tsv` — species-level abundance table used by the analysis (Zymo Pendulum vs Others, 18 samples).

**Run (requires [uv](https://docs.astral.sh/uv/)):**

```bash
# Use default data in repo
uv run python run_analysis.py

# Or point to your own TSV
uv run python run_analysis.py --abundance path/to/species_abundance.tsv
```

Reports are written to `reports/`. Sample IDs: P=Pendulum, K=Ketrophy, L=Lifeatlas, W=Wsidche, CTL=Control.
