import pytest

from app.analysis.calibration import (
    CalibrationConfig,
    CalibrationDataset,
    CalibrationWorkflow,
)


class FixedFitter:
    def fit(self, dataset: CalibrationDataset) -> dict[str, float]:
        return {"threshold": 1.25}


@pytest.mark.parametrize(
    "parameters",
    [
        {},
        {"threshold": float("nan")},
        {"threshold": float("inf")},
        {"threshold": True},
        {"threshold": "1.25"},
        {"": 1},
        {3: 1},
    ],
)
def test_invalid_fitter_results_cannot_be_recorded(parameters) -> None:
    class InvalidFitter:
        def fit(self, dataset):
            return parameters

    with pytest.raises(ValueError):
        CalibrationWorkflow().fit(
            CalibrationDataset("dev", "development", "v1"),
            CalibrationConfig("v1"),
            "s1",
            "quality",
            InvalidFitter(),
        )


@pytest.mark.parametrize(
    "configuration",
    [
        {"version": ""},
        {"minimum_risk_reward": 0},
        {"minimum_risk_reward": float("nan")},
        {"minimum_risk_reward": True},
        {"minimum_independent_families": True},
        {"minimum_independent_families": 0},
        {"confidence_labels": ("low", "low", "high")},
    ],
)
def test_invalid_calibration_configuration_is_rejected(configuration) -> None:
    with pytest.raises(ValueError):
        CalibrationConfig(**{"version": "v1", **configuration})


@pytest.mark.parametrize(
    "identity,role,version",
    [
        ("", "development", "v1"),
        ("dev", "unknown", "v1"),
        ("dev", "oos", ""),
    ],
)
def test_dataset_provenance_must_be_explicit(identity, role, version) -> None:
    with pytest.raises(ValueError):
        CalibrationDataset(identity, role, version)


def test_calibration_fits_only_development_data_reproducibly() -> None:
    workflow = CalibrationWorkflow()
    dataset = CalibrationDataset("development-2026-01", "development", "ohlcv-v1")
    config = CalibrationConfig("config-v1")
    first = workflow.fit(
        dataset, config, "strategy-v1", "maximize_quality", FixedFitter()
    )
    second = workflow.fit(
        dataset, config, "strategy-v1", "maximize_quality", FixedFitter()
    )
    assert first == second
    assert first.status == "uncalibrated"
    assert first.development_dataset_id == dataset.dataset_id


def test_calibration_rejects_oos_fitting_and_keeps_evaluation_isolated() -> None:
    workflow = CalibrationWorkflow()
    oos = CalibrationDataset("oos-2026-02", "oos", "ohlcv-v1")
    with pytest.raises(ValueError, match="development"):
        workflow.fit(
            oos, CalibrationConfig("config-v1"), "strategy-v1", "quality", FixedFitter()
        )
    result = workflow.fit(
        CalibrationDataset("development-2026-01", "development", "ohlcv-v1"),
        CalibrationConfig("config-v1"),
        "strategy-v1",
        "quality",
        FixedFitter(),
    )
    assert workflow.evaluate(result, oos)["dataset_id"] == "oos-2026-02"
    with pytest.raises(ValueError, match="out-of-sample"):
        workflow.evaluate(
            result, CalibrationDataset("development-2026-01", "development", "ohlcv-v1")
        )
