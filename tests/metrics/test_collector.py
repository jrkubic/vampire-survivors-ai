import os
import csv
from src.metrics.collector import MetricsCollector


class TestMetricsCollector:
    def test_log_decision_stores_metrics(self):
        mc = MetricsCollector(run_id="test_run")
        mc.log_decision({
            "tick": 1,
            "inference_time_ms": 250.5,
            "action_chosen": "up",
            "action_parse_success": True,
            "player_hp": 100,
        })
        assert len(mc.decisions) == 1
        assert mc.decisions[0]["tick"] == 1

    def test_save_creates_csv(self, tmp_path):
        mc = MetricsCollector(run_id="test_run", output_dir=str(tmp_path))
        mc.log_decision({"tick": 1, "action_chosen": "up", "inference_time_ms": 100.0})
        mc.log_decision({"tick": 2, "action_chosen": "down", "inference_time_ms": 150.0})
        filepath = mc.save()
        assert os.path.exists(filepath)
        with open(filepath) as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        assert len(rows) == 2
        assert rows[0]["tick"] == "1"
        assert rows[1]["action_chosen"] == "down"

    def test_get_summary(self):
        mc = MetricsCollector(run_id="test_run")
        mc.log_decision({"tick": 1, "inference_time_ms": 100.0, "action_parse_success": True, "player_hp": 100})
        mc.log_decision({"tick": 2, "inference_time_ms": 200.0, "action_parse_success": True, "player_hp": 80})
        mc.log_decision({"tick": 3, "inference_time_ms": 300.0, "action_parse_success": False, "player_hp": 60})
        summary = mc.get_summary()
        assert summary["total_ticks"] == 3
        assert summary["avg_inference_ms"] == 200.0
        assert abs(summary["parse_failure_rate"] - 1/3) < 0.01
