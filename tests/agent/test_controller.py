from unittest.mock import MagicMock, patch
from src.agent.controller import StepLockController


class TestStepLockController:
    def _make_controller(self):
        game = MagicMock()
        game.is_over.side_effect = [False, False, True]  # run for 2 ticks
        game.get_state.return_value = {
            "player": {"x": 100, "y": 100, "hp": 100, "max_hp": 100, "attack_range": 60, "attack_cooldown": 0},
            "enemies": [],
            "projectiles": [],
            "pickups": [],
            "arena": {"width": 2000, "height": 2000, "elapsed_ticks": 1, "wave_number": 1},
        }
        game.tick.return_value = game.get_state.return_value

        client = MagicMock()
        client.generate.return_value = {
            "response": "I see no threats. none",
            "prompt_eval_count": 50,
            "eval_count": 10,
            "error": None,
        }

        return StepLockController(game=game, client=client), game, client

    def test_step_calls_llm_and_ticks_game(self):
        ctrl, game, client = self._make_controller()
        result = ctrl.step()
        assert client.generate.called
        assert game.tick.called
        assert result["action_chosen"] == "none"
        assert result["inference_time_ms"] >= 0

    def test_step_logs_metrics(self):
        ctrl, game, client = self._make_controller()
        ctrl.step()
        assert len(ctrl.metrics.decisions) == 1

    def test_step_handles_llm_error(self):
        ctrl, game, client = self._make_controller()
        client.generate.return_value = {"response": "", "prompt_eval_count": 0, "eval_count": 0, "error": "connection refused"}
        result = ctrl.step()
        assert result["action_chosen"] == "none"
        assert result["action_parse_success"] is False
