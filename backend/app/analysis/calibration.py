from dataclasses import dataclass


@dataclass(frozen=True)
class CalibrationConfig:
    version: str
    minimum_risk_reward: float = 1.0
    minimum_independent_families: int = 2
    confidence_labels: tuple[str, str, str] = ("low", "medium", "high")


def ensure_development_only(dataset_role: str) -> None:
    if dataset_role != "development":
        raise ValueError("Calibration may only use development data")
