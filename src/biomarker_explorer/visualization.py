"""Visualization utilities for exploratory analysis and reporting."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import seaborn as sns
from sklearn.decomposition import PCA

from .config import VisualizationConfig
from .integration import IntegrationResult

sns.set_theme(style="whitegrid")


def _ensure_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def plot_outcome_distribution(
    clinical: pd.DataFrame, target_column: str, config: VisualizationConfig, output_dir: Path
) -> Path:
    fig, ax = plt.subplots(figsize=(6, 4))
    counts = clinical[target_column].value_counts().reset_index()
    counts.columns = [target_column, "count"]
    sns.barplot(data=counts, x=target_column, y="count", ax=ax)
    ax.set_title("Clinical outcome distribution")
    ax.set_xlabel(target_column)
    ax.set_ylabel("Samples")
    output_path = output_dir / "outcome_distribution"
    _save_matplotlib(fig, output_path, config.output_formats)
    plt.close(fig)
    return output_path


def plot_feature_importances(
    feature_importances: pd.DataFrame,
    config: VisualizationConfig,
    output_dir: Path,
) -> Path:
    if feature_importances.empty:
        return output_dir / "feature_importances"
    top = feature_importances.head(config.n_top_features)
    fig, ax = plt.subplots(figsize=(8, max(4, config.n_top_features * 0.25)))
    sns.barplot(data=top, y="feature", x="importance", ax=ax, orient="h")
    ax.set_title("Top feature importances")
    ax.set_xlabel("Importance score")
    ax.set_ylabel("Feature")
    output_path = output_dir / "feature_importances"
    _save_matplotlib(fig, output_path, config.output_formats)
    plt.close(fig)
    return output_path


def plot_correlation_heatmap(result: IntegrationResult, config: VisualizationConfig, output_dir: Path) -> Path:
    sample_count = min(200, len(result.combined_features))
    frame = result.combined_features.iloc[:sample_count]
    corr = frame.corr(method=config.correlation_method)
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(corr, ax=ax, cmap="coolwarm", center=0)
    ax.set_title(f"Feature correlation ({config.correlation_method})")
    output_path = output_dir / "correlation_heatmap"
    _save_matplotlib(fig, output_path, config.output_formats)
    plt.close(fig)
    return output_path


def plot_pca_projection(
    result: IntegrationResult,
    clinical: pd.DataFrame,
    target_column: str,
    output_dir: Path,
) -> Path:
    pca = PCA(n_components=2, random_state=0)
    coords = pca.fit_transform(result.combined_features)
    plot_df = pd.DataFrame(
        coords,
        columns=["PC1", "PC2"],
        index=result.combined_features.index,
    )
    plot_df = plot_df.join(clinical[[target_column]])
    fig = px.scatter(
        plot_df,
        x="PC1",
        y="PC2",
        color=target_column,
        hover_name=plot_df.index,
        title="PCA projection",
    )
    output_path = output_dir / "pca_projection.html"
    _ensure_dir(output_path)
    fig.write_html(str(output_path))
    return output_path


def _save_matplotlib(fig: plt.Figure, output_path: Path, formats: Iterable[str]) -> None:
    for fmt in formats:
        dest = output_path.with_suffix(f".{fmt}")
        _ensure_dir(dest)
        fig.savefig(dest, bbox_inches="tight", dpi=300)
