"""Generate synthetic multi-omics datasets for demos and testing."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, Tuple

import numpy as np
import pandas as pd
import yaml


def _make_samples(n: int) -> list[str]:
    return [f"S{i:04d}" for i in range(1, n + 1)]


def _simulate_rna(rng: np.random.Generator, n_samples: int, n_genes: int) -> Tuple[pd.DataFrame, np.ndarray]:
    latent = rng.normal(size=n_samples)
    base = rng.normal(loc=0.0, scale=1.0, size=(n_samples, n_genes))
    signal = rng.normal(loc=2.0, scale=0.5, size=(n_samples, 5))
    base[:, :5] += signal
    base += latent[:, None] * 0.5
    genes = [f"GENE_{i:03d}" for i in range(1, n_genes + 1)]
    frame = pd.DataFrame(base, columns=genes)
    return frame, latent


def _simulate_methylation(
    rng: np.random.Generator, n_samples: int, n_sites: int, latent: np.ndarray
) -> Tuple[pd.DataFrame, np.ndarray]:
    base = rng.beta(a=2.0, b=5.0, size=(n_samples, n_sites))
    base[:, :5] -= np.clip(latent[:, None] * 0.1, -0.2, 0.2)
    sites = [f"CPG_{i:03d}" for i in range(1, n_sites + 1)]
    frame = pd.DataFrame(np.clip(base, 0, 1), columns=sites)
    return frame, base[:, :5].mean(axis=1)


def _simulate_mutations(
    rng: np.random.Generator, n_samples: int, n_genes: int, latent: np.ndarray
) -> Tuple[pd.DataFrame, np.ndarray]:
    probs = 0.05 + 0.2 * (latent - latent.min()) / (latent.max() - latent.min() + 1e-6)
    mutations = rng.binomial(1, probs[:, None], size=(n_samples, n_genes))
    genes = [f"MUT_{i:03d}" for i in range(1, n_genes + 1)]
    frame = pd.DataFrame(mutations, columns=genes)
    return frame, mutations[:, :5].sum(axis=1)


def _simulate_clinical(
    rng: np.random.Generator,
    sample_ids: list[str],
    latent: np.ndarray,
    methyl_signal: np.ndarray,
    mutation_signal: np.ndarray,
) -> pd.DataFrame:
    logits = 0.8 * latent - 1.5 * methyl_signal + 0.7 * mutation_signal
    probs = 1 / (1 + np.exp(-logits))
    outcome = rng.binomial(1, np.clip(probs, 0.05, 0.95))
    age = rng.normal(loc=60, scale=8, size=len(sample_ids)).round(1)
    stage = rng.choice(["I", "II", "III", "IV"], size=len(sample_ids), p=[0.25, 0.35, 0.25, 0.15])
    clinical = pd.DataFrame(
        {
            "sample_id": sample_ids,
            "outcome": outcome,
            "age": age,
            "stage": stage,
        }
    )
    return clinical


def generate_synthetic_dataset(
    out_dir: Path,
    *,
    seed: int = 17,
    n_samples: int = 80,
    n_rna_genes: int = 200,
    n_methylation_sites: int = 120,
    n_mutation_genes: int = 80,
) -> Dict[str, pd.DataFrame]:
    out_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(seed)
    samples = _make_samples(n_samples)
    rna, latent = _simulate_rna(rng, n_samples, n_rna_genes)
    methyl, methyl_signal = _simulate_methylation(rng, n_samples, n_methylation_sites, latent)
    mutation, mutation_signal = _simulate_mutations(rng, n_samples, n_mutation_genes, latent)
    clinical = _simulate_clinical(rng, samples, latent, methyl_signal, mutation_signal)

    rna.insert(0, "sample_id", samples)
    methyl.insert(0, "sample_id", samples)
    mutation.insert(0, "sample_id", samples)

    frames = {
        "rna_seq": rna,
        "methylation": methyl,
        "mutation": mutation,
        "clinical": clinical,
    }
    for name, frame in frames.items():
        frame.to_csv(out_dir / f"{name}.csv", index=False)
    return frames


def _default_config_dict(out_dir: Path, results_dir: Path) -> Dict:
    return {
        "rna_seq": {"path": str(out_dir / "rna_seq.csv"), "id_column": "sample_id"},
        "methylation": {"path": str(out_dir / "methylation.csv"), "id_column": "sample_id"},
        "mutation": {"path": str(out_dir / "mutation.csv"), "id_column": "sample_id"},
        "clinical": {
            "path": str(out_dir / "clinical.csv"),
            "id_column": "sample_id",
            "outcome_column": "outcome",
        },
        "integration": {
            "join": "inner",
            "impute_strategy": "mean",
            "scale": "zscore",
            "prefix_modality": True,
        },
        "feature_selection": {"top_k": 100, "variance_threshold": 0.0},
        "modeling": {
            "estimator": "logistic_regression",
            "target_column": "outcome",
            "test_size": 0.2,
            "cv_folds": 5,
            "random_state": 17,
        },
        "visualization": {"n_top_features": 30, "output_formats": ["png"]},
        "results_dir": str(results_dir),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a synthetic multi-omics dataset")
    parser.add_argument("--out-dir", type=Path, default=Path("data/demo"), help="Output directory for CSV files")
    parser.add_argument("--config-out", type=Path, default=Path("configs/demo_config.yaml"), help="Path to write YAML config")
    parser.add_argument("--results-dir", type=Path, default=Path("results/demo"), help="Results directory in config")
    parser.add_argument("--seed", type=int, default=17)
    parser.add_argument("--n-samples", type=int, default=80)
    parser.add_argument("--n-rna-genes", type=int, default=200)
    parser.add_argument("--n-methylation-sites", type=int, default=120)
    parser.add_argument("--n-mutation-genes", type=int, default=80)
    parser.add_argument("--no-config", action="store_true", help="Skip writing the YAML configuration file")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    frames = generate_synthetic_dataset(
        args.out_dir,
        seed=args.seed,
        n_samples=args.n_samples,
        n_rna_genes=args.n_rna_genes,
        n_methylation_sites=args.n_methylation_sites,
        n_mutation_genes=args.n_mutation_genes,
    )
    if not args.no_config:
        config = _default_config_dict(args.out_dir, args.results_dir)
        args.config_out.parent.mkdir(parents=True, exist_ok=True)
        with args.config_out.open("w", encoding="utf-8") as handle:
            yaml.safe_dump(config, handle, sort_keys=False)
    print(f"Wrote synthetic dataset with {args.n_samples} samples to {args.out_dir}")


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    main()
