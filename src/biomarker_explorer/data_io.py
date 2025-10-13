"""I/O helpers for loading omics tables and clinical metadata."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

import pandas as pd

from .config import ClinicalConfig, TableConfig


@dataclass
class OmicsTable:
    """Container holding a processed omics matrix."""

    name: str
    data: pd.DataFrame

    @property
    def samples(self) -> pd.Index:
        return self.data.index

    @property
    def features(self) -> pd.Index:
        return self.data.columns


@dataclass
class ClinicalTable:
    """Wrapper for clinical metadata."""

    data: pd.DataFrame
    outcome_column: str

    @property
    def samples(self) -> pd.Index:
        return self.data.index


def _read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():  # pragma: no cover - runtime safeguard
        raise FileNotFoundError(f"Data file not found: {path}")
    return pd.read_csv(path)


def load_omics_table(name: str, config: TableConfig) -> OmicsTable:
    """Load an omics table from disk using a :class:`TableConfig`."""

    frame = _read_csv(Path(config.path))
    if config.id_column not in frame.columns:
        raise ValueError(f"Column '{config.id_column}' missing from {config.path}")
    frame = frame.set_index(config.id_column)
    if config.features:
        missing = sorted(set(config.features) - set(frame.columns))
        if missing:
            raise ValueError(f"Requested features not found in {config.path}: {missing}")
        frame = frame.loc[:, config.features]
    if config.dropna:
        frame = frame.dropna(axis=0, how="any")
    frame = frame.sort_index()
    return OmicsTable(name=name, data=frame)


def load_clinical_table(config: ClinicalConfig) -> ClinicalTable:
    """Load and prepare the clinical metadata table."""

    frame = _read_csv(Path(config.path))
    if config.id_column not in frame.columns:
        raise ValueError(f"Column '{config.id_column}' missing from {config.path}")
    frame = frame.set_index(config.id_column)
    if config.dropna:
        frame = frame.dropna(subset=[config.outcome_column])
    frame = frame.sort_index()
    return ClinicalTable(data=frame, outcome_column=config.outcome_column)


def write_table(frame: pd.DataFrame, path: Path, index_label: Optional[str] = None) -> None:
    """Persist a dataframe to CSV, creating parent folders if needed."""

    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=True, index_label=index_label)


def shared_samples(tables: Iterable[OmicsTable]) -> pd.Index:
    """Return the intersection of sample identifiers across modalities."""

    iterator = iter(tables)
    try:
        first = next(iterator)
    except StopIteration:
        return pd.Index([])
    intersect = set(first.samples)
    for table in iterator:
        intersect &= set(table.samples)
    return pd.Index(sorted(intersect))
