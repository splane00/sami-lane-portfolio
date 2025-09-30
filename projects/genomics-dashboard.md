# Genomics Variant Explorer Dashboard

This project demonstrates ability to build interactive dashboards for exploring genomic variant data. The workflow combines data wrangling, statistical summaries, and interactive visualization tailored for translational research teams.

## Highlights
- Cleaned and harmonized variant call format (VCF) files with phenotype metadata.
- Calculated population frequency summaries and annotated variants with ClinVar and gnomAD data sources.
- Built an interactive dashboard using Plotly Dash to filter variants by gene, consequence, and clinical significance.
- Implemented reproducible data processing pipelines using Jupyter notebooks and documented all steps for collaborators.

## Repository Structure
```
/etl                # Python scripts for ingesting and cleaning raw variant data
/notebooks          # Exploratory analysis and validation notebooks
/dashboard          # Plotly Dash application code
/docs               # User guide, deployment instructions, and screenshots
```

## Skills Demonstrated
- Python (pandas, plotly, dash)
- Data cleaning & integration
- Interactive data visualization
- Scientific communication

## Future Enhancements
- Automate variant annotation updates through scheduled workflows.
- Add support for exporting filtered variant tables to CSV and Excel formats.
- Integrate authentication for sharing dashboards with clinical partners.
