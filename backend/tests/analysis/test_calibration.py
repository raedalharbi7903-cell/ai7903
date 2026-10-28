import pytest

from app.analysis.calibration import (
    CalibrationConfig,
    CalibrationDataset,
    CalibrationWorkflow,
)


class FixedFitter:
    def fit(self, dataset: CalibrationDataset) -> dict[str, float]:
        return {"threshold": 1.25}


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
