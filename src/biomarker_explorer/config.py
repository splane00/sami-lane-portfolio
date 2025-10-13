"""Configuration models and helpers for the biomarker explorer."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

try:  # pragma: no cover - optional dependency
    import yaml  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - fallback parser used in tests
    yaml = None  # type: ignore


class ConfigError(Exception):
    """Raised when a configuration file is missing required information."""


def _parse_scalar(value: str) -> Any:
    lowered = value.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    if lowered in {"null", "none"}:
        return None
    if (value.startswith("\"") and value.endswith("\"")) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    try:
        if "." in value or "e" in lowered:
            return float(value)
        return int(value)
    except ValueError:
        return value


def _simple_yaml_load(text: str) -> Dict[str, Any]:
    lines = text.splitlines()
    root: Dict[str, Any] = {}
    stack: List[tuple[int, Any]] = [(-1, root)]
    for idx, raw_line in enumerate(lines):
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(line) - len(stripped)
        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]
        if stripped.startswith("- "):
            value = _parse_scalar(stripped[2:])
            if not isinstance(parent, list):
                raise ConfigError("List item without list parent in configuration")
            parent.append(value)
            continue
        key, sep, remainder = stripped.partition(":")
        if not sep:
            raise ConfigError(f"Invalid configuration line: {line}")
        key = key.strip()
        remainder = remainder.strip()
        if remainder == "":
            # determine whether the nested structure is a list or dict
            next_container_is_list = False
            for future_line in lines[idx + 1 :]:
                future_stripped = future_line.strip()
                if not future_stripped or future_stripped.startswith("#"):
                    continue
                future_indent = len(future_line) - len(future_stripped)
                if future_indent <= indent:
                    break
                next_container_is_list = future_stripped.startswith("- ")
                break
            container: Any = [] if next_container_is_list else {}
            if not isinstance(parent, dict):
                raise ConfigError("Cannot create mapping entry inside a list without a key")
            parent[key] = container
            stack.append((indent, container))
        else:
            if not isinstance(parent, dict):
                raise ConfigError("Cannot assign key-value pair inside list parent")
            parent[key] = _parse_scalar(remainder)
    return root


@dataclass
class TableConfig:
    """Configuration describing a generic omics table."""

    path: str
    id_column: str = "sample_id"
    dropna: bool = False
    features: Optional[List[str]] = None


@dataclass
class ClinicalConfig(TableConfig):
    """Configuration for the clinical metadata table."""

    outcome_column: str = "outcome"
    covariates: Optional[List[str]] = None


@dataclass
class IntegrationConfig:
    """Integration-specific options that apply across modalities."""

    join: str = "inner"
    impute_strategy: Optional[str] = "mean"
    scale: str = "zscore"
    prefix_modality: bool = True
    min_nonzero_fraction: Optional[float] = None


@dataclass
class FeatureSelectionConfig:
    """Feature selection strategy options."""

    top_k: Optional[int] = None
    variance_threshold: Optional[float] = None
    per_modality: bool = True


@dataclass
class ModelConfig:
    """Model training hyperparameters."""

    estimator: str = "logistic_regression"
    estimator_params: Dict[str, Any] = field(default_factory=dict)
    target_column: str = "outcome"
    test_size: float = 0.2
    cv_folds: int = 5
    scoring: str = "roc_auc"
    random_state: int = 42
    n_jobs: int = 1
    class_weight: Optional[str] = "balanced"


@dataclass
class VisualizationConfig:
    """Options that control figure generation."""

    n_top_features: int = 20
    correlation_method: str = "spearman"
    output_formats: List[str] = field(default_factory=lambda: ["png"])


@dataclass
class PipelineConfig:
    """Full pipeline configuration assembled from nested sections."""

    rna_seq: TableConfig
    methylation: TableConfig
    mutation: TableConfig
    clinical: ClinicalConfig
    integration: IntegrationConfig = field(default_factory=IntegrationConfig)
    feature_selection: FeatureSelectionConfig = field(default_factory=FeatureSelectionConfig)
    modeling: ModelConfig = field(default_factory=ModelConfig)
    visualization: VisualizationConfig = field(default_factory=VisualizationConfig)
    results_dir: str = "results"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PipelineConfig":
        try:
            rna_cfg = TableConfig(**data["rna_seq"])
            methyl_cfg = TableConfig(**data["methylation"])
            mut_cfg = TableConfig(**data["mutation"])
            clinical_cfg = ClinicalConfig(**data["clinical"])
        except KeyError as exc:  # pragma: no cover - explicit message
            raise ConfigError(f"Missing required configuration section: {exc.args[0]}") from exc
        integration_cfg = IntegrationConfig(**data.get("integration", {}))
        feature_cfg = FeatureSelectionConfig(**data.get("feature_selection", {}))
        model_cfg = ModelConfig(**data.get("modeling", {}))
        viz_cfg = VisualizationConfig(**data.get("visualization", {}))
        results_dir = data.get("results_dir", "results")
        return cls(
            rna_seq=rna_cfg,
            methylation=methyl_cfg,
            mutation=mut_cfg,
            clinical=clinical_cfg,
            integration=integration_cfg,
            feature_selection=feature_cfg,
            modeling=model_cfg,
            visualization=viz_cfg,
            results_dir=results_dir,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rna_seq": vars(self.rna_seq),
            "methylation": vars(self.methylation),
            "mutation": vars(self.mutation),
            "clinical": vars(self.clinical),
            "integration": vars(self.integration),
            "feature_selection": vars(self.feature_selection),
            "modeling": vars(self.modeling),
            "visualization": vars(self.visualization),
            "results_dir": self.results_dir,
        }


def load_config(path: str | Path) -> PipelineConfig:
    """Load a :class:`PipelineConfig` from a YAML file."""

    cfg_path = Path(path)
    if not cfg_path.exists():  # pragma: no cover - validated at runtime
        raise FileNotFoundError(f"Configuration file not found: {cfg_path}")
    text = cfg_path.read_text(encoding="utf-8")
    if yaml is not None:  # pragma: no branch - prefer PyYAML when available
        data = yaml.safe_load(text) or {}
    else:
        data = _simple_yaml_load(text)
    if not isinstance(data, dict):  # pragma: no cover - defensive
        raise ConfigError("Configuration YAML must define a mapping")
    return PipelineConfig.from_dict(data)
