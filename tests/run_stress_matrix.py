from __future__ import annotations

import csv
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


CONCURRENCY_LEVELS = (5, 10, 20)


@dataclass
class StressResult:
    users: int
    request_count: int
    failure_count: int
    avg_response_ms: float
    failure_rate: float
    avg_response_seconds: float
    passed: bool


def _read_positive_int_env(name: str, default: int) -> int:
    raw_value = os.getenv(name, str(default)).strip()
    try:
        value = int(raw_value)
    except ValueError:
        return default
    if value <= 0:
        return default
    return value


def _read_positive_float_env(name: str, default: float) -> float:
    raw_value = os.getenv(name, str(default)).strip()
    try:
        value = float(raw_value)
    except ValueError:
        return default
    if value <= 0:
        return default
    return value


def _normalize_locust_host(raw_base_url: str) -> str:
    base_url = raw_base_url.strip().rstrip("/")
    if not base_url:
        raise ValueError("WEB2API_BASE_URL is empty.")
    if base_url.endswith("/v1"):
        return base_url[:-3]
    return base_url


def _run_locust_once(
    *,
    host: str,
    users: int,
    total_requests: int,
    report_prefix: Path,
) -> None:
    env = os.environ.copy()
    env["WEB2API_STRESS_TOTAL_REQUESTS"] = str(total_requests)

    command = [
        sys.executable,
        "-m",
        "locust",
        "-f",
        "tests/locustfile_openai.py",
        "--headless",
        "--host",
        host,
        "-u",
        str(users),
        "-r",
        str(users),
        "--run-time",
        "30m",
        "--only-summary",
        "--csv",
        str(report_prefix),
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        env=env,
    )
    if result.stdout.strip():
        print(result.stdout.strip())
    if result.returncode != 0:
        stderr = result.stderr.strip()
        raise RuntimeError(
            f"Locust run failed for users={users}. stderr={stderr or '<empty>'}"
        )


def _read_aggregated_stats(stats_csv_path: Path) -> tuple[int, int, float]:
    if not stats_csv_path.exists():
        raise RuntimeError(f"Missing stats CSV file: {stats_csv_path}")

    with stats_csv_path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row.get("Name") != "Aggregated":
                continue

            request_count = int(float(row.get("Request Count", "0") or 0))
            failure_count = int(float(row.get("Failure Count", "0") or 0))
            avg_response_ms = float(row.get("Average Response Time", "0") or 0)
            return request_count, failure_count, avg_response_ms

    raise RuntimeError(f"Cannot find Aggregated row in {stats_csv_path}")


def _format_result_line(result: StressResult) -> str:
    status = "PASS" if result.passed else "FAIL"
    return (
        f"users={result.users:>2} | requests={result.request_count:>3} | "
        f"errors={result.failure_count:>3} | "
        f"error_rate={result.failure_rate * 100:>6.2f}% | "
        f"avg={result.avg_response_seconds:>5.2f}s | {status}"
    )


def main() -> None:
    base_url = os.getenv("WEB2API_BASE_URL", "http://localhost:8000")
    host = _normalize_locust_host(base_url)

    total_requests = _read_positive_int_env("WEB2API_STRESS_TOTAL_REQUESTS", 100)
    max_error_rate = _read_positive_float_env("WEB2API_STRESS_MAX_ERROR_RATE", 0.01)
    max_avg_seconds = _read_positive_float_env("WEB2API_STRESS_MAX_AVG_SECONDS", 5.0)

    print(
        "Stress test config: "
        f"host={host}, total_requests={total_requests}, "
        f"max_error_rate={max_error_rate:.2%}, max_avg_seconds={max_avg_seconds:.2f}"
    )

    results: list[StressResult] = []
    with tempfile.TemporaryDirectory(prefix="web2api-stress-") as temp_dir:
        report_root = Path(temp_dir)

        for users in CONCURRENCY_LEVELS:
            print(f"\n[run] users={users}, target_requests={total_requests}")
            prefix = report_root / f"u{users}"
            _run_locust_once(
                host=host,
                users=users,
                total_requests=total_requests,
                report_prefix=prefix,
            )

            request_count, failure_count, avg_response_ms = _read_aggregated_stats(
                Path(f"{prefix}_stats.csv")
            )
            failure_rate = (
                failure_count / request_count if request_count > 0 else 1.0
            )
            avg_response_seconds = avg_response_ms / 1000.0
            passed = (
                failure_rate < max_error_rate
                and avg_response_seconds < max_avg_seconds
            )
            results.append(
                StressResult(
                    users=users,
                    request_count=request_count,
                    failure_count=failure_count,
                    avg_response_ms=avg_response_ms,
                    failure_rate=failure_rate,
                    avg_response_seconds=avg_response_seconds,
                    passed=passed,
                )
            )

    print("\nStress test summary:")
    for result in results:
        print(_format_result_line(result))

    failed_levels = [result.users for result in results if not result.passed]
    if failed_levels:
        joined = ", ".join(str(level) for level in failed_levels)
        raise SystemExit(f"Threshold check failed for user levels: {joined}")

    print("All stress test thresholds passed.")


if __name__ == "__main__":
    main()
