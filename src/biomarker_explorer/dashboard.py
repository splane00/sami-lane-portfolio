"""Streamlit dashboard for interactive biomarker exploration."""

from __future__ import annotations

import argparse
import io

import pandas as pd
import plotly.express as px
import streamlit as st
from sklearn.decomposition import PCA

from .pipeline import run_pipeline


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--config", type=str, default="configs/demo_config.yaml")
    return parser.parse_known_args()[0]


@st.cache_resource(show_spinner=True)
def load_results(config_path: str):
    return run_pipeline(config_path, write_outputs=False, verbose=False)


def main() -> None:
    args = _parse_args()
    st.set_page_config(page_title="Multi-Omics Biomarker Explorer", layout="wide")
    st.title("🧬 Multi-Omics Biomarker Explorer")
    st.caption(
        "Integrate RNA-seq, DNA methylation, and somatic mutation data to uncover candidate biomarkers."
    )

    result = load_results(args.config)
    target_column = result.config.modeling.target_column

    st.sidebar.header("Controls")
    top_k = st.sidebar.slider("Top features", min_value=5, max_value=100, value=20, step=5)
    show_predictions = st.sidebar.checkbox("Show test predictions", value=True)

    metrics_cols = st.columns(len(result.model.metrics))
    for col, (name, value) in zip(metrics_cols, result.model.metrics.items()):
        col.metric(name.replace("_", " ").title(), f"{value:.3f}")

    st.subheader("Modality summary")
    st.dataframe(result.feature_summary, use_container_width=True)

    st.subheader("Top feature importances")
    feature_df = result.model.feature_importances.head(top_k).iloc[::-1]
    fig = px.bar(
        feature_df,
        x="importance",
        y="feature",
        orientation="h",
        labels={"importance": "Importance", "feature": "Feature"},
        title=f"Top {top_k} features",
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("PCA projection")
    pca = PCA(n_components=2, random_state=0)
    coords = pca.fit_transform(result.integration.combined_features)
    projection = pd.DataFrame(coords, columns=["PC1", "PC2"], index=result.integration.combined_features.index)
    projection[target_column] = result.integration.clinical.data[target_column]
    fig_pca = px.scatter(
        projection,
        x="PC1",
        y="PC2",
        color=target_column,
        hover_name=projection.index,
        title="Samples in PCA space",
    )
    st.plotly_chart(fig_pca, use_container_width=True)

    if show_predictions:
        st.subheader("Held-out predictions")
        st.dataframe(result.model.test_predictions, use_container_width=True)

    st.subheader("Download integrated feature matrix")
    buffer = io.StringIO()
    result.integration.combined_features.to_csv(buffer)
    st.download_button(
        "Download CSV",
        buffer.getvalue(),
        file_name="integrated_features.csv",
        mime="text/csv",
    )


if __name__ == "__main__":  # pragma: no cover - Streamlit entry point
    main()
