"""Reproducible calibration records; this module does not make empirical claims."""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class CalibrationConfig:
    version: str
    minimum_risk_reward: float = 1.0
    minimum_independent_families: int = 2
    confidence_labels: tuple[str, str, str] = ("low", "medium", "high")


@dataclass(frozen=True)
class CalibrationDataset:
    dataset_id: str
    role: str
    content_version: str


@dataclass(frozen=True)
class CalibrationResult:
    calibration_version: str
    config_version: str
    development_dataset_id: str
    strategy_version: str
    objective: str
    parameters: dict[str, float]
    status: str = "uncalibrated"


class ParameterFitter(Protocol):
    def fit(self, dataset: CalibrationDataset) -> Mapping[str, float]: ...


class CalibrationWorkflow:
    """Keeps fitting and OOS evaluation structurally separate."""

    def fit(
        self,
        dataset: CalibrationDataset,
        config: CalibrationConfig,
        strategy_version: str,
        objective: str,
        fitter: ParameterFitter,
    ) -> CalibrationResult:
        ensure_development_only(dataset.role)
        parameters = {name: float(value) for name, value in fitter.fit(dataset).items()}
        return CalibrationResult(
            calibration_version="calibration-workflow-v1",
            config_version=config.version,
            development_dataset_id=dataset.dataset_id,
            strategy_version=strategy_version,
            objective=objective,
            parameters=parameters,
        )

    def evaluate(
        self, result: CalibrationResult, dataset: CalibrationDataset
    ) -> dict[str, str]:
        if dataset.role != "oos":
            raise ValueError("Calibration evaluation requires an out-of-sample dataset")
        if dataset.dataset_id == result.development_dataset_id:
            raise ValueError("Development data cannot be reused as out-of-sample data")
        return {
            "calibration_version": result.calibration_version,
            "dataset_id": dataset.dataset_id,
            "status": "evaluation_pending",
        }


def ensure_development_only(dataset_role: str) -> None:
    if dataset_role != "development":
        raise ValueError("Calibration may only use development data")
