"""Measure synthetic local service latency; not a production SLO or market result."""

import argparse
import json
import sys
from datetime import UTC, datetime, timedelta
from math import ceil, sin
from pathlib import Path
from statistics import median
from time import perf_counter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.analysis.models import AnalysisInput  # noqa: E402
from app.analysis.service import AnalysisService  # noqa: E402


def fixture(size: int) -> AnalysisInput:
    candles = []
    for index in range(size):
        price = 100 + index * 0.01 + sin(index / 4)
        candles.append(
            {
                "timestamp": datetime(2026, 1, 1, tzinfo=UTC) + timedelta(hours=index),
                "open": price,
                "high": price + 1,
                "low": price - 1,
                "close": price,
                "volume": 100,
                "complete": True,
            }
        )
    return AnalysisInput(
        data={
            "instrument": "SYNTHETIC-USDT",
            "market": "crypto",
            "timeframe": "1h",
            "fixture": True,
            "provider": "synthetic-benchmark",
            "source_timestamp": candles[-1]["timestamp"],
            "candles": candles,
        }
    )


def measure(size: int, samples: int) -> dict:
    service = AnalysisService()
    request = fixture(size)
    service.analyze(request)  # One explicit warm-up, excluded from measurements.
    durations = []
    for _ in range(samples):
        start = perf_counter()
        result = service.analyze(request)
        durations.append((perf_counter() - start) * 1000)
        if result.decision.value in {"buy", "sell"}:
            raise RuntimeError("Missing MTF must not produce executable analysis")
    ordered = sorted(durations)
    return {
        "candles": size,
        "samples": samples,
        "p50_ms": median(ordered),
        "p95_ms": ordered[ceil(samples * 0.95) - 1],
        "max_ms": max(ordered),
        "durations_ms": durations,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", type=int, default=20)
    args = parser.parse_args()
    if not 2 <= args.samples <= 1000:
        parser.error("--samples must be between 2 and 1000")
    results = [measure(size, args.samples) for size in (32, 256, 1024)]
    report = ROOT / ".verification" / "latency-baseline.json"
    report.parent.mkdir(exist_ok=True)
    report.write_text(
        json.dumps(
            {
                "scope": (
                    "warm sequential in-process synthetic service; MTF unavailable"
                ),
                "production_slo_verified": False,
                "results": results,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    for item in results:
        print(
            f"{item['candles']} candles: p50={item['p50_ms']:.3f}ms, "
            f"p95={item['p95_ms']:.3f}ms, max={item['max_ms']:.3f}ms"
        )


if __name__ == "__main__":
    main()
