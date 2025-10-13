"""Feature integration across modalities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable

import pandas as pd

from .config import FeatureSelectionConfig, IntegrationConfig
from .data_io import ClinicalTable, OmicsTable
from .preprocessing import align_modalities, preprocess_modalities


@dataclass
class IntegrationResult:
    """Outputs from integrating multiple omics tables."""

    combined_features: pd.DataFrame
    modality_frames: Dict[str, pd.DataFrame]
    clinical: ClinicalTable


def integrate_modalities(
    tables: Iterable[OmicsTable],
    clinical: ClinicalTable,
    integration_cfg: IntegrationConfig,
    feature_cfg: FeatureSelectionConfig,
) -> IntegrationResult:
    """Preprocess, align, and concatenate omics modalities."""

    tables = list(tables)
    processed = preprocess_modalities(tables, integration_cfg, feature_cfg)
    aligned_tables, aligned_clinical = align_modalities(processed, clinical, join=integration_cfg.join)
    modality_frames: Dict[str, pd.DataFrame] = {}
    aligned_frames = []
    for table in aligned_tables:
        frame = table.data
        if integration_cfg.prefix_modality:
            frame = frame.add_prefix(f"{table.name}__")
        modality_frames[table.name] = frame
        aligned_frames.append(frame)
    combined = pd.concat(aligned_frames, axis=1)
    combined.index.name = aligned_clinical.data.index.name or "sample_id"
    return IntegrationResult(
        combined_features=combined,
        modality_frames=modality_frames,
        clinical=aligned_clinical,
    )


def compute_feature_summary(result: IntegrationResult) -> pd.DataFrame:
    """Generate descriptive statistics for each modality and the combined matrix."""

    rows = []
    total_samples = len(result.combined_features)
    for name, frame in result.modality_frames.items():
        rows.append(
            {
                "modality": name,
                "n_samples": len(frame),
                "n_features": frame.shape[1],
                "sparsity": float((frame == 0).sum().sum()) / (frame.shape[0] * frame.shape[1]),
                "mean_variance": float(frame.var().mean()),
            }
        )
    rows.append(
        {
            "modality": "combined",
            "n_samples": total_samples,
            "n_features": result.combined_features.shape[1],
            "sparsity": float((result.combined_features == 0).sum().sum())
            / max(1, result.combined_features.shape[0] * result.combined_features.shape[1]),
            "mean_variance": float(result.combined_features.var().mean()),
        }
    )
    return pd.DataFrame(rows)
