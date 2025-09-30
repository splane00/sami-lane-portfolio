# Genomics Variant Explorer Dashboard

An interactive [Dash](https://dash.plotly.com/) prototype for filtering, prioritizing, and visualizing genomic variants. The app demonstrates how harmonized variant call (VCF) data and phenotype annotations can be combined to support translational genomics teams during triage.

## Features
- Multi-select filtering by gene and clinical significance
- Minimum impact score slider to focus on high-priority variants
- Free-text phenotype search to match cohorts of interest
- Interactive scatter plot summarizing variant impact by genomic position
- Data table with native sorting and column-level filtering

## Getting started

### 1. Install dependencies
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Launch the dashboard
```bash
python app.py
```

Navigate to http://127.0.0.1:8050 to interact with the dashboard.

## Project structure
```
repos/genomics-variant-explorer/
├── app.py               # Dash application entry point
├── data/
│   └── variants.csv     # Example harmonized variant dataset
├── README.md            # Project overview and setup instructions
└── requirements.txt     # Python dependencies
```

## Publish as a dedicated repo
```bash
cd repos/genomics-variant-explorer
git init
git add .
git commit -m "Initial commit: Genomics Variant Explorer"
```

After creating the initial commit you can add a remote (e.g., GitHub) and push
to make the dashboard available outside of this portfolio repository.

## Next steps
- Integrate live variant annotation services (ClinVar, gnomAD)
- Add cohort-level summary statistics and exportable reports
- Containerize with Docker for reproducible deployment
