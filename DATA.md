# Data and large files

This repo only tracks the **species-level abundance table** needed to regenerate the report tables and figures:

- `zr25501.250902/01.Pendulum.vs.Others.illumina.pe/All/Heatmaps_Subgroup1/5.Species/new_abun_table.tsv`

## Files over GitHub’s 100 MB limit (not in repo)

The following types of file are **ignored** (see `.gitignore`) because they typically exceed GitHub’s 100 MB limit:

| Type | Extension(s) | Description |
|------|--------------|-------------|
| Alignments | `.bam`, `.bai`, `.sam`, `.cram`, `.crai` | Aligned sequencing reads / indexes |
| Raw reads | `.fastq`, `.fastq.gz`, `.fq`, `.fq.gz` | Raw or compressed reads |
| Variants | `.vcf`, `.vcf.gz`, `.tbi` | Variant calls / indexes |
| Large arrays | `.h5`, `.hdf5` | HDF5 tables or arrays |
| Archives | `.zip`, `.tar`, `.tar.gz`, `.tar.bz2` | Compressed data dumps |
| Zymo FunctionalPathway | `FunctionalPathway/RawData/gene_fam_cpm*.tsv`, `species_gene_fam_cpm*.tsv` | 50–150 MB pathway tables (not needed for report) |

**How to get them:** Obtain the full Zymo output (e.g. `zr25501.250902`) from the original sequencing delivery or your lab’s copy. Place it in this repo root so the path  
`zr25501.250902/01.Pendulum.vs.Others.illumina.pe/All/Heatmaps_Subgroup1/5.Species/new_abun_table.tsv`  
exists, or run the pipeline with  
`uv run python run_analysis.py --abundance /path/to/new_abun_table.tsv`.
