"""Command-line entry point for the biomarker explorer pipeline."""

from __future__ import annotations

import argparse
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Optional

from .config import PipelineConfig, VisualizationConfig, load_config
from .data_io import ClinicalTable, OmicsTable, load_clinical_table, load_omics_table, write_table
from .integration import IntegrationResult, compute_feature_summary, integrate_modalities
from .modeling import ModelResult, train_model
from .visualization import (
    plot_correlation_heatmap,
    plot_feature_importances,
    plot_outcome_distribution,
    plot_pca_projection,
)

logger = logging.getLogger(__name__)


@dataclass
class PipelineResult:
    config: PipelineConfig
    integration: IntegrationResult
    model: ModelResult
    feature_summary: pd.DataFrame
    outputs: Dict[str, Path]


def _configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")


def _load_modalities(config: PipelineConfig) -> tuple[ClinicalTable, list[OmicsTable]]:
    clinical = load_clinical_table(config.clinical)
    tables = [
        load_omics_table("rna_seq", config.rna_seq),
        load_omics_table("methylation", config.methylation),
        load_omics_table("mutation", config.mutation),
    ]
    return clinical, tables


def _write_metrics(metrics_dir: Path, model: ModelResult) -> Dict[str, Path]:
    metrics_dir.mkdir(parents=True, exist_ok=True)
    test_metrics_path = metrics_dir / "test_metrics.json"
    cv_metrics_path = metrics_dir / "cv_metrics.json"
    with test_metrics_path.open("w", encoding="utf-8") as handle:
        json.dump(model.metrics, handle, indent=2)
    with cv_metrics_path.open("w", encoding="utf-8") as handle:
        json.dump(model.cv_metrics, handle, indent=2)
    return {"test_metrics": test_metrics_path, "cv_metrics": cv_metrics_path}


def _write_tables(results_dir: Path, integration: IntegrationResult, summary: pd.DataFrame, model: ModelResult) -> Dict[str, Path]:
    tables_dir = results_dir / "tables"
    tables_dir.mkdir(parents=True, exist_ok=True)
    combined_path = tables_dir / "integrated_features.csv"
    write_table(integration.combined_features, combined_path, index_label="sample_id")
    summary_path = tables_dir / "modality_summary.csv"
    write_table(summary.set_index("modality"), summary_path, index_label="modality")
    predictions_path = tables_dir / "test_predictions.csv"
    model.test_predictions.to_csv(predictions_path)
    importances_path = tables_dir / "feature_importances.csv"
    model.feature_importances.to_csv(importances_path, index=False)
    return {
        "integrated_features": combined_path,
        "modality_summary": summary_path,
        "test_predictions": predictions_path,
        "feature_importances": importances_path,
    }


def _render_figures(
    results_dir: Path,
    integration: IntegrationResult,
    model: ModelResult,
    viz_config: VisualizationConfig,
    target_column: str,
) -> Dict[str, Path]:
    plots_dir = results_dir / "plots"
    plots_dir.mkdir(parents=True, exist_ok=True)
    outputs: Dict[str, Path] = {}
    outputs["outcome_distribution"] = plot_outcome_distribution(
        integration.clinical.data,
        target_column,
        viz_config,
        plots_dir,
    )
    outputs["feature_importances"] = plot_feature_importances(
        model.feature_importances,
        viz_config,
        plots_dir,
    )
    outputs["correlation_heatmap"] = plot_correlation_heatmap(
        integration,
        viz_config,
        plots_dir,
    )
    outputs["pca_projection"] = plot_pca_projection(
        integration,
        integration.clinical.data,
        target_column,
        plots_dir,
    )
    return outputs


def _persist_results(
    config: PipelineConfig,
    integration: IntegrationResult,
    model: ModelResult,
    summary: pd.DataFrame,
) -> Dict[str, Path]:
    results_dir = Path(config.results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)
    paths: Dict[str, Path] = {}
    paths.update(_write_metrics(results_dir / "metrics", model))
    paths.update(_write_tables(results_dir, integration, summary, model))
    paths.update(
        _render_figures(
            results_dir,
            integration,
            model,
            config.visualization,
            config.modeling.target_column,
        )
    )
    return paths


def run_pipeline(config: PipelineConfig | str | Path, *, write_outputs: bool = True, verbose: bool = False) -> PipelineResult:
    if isinstance(config, (str, Path)):
        config = load_config(config)
    _configure_logging(verbose)
    logger.info("Loading modality tables")
    clinical, tables = _load_modalities(config)
    logger.info("Integrating modalities")
    integration = integrate_modalities(
        tables,
        clinical,
        config.integration,
        config.feature_selection,
    )
    summary = compute_feature_summary(integration)
    logger.info("Training model: %s", config.modeling.estimator)
    model = train_model(
        integration.combined_features,
        integration.clinical.data,
        config.modeling,
    )
    outputs: Dict[str, Path] = {}
    if write_outputs:
        outputs = _persist_results(config, integration, model, summary)
    return PipelineResult(
        config=config,
        integration=integration,
        model=model,
        feature_summary=summary,
        outputs=outputs,
    )


def main(argv: Optional[Iterable[str]] = None) -> PipelineResult:
    parser = argparse.ArgumentParser(description="Run the multi-omics biomarker explorer pipeline")
    parser.add_argument("--config", required=True, help="Path to YAML configuration file")
    parser.add_argument("--no-write", action="store_true", help="Disable writing outputs to disk")
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging")
    args = parser.parse_args(argv)
    return run_pipeline(args.config, write_outputs=not args.no_write, verbose=args.verbose)


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    main()
