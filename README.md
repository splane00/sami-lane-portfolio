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
# Samantha (Sami) Lane – Portfolio

Welcome to my portfolio! I am a Master's student in Bioinformatics at Johns Hopkins University with interests in genomics, women’s health, and computational biology. This repository highlights selected projects that showcase my skills in Python, data analysis, bioinformatics pipelines, and software development.  

---

## Projects

### Bioinformatics
- [**BTN1A1 Gene Analysis**](https://github.com/splane00/bioinfo_projects/blob/main/BTN1A1-analysis.md) - *Intro to Bioinformatics coursework* - in progress!  
  Explored gene structure, SNPs, and protein domains using Ensembl, NCBI, and UCSC Genome Browser.  
  *Skills:* Genomic databases, sequence analysis, literature integration.

### Software Development  
- [**Huffman Encoding Tree Implementation**](https://github.com/splane00/data-struc-3) - *Data Structures coursework*  
  Python implementation of a Huffman tree for text compression and decompression. The program builds an encoding tree from character frequencies, generates binary codes, and encodes/decodes files while reporting compression results.  
  *Skills:* Python, binary trees, greedy algorithms, file I/O, modular design.
- [**Quicksort vs. Natural Merge Sort**](https://github.com/splane00/data-struc-4) - *Data Structures coursework*  
  Python project comparing the performance of Quicksort and Natural Merge Sort on different input datasets. The program measures runtime and analyzes efficiency based on input size and order.  
  *Skills:* Python, sorting algorithms, algorithm analysis, runtime measurement, data structures.
- [**Prefix to Postfix Converter**](https://github.com/splane00/data-struc-1) - *Data Structures coursework*  
  Python program that converts prefix expressions to postfix form using a stack-based approach. Demonstrates parsing, validation, and expression conversion with proper error handling.  
  *Skills:* Python, stacks, expression parsing, algorithm design, modular programming.  
- [**Stack Implementation**](https://github.com/splane00/data-struc-2) - *Data Structures coursework*  
  Python program implementing a stack data structure with operations for push, pop, peek, and error handling. Includes file input/output to test stack functionality with expression evaluation.  
*Skills:* Python, stacks, data structures, file I/O, modular programming.  

### Data Analysis and Visualization  
- **Exploratory Data Analysis With Python and Pandas** - Coursera Project Network - coming soon!  
  *Skills:* Python, Pandas, Numpy, Seaborn, Matploptlib, data wrangling, data cleaning, tabular datasets, statistical analysis
- **Data Cleaning in Excel: Techniques to Clean Messy Data** - Coursera Project Network - coming soon!  
  *Skills:* Microsoft Excel, Excel formulas, automation techniques, data cleaning  

### Undergraduate Projects
- **Literature Review:** ["Ethical Implications of Clinician Responses to Patients Presenting with Suicidal Ideation"](https://github.com/splane00/undergrad/blob/main/BHUM%20Lit%20Review.pdf)
- **Literature Review:** "Feasibility of Using Pharmacogenomics as Standard Practice in Psychiatric Healthcare" - coming soon!
- **Organic Chemistry Research:** [“Optimization of Alkylation of Ammonia and Amines Reaction to Selectively Form Ammonium Salts”](https://github.com/splane00/undergrad/blob/main/Optimization%20of%20Alkylation%20OCII.pdf)
- **Organic Chemistry Research:** [“Optimization of Alcohol Reagent in Williamson Ether Synthesis”](https://github.com/splane00/undergrad/blob/main/Williamson%20Ether%20Synthesis%20OCII.pdf)

---

## Skills
- **Languages:** Python, SQL, Java, JavaScript (React, Next.js)  
- **Libraries/Frameworks:** Pandas, NumPy, Scikit-learn, Seaborn, Matplotlib  
- **Bioinformatics Tools:** BLAST, FASTA, Ensembl, UCSC Genome Browser, NCBI/Entrez, ENCODE, WashU Epigenome Browser  
- **Other:** Git/GitHub, Firebase, Data Visualization, Cloud Deployment

---

## Contact me
- Email: slane21@jh.edu  
- [GitHub](https://github.com/splane00)   
- [LinkedIn](https://www.linkedin.com/in/samantha-lane-917771155/)  
