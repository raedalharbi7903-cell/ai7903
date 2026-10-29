"""Reproducible calibration records; this module does not make empirical claims."""

from collections.abc import Mapping
from dataclasses import dataclass
from math import isfinite
from typing import Protocol


@dataclass(frozen=True)
class CalibrationConfig:
    version: str
    minimum_risk_reward: float = 1.0
    minimum_independent_families: int = 2
    confidence_labels: tuple[str, str, str] = ("low", "medium", "high")

    def __post_init__(self) -> None:
        if not self.version.strip():
            raise ValueError("Configuration version is required")
        if (
            isinstance(self.minimum_risk_reward, bool)
            or not isfinite(self.minimum_risk_reward)
            or self.minimum_risk_reward <= 0
        ):
            raise ValueError("Risk/reward must be finite and positive")
        if (
            type(self.minimum_independent_families) is not int
            or self.minimum_independent_families < 1
        ):
            raise ValueError("Independent family count must be a positive integer")
        if (
            len(self.confidence_labels) != 3
            or len(set(self.confidence_labels)) != 3
            or any(not label.strip() for label in self.confidence_labels)
        ):
            raise ValueError("Three distinct nonempty confidence labels are required")


@dataclass(frozen=True)
class CalibrationDataset:
    dataset_id: str
    role: str
    content_version: str

    def __post_init__(self) -> None:
        if not self.dataset_id.strip() or not self.content_version.strip():
            raise ValueError("Dataset identity and content version are required")
        if self.role not in {"development", "oos"}:
            raise ValueError("Dataset role must be development or oos")


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
        if not strategy_version.strip() or not objective.strip():
            raise ValueError("Strategy version and fitting objective are required")
        parameters = {}
        for name, value in fitter.fit(dataset).items():
            if not isinstance(name, str) or not name.strip():
                raise ValueError("Fitted parameter names must be nonempty strings")
            if (
                isinstance(value, bool)
                or not isinstance(value, int | float)
                or not isfinite(value)
            ):
                raise ValueError(
                    "Fitted parameters must be finite numeric observations"
                )
            parameters[name] = float(value)
        if not parameters:
            raise ValueError("Fitter returned no parameters")
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
