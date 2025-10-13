"""Preprocessing utilities for omics tables."""

from __future__ import annotations

from dataclasses import replace
from typing import Iterable, List
import pandas as pd
from sklearn.feature_selection import VarianceThreshold
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import MinMaxScaler, StandardScaler

from .config import FeatureSelectionConfig, IntegrationConfig
from .data_io import ClinicalTable, OmicsTable, shared_samples


def _apply_min_nonzero_fraction(frame: pd.DataFrame, threshold: float) -> pd.DataFrame:
    if threshold <= 0:
        return frame
    mask = (frame != 0).sum(axis=0) / max(len(frame), 1) >= threshold
    return frame.loc[:, mask]


def _apply_variance_threshold(frame: pd.DataFrame, threshold: float) -> pd.DataFrame:
    selector = VarianceThreshold(threshold=threshold)
    selector.fit(frame)
    kept_columns = frame.columns[selector.get_support(indices=True)]
    return frame.loc[:, kept_columns]


def _select_top_k(frame: pd.DataFrame, k: int) -> pd.DataFrame:
    if k >= frame.shape[1]:
        return frame
    variances = frame.var(axis=0)
    top_features = variances.sort_values(ascending=False).head(k).index
    return frame.loc[:, top_features]


def _impute(frame: pd.DataFrame, strategy: str) -> pd.DataFrame:
    imputer = SimpleImputer(strategy=strategy)
    transformed = imputer.fit_transform(frame)
    return pd.DataFrame(transformed, index=frame.index, columns=frame.columns)


def _scale(frame: pd.DataFrame, method: str) -> pd.DataFrame:
    if method == "none":
        return frame
    if method == "minmax":
        scaler = MinMaxScaler()
    else:
        scaler = StandardScaler()
    scaled = scaler.fit_transform(frame)
    return pd.DataFrame(scaled, index=frame.index, columns=frame.columns)


def preprocess_table(
    table: OmicsTable,
    integration_cfg: IntegrationConfig,
    feature_cfg: FeatureSelectionConfig,
) -> OmicsTable:
    """Apply preprocessing and feature selection to a single modality."""

    frame = table.data.copy()
    if integration_cfg.min_nonzero_fraction is not None:
        frame = _apply_min_nonzero_fraction(frame, integration_cfg.min_nonzero_fraction)
    if feature_cfg.variance_threshold is not None:
        frame = _apply_variance_threshold(frame, feature_cfg.variance_threshold)
    if feature_cfg.top_k is not None:
        frame = _select_top_k(frame, feature_cfg.top_k)
    if integration_cfg.impute_strategy:
        frame = _impute(frame, integration_cfg.impute_strategy)
    frame = _scale(frame, integration_cfg.scale)
    return replace(table, data=frame)


def preprocess_modalities(
    tables: Iterable[OmicsTable],
    integration_cfg: IntegrationConfig,
    feature_cfg: FeatureSelectionConfig,
) -> List[OmicsTable]:
    """Apply preprocessing to each modality individually."""

    processed = []
    for table in tables:
        processed.append(preprocess_table(table, integration_cfg, feature_cfg))
    return processed


def align_modalities(
    tables: Iterable[OmicsTable],
    clinical: ClinicalTable,
    join: str = "inner",
) -> tuple[List[OmicsTable], ClinicalTable]:
    """Align sample IDs across modalities and clinical metadata."""

    tables = list(tables)
    if join not in {"inner", "outer"}:
        raise ValueError("join must be 'inner' or 'outer'")
    if join == "inner":
        shared = shared_samples(tables + [OmicsTable("clinical", clinical.data)])
    else:
        union = set(clinical.samples)
        for table in tables:
            union |= set(table.samples)
        shared = pd.Index(sorted(union))
    aligned_tables: List[OmicsTable] = []
    for table in tables:
        reindexed = table.data.reindex(shared)
        aligned_tables.append(replace(table, data=reindexed))
    clinical_aligned = ClinicalTable(data=clinical.data.reindex(shared), outcome_column=clinical.outcome_column)
    return aligned_tables, clinical_aligned
