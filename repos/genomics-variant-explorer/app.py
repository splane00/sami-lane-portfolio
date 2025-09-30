import pandas as pd
from dash import Dash, dcc, html, dash_table, Input, Output
import plotly.express as px


def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["clin_sig"] = df["clin_sig"].astype("category")
    return df


def create_app(data_path: str = "data/variants.csv") -> Dash:
    df = load_data(data_path)

    app = Dash(__name__)
    app.title = "Genomics Variant Explorer"

    app.layout = html.Div(
        className="app",
        children=[
            html.H1("Genomics Variant Explorer"),
            html.P(
                "Interactively explore harmonized variant data, filter based on gene, "
                "clinical significance, and impact score, and identify variants that "
                "merit follow-up."
            ),
            html.Div(
                className="controls",
                children=[
                    html.Div(
                        children=[
                            html.Label("Gene"),
                            dcc.Dropdown(
                                id="gene-filter",
                                options=[{"label": gene, "value": gene} for gene in sorted(df["gene"].unique())],
                                multi=True,
                                placeholder="Select one or more genes",
                            ),
                        ]
                    ),
                    html.Div(
                        children=[
                            html.Label("Clinical significance"),
                            dcc.Dropdown(
                                id="significance-filter",
                                options=[
                                    {"label": sig, "value": sig} for sig in sorted(df["clin_sig"].cat.categories)
                                ],
                                multi=True,
                                placeholder="Filter by clinical significance",
                            ),
                        ]
                    ),
                    html.Div(
                        children=[
                            html.Label("Minimum impact score"),
                            dcc.Slider(
                                id="impact-filter",
                                min=0,
                                max=1,
                                step=0.01,
                                value=0.6,
                                marks={0: "0.0", 0.5: "0.5", 1: "1.0"},
                                tooltip={"always_visible": False, "placement": "bottom"},
                            ),
                        ]
                    ),
                    html.Div(
                        children=[
                            html.Label("Phenotype contains"),
                            dcc.Input(
                                id="phenotype-filter",
                                type="text",
                                placeholder="e.g. cancer",
                                debounce=True,
                            ),
                        ]
                    ),
                ],
            ),
            dcc.Graph(id="variant-impact-plot"),
            dash_table.DataTable(
                id="variant-table",
                columns=[{"name": col.replace("_", " ").title(), "id": col} for col in df.columns],
                page_size=5,
                filter_action="native",
                sort_action="native",
                style_table={"overflowX": "auto"},
                style_cell={"textAlign": "left", "padding": "0.5rem"},
            ),
        ],
    )

    @app.callback(
        Output("variant-table", "data"),
        Output("variant-impact-plot", "figure"),
        Input("gene-filter", "value"),
        Input("significance-filter", "value"),
        Input("impact-filter", "value"),
        Input("phenotype-filter", "value"),
    )
    def update_outputs(selected_genes, selected_significance, min_impact, phenotype_text):
        filtered = df.copy()

        if selected_genes:
            filtered = filtered[filtered["gene"].isin(selected_genes)]
        if selected_significance:
            filtered = filtered[filtered["clin_sig"].isin(selected_significance)]
        if min_impact is not None:
            filtered = filtered[filtered["impact_score"] >= float(min_impact)]
        if phenotype_text:
            filtered = filtered[filtered["phenotype"].str.contains(phenotype_text, case=False, na=False)]

        table_data = filtered.to_dict("records")

        if filtered.empty:
            fig = px.scatter(
                filtered,
                x="position",
                y="impact_score",
                color="clin_sig",
                hover_data=["sample_id", "gene", "phenotype"],
                title="No variants match the filters",
            )
        else:
            fig = px.scatter(
                filtered,
                x="position",
                y="impact_score",
                color="clin_sig",
                size="impact_score",
                hover_data=["sample_id", "gene", "phenotype", "consequence"],
                title="Variant impact by genomic position",
                labels={
                    "position": "Genomic position",
                    "impact_score": "Impact score",
                    "clin_sig": "Clinical significance",
                },
            )

        fig.update_layout(margin=dict(l=40, r=20, t=60, b=40))
        return table_data, fig

    return app


def main():
    app = create_app()
    app.run_server(debug=True, host="0.0.0.0", port=8050)


if __name__ == "__main__":
    main()
