# Genomics Variant Explorer Dashboard

Hands-on prototype showcasing Sami Lane's ability to build interactive genomics dashboards that help translational teams triage variants quickly.

## Highlights
- Harmonizes variant calls with phenotype context and exposes intuitive filtering controls.
- Presents interactive scatter plots and sortable tables for rapidly prioritizing variants.
- Provides clear setup instructions and lightweight sample data to demonstrate the workflow end-to-end.

## Repository Structure
```
repos/genomics-variant-explorer/
├── app.py            # Dash application with filtering callbacks and visualizations
├── data/
│   └── variants.csv  # Sample harmonized variant dataset with phenotype context
├── README.md         # Project overview and run instructions
└── requirements.txt  # Reproducible Python dependencies
```

> **Note:** The dashboard now lives in its own standalone repository folder at
> `repos/genomics-variant-explorer/`, making it easy to publish as a dedicated
> GitHub project or share independently from the main portfolio.

## Skills Demonstrated
- Python (pandas, dash, plotly)
- Data wrangling & harmonization
- Interactive data visualization
- Scientific communication & documentation

## Future Enhancements
- Automate variant annotation refreshes via ClinVar and gnomAD APIs.
- Add export options for filtered variant tables (CSV, Excel).
- Containerize deployment for streamlined handoff to collaborators.
