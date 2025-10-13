"""Smoke tests for the biomarker explorer pipeline."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from biomarker_explorer import (
    ClinicalConfig,
    FeatureSelectionConfig,
    IntegrationConfig,
    ModelConfig,
    PipelineConfig,
    TableConfig,
    VisualizationConfig,
    run_pipeline,
)
from scripts.generate_synthetic_multiomics import generate_synthetic_dataset


def test_pipeline_runs_on_synthetic_dataset(tmp_path):
    data_dir = tmp_path / "data"
    results_dir = tmp_path / "results"
    generate_synthetic_dataset(
        data_dir,
        seed=123,
        n_samples=40,
        n_rna_genes=60,
        n_methylation_sites=40,
        n_mutation_genes=30,
    )
    config = PipelineConfig(
        rna_seq=TableConfig(path=str(data_dir / "rna_seq.csv")),
        methylation=TableConfig(path=str(data_dir / "methylation.csv")),
        mutation=TableConfig(path=str(data_dir / "mutation.csv")),
        clinical=ClinicalConfig(path=str(data_dir / "clinical.csv")),
        integration=IntegrationConfig(),
        feature_selection=FeatureSelectionConfig(top_k=25),
        modeling=ModelConfig(random_state=123, cv_folds=3, test_size=0.25),
        visualization=VisualizationConfig(n_top_features=25),
        results_dir=str(results_dir),
    )
    result = run_pipeline(config, write_outputs=False)
    assert result.integration.combined_features.shape[0] == 40
    assert result.integration.combined_features.shape[1] > 0
    assert "roc_auc" in result.model.metrics
    assert result.model.feature_importances.shape[0] > 0
    assert not result.model.test_predictions.empty
    assert set(result.model.test_predictions.columns) == {"true_label", "predicted_label", "score"}
