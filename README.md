# Multi-Omics Biomarker Explorer

Integrate RNA-seq expression, DNA methylation, and somatic mutation profiles to discover potential biomarkers for a specific cancer type. This repository contains a reproducible Python toolkit and optional Streamlit dashboard for end-to-end multi-omics exploration using public GEO/TCGA-style datasets or institution-specific cohorts.

## Why this project matters

Multi-omics integration is essential for connecting molecular alterations with clinical phenotypes. The Biomarker Explorer demonstrates:

- Practical bioinformatics data wrangling across heterogeneous assay types.
- Feature harmonization and modeling workflows that surface candidate biomarkers.
- Reusable visualization utilities for communicating findings to collaborators.

The project builds on foundational experience with SNP and gene-expression analytics and extends it into a more realistic translational research scenario.

## Features

- **Configurable data ingestion** for RNA-seq counts/TPM, methylation beta values, and mutation calls.
- **Preprocessing utilities** for filtering, transformation, batch correction hooks, and clinical metadata alignment.
- **Feature integration** via concatenation, scaling, and modality-aware feature selection.
- **Modeling toolkit** with scikit-learn pipelines for supervised biomarker discovery (logistic regression, random forest, elastic net).
- **Visualization helpers** powered by seaborn and Plotly for exploratory analysis and model interpretation.
- **Streamlit dashboard (optional stretch goal)** for interactive exploration of integrated cohorts.
- **Synthetic demo dataset generator** for fast experimentation without external downloads.

## Repository structure

```text
.
├── pyproject.toml                  # Project metadata and dependencies
├── README.md
├── scripts/
│   └── generate_synthetic_multiomics.py  # Creates demo RNA-seq, methylation, mutation, clinical CSVs
├── src/
│   └── biomarker_explorer/
│       ├── __init__.py
│       ├── config.py
│       ├── data_io.py
│       ├── preprocessing.py
│       ├── integration.py
│       ├── modeling.py
│       ├── visualization.py
│       ├── pipeline.py
│       └── dashboard.py
└── tests/
    └── test_pipeline.py
```

## Getting started

1. **Create and activate a virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows use .venv\Scripts\activate
   ```

2. **Install the project in editable mode**
   ```bash
   pip install -e .
   ```

3. **Generate synthetic demo data (optional but recommended)**
   ```bash
   python scripts/generate_synthetic_multiomics.py --out-dir data/demo --seed 17
   ```

4. **Run the end-to-end analysis pipeline**
   ```bash
   python -m biomarker_explorer.pipeline \
       --config configs/demo_config.yaml
   ```

   The pipeline will read the YAML configuration, load the CSV inputs, preprocess and integrate features, fit the specified models, and write all outputs into the configured results directory.

5. **Launch the interactive dashboard** (requires Streamlit)
   ```bash
   streamlit run src/biomarker_explorer/dashboard.py -- \
       --config configs/demo_config.yaml
   ```

## Configuration

Define cohorts via YAML files (see `configs/demo_config.yaml` once generated). Key fields include:

- `rna_seq.path`: Path to the RNA-seq expression matrix (samples × genes).
- `methylation.path`: Path to the methylation beta-value matrix (samples × CpG sites).
- `mutation.path`: Path to the mutation matrix (samples × genes; binary or counts).
- `clinical.path`: Clinical metadata with at least `sample_id` and `outcome` columns.
- `feature_selection`: Options for variance filtering or selecting top-k features per modality.
- `modeling`: Choice of estimator, cross-validation settings, and evaluation metrics.
- `results_dir`: Directory where outputs (merged matrices, metrics, feature importances, plots) are written.

Use the demo configuration as a template and adapt the file paths and schema for your cancer cohort.

## Development roadmap

- Add automated data downloaders for TCGA via the Genomic Data Commons API.
- Incorporate pathway-level feature aggregation (e.g., GSVA scores).
- Extend modeling support to survival analysis (Cox proportional hazards, random survival forests).
- Enable cloud-friendly execution via Snakemake or Nextflow wrappers.

## Contributing & support

Contributions, bug reports, and feature requests are welcome via GitHub issues and pull requests. For questions, contact `slane21@jh.edu` or open a discussion thread.

## License

This repository is distributed under the MIT License. See `LICENSE` for details.
