"""Model training utilities for biomarker discovery."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Tuple

import numpy as np
import pandas as pd
from sklearn.base import ClassifierMixin
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    f1_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split

from .config import ModelConfig


@dataclass
class ModelResult:
    """Outputs from model fitting."""

    estimator_name: str
    estimator: ClassifierMixin
    metrics: Dict[str, float]
    cv_metrics: Dict[str, float]
    feature_importances: pd.DataFrame
    test_predictions: pd.DataFrame


def _build_estimator(config: ModelConfig) -> ClassifierMixin:
    params = dict(config.estimator_params)
    if config.estimator.lower() in {"logistic", "logistic_regression"}:
        estimator = LogisticRegression(
            max_iter=params.pop("max_iter", 1000),
            class_weight=config.class_weight,
            random_state=config.random_state,
            solver=params.pop("solver", "saga"),
            penalty=params.pop("penalty", "l2"),
        )
        if estimator.penalty == "elasticnet":
            estimator.set_params(l1_ratio=params.pop("l1_ratio", 0.5))
        estimator.set_params(**params)
        return estimator
    if config.estimator.lower() in {"elastic_net", "elasticnet"}:
        estimator = LogisticRegression(
            max_iter=params.pop("max_iter", 1000),
            class_weight=config.class_weight,
            random_state=config.random_state,
            solver=params.pop("solver", "saga"),
            penalty="elasticnet",
            l1_ratio=params.pop("l1_ratio", 0.5),
        )
        estimator.set_params(**params)
        return estimator
    if config.estimator.lower() in {"sgd", "sgd_classifier"}:
        estimator = SGDClassifier(
            loss=params.pop("loss", "log_loss"),
            penalty=params.pop("penalty", "elasticnet"),
            alpha=params.pop("alpha", 0.0001),
            l1_ratio=params.pop("l1_ratio", 0.15),
            class_weight=config.class_weight,
            random_state=config.random_state,
            max_iter=params.pop("max_iter", 1000),
        )
        estimator.set_params(**params)
        return estimator
    if config.estimator.lower() in {"rf", "random_forest", "randomforest"}:
        estimator = RandomForestClassifier(
            n_estimators=params.pop("n_estimators", 300),
            random_state=config.random_state,
            class_weight=config.class_weight,
            n_jobs=config.n_jobs,
        )
        estimator.set_params(**params)
        return estimator
    raise ValueError(f"Unknown estimator '{config.estimator}'")


def _prediction_scores(estimator: ClassifierMixin, features: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
    if hasattr(estimator, "predict_proba"):
        proba = estimator.predict_proba(features)[:, 1]
    elif hasattr(estimator, "decision_function"):
        proba = estimator.decision_function(features)
    else:  # pragma: no cover - unlikely for classifiers used here
        proba = estimator.predict(features)
    labels = estimator.predict(features)
    return labels, proba


def _extract_feature_importances(estimator: ClassifierMixin, feature_names: Iterable[str]) -> pd.DataFrame:
    if hasattr(estimator, "coef_"):
        coefs = np.abs(estimator.coef_)
        if coefs.ndim > 1:
            coefs = coefs[0]
        importances = coefs
    elif hasattr(estimator, "feature_importances_"):
        importances = estimator.feature_importances_
    else:
        return pd.DataFrame(columns=["feature", "importance"])
    return (
        pd.DataFrame({"feature": list(feature_names), "importance": importances})
        .sort_values("importance", ascending=False)
        .reset_index(drop=True)
    )


def train_model(
    features: pd.DataFrame,
    clinical: pd.DataFrame,
    config: ModelConfig,
) -> ModelResult:
    """Fit the configured model and compute evaluation metrics."""

    target = clinical[config.target_column]
    X_train, X_test, y_train, y_test = train_test_split(
        features,
        target,
        test_size=config.test_size,
        stratify=target,
        random_state=config.random_state,
    )
    estimator = _build_estimator(config)
    estimator.fit(X_train, y_train)
    y_pred, y_scores = _prediction_scores(estimator, X_test)
    metrics = {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "roc_auc": float(roc_auc_score(y_test, y_scores)),
        "average_precision": float(average_precision_score(y_test, y_scores)),
        "f1": float(f1_score(y_test, y_pred)),
    }
    scoring = {
        "roc_auc": "roc_auc",
        "accuracy": "accuracy",
        "average_precision": "average_precision",
        "f1": "f1",
    }
    cv = StratifiedKFold(n_splits=config.cv_folds, shuffle=True, random_state=config.random_state)
    cv_result = cross_validate(
        _build_estimator(config),
        features,
        target,
        scoring=scoring,
        cv=cv,
        n_jobs=config.n_jobs,
    )
    cv_metrics = {name: float(cv_result[f"test_{name}"].mean()) for name in scoring}
    feature_importances = _extract_feature_importances(estimator, features.columns)
    test_predictions = pd.DataFrame(
        {
            "sample_id": X_test.index,
            "true_label": y_test.values,
            "predicted_label": y_pred,
            "score": y_scores,
        }
    ).set_index("sample_id")
    return ModelResult(
        estimator_name=config.estimator,
        estimator=estimator,
        metrics=metrics,
        cv_metrics=cv_metrics,
        feature_importances=feature_importances,
        test_predictions=test_predictions,
    )
