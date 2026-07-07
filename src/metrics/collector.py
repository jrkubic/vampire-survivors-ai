import csv
import os
import time
from dataclasses import dataclass, field


class MetricsCollector:
    def __init__(self, run_id: str, output_dir: str = "data/runs"):
        self.run_id = run_id
        self.output_dir = output_dir
        self.decisions: list[dict] = []
        self.start_time = time.time()

    def log_decision(self, metric: dict) -> None:
        metric.setdefault("timestamp", time.time() - self.start_time)
        self.decisions.append(metric)

    def save(self) -> str:
        os.makedirs(self.output_dir, exist_ok=True)
        filepath = os.path.join(self.output_dir, f"{self.run_id}.csv")
        if not self.decisions:
            return filepath

        fieldnames = list(self.decisions[0].keys())
        # Ensure all keys from all decisions are included
        for d in self.decisions:
            for k in d:
                if k not in fieldnames:
                    fieldnames.append(k)

        with open(filepath, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(self.decisions)

        return filepath

    def get_summary(self) -> dict:
        if not self.decisions:
            return {}

        inference_times = [d.get("inference_time_ms", 0) for d in self.decisions]
        parse_results = [d.get("action_parse_success", True) for d in self.decisions]
        failures = sum(1 for p in parse_results if not p)

        sorted_times = sorted(inference_times)
        p95_idx = int(len(sorted_times) * 0.95)

        return {
            "total_ticks": len(self.decisions),
            "avg_inference_ms": sum(inference_times) / len(inference_times),
            "p95_inference_ms": sorted_times[min(p95_idx, len(sorted_times) - 1)],
            "parse_failure_rate": failures / len(self.decisions),
            "total_tokens": sum(
                d.get("prompt_tokens", 0) + d.get("completion_tokens", 0)
                for d in self.decisions
            ),
        }
