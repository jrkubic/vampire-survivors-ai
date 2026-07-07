import time
import math
from src.agent.llm_client import OllamaClient
from src.agent.state_serializer import serialize_game_state
from src.agent.action_parser import parse_action
from src.metrics.collector import MetricsCollector


class StepLockController:
    def __init__(self, game, client: OllamaClient = None, run_id: str = None):
        self.game = game
        self.client = client or OllamaClient()
        self.run_id = run_id or f"ai_run_{int(time.time())}"
        self.metrics = MetricsCollector(run_id=self.run_id)

    def step(self) -> dict:
        """Execute one step-lock cycle: get state -> LLM -> action -> tick."""
        state = self.game.get_state()
        prompt = serialize_game_state(state)

        start = time.perf_counter()
        llm_result = self.client.generate(prompt)
        inference_ms = (time.perf_counter() - start) * 1000

        direction, parse_success = parse_action(llm_result["response"])

        self.game.tick(direction)

        # Compute contextual metrics
        player = state["player"]
        enemies = state["enemies"]
        pickups = state["pickups"]
        threats_in_range = sum(
            1 for e in enemies
            if math.hypot(e["x"] - player["x"], e["y"] - player["y"]) <= player["attack_range"] * 2
        )
        nearest_threat = min(
            (math.hypot(e["x"] - player["x"], e["y"] - player["y"]) for e in enemies),
            default=float("inf"),
        )
        nearest_pickup = min(
            (math.hypot(p["x"] - player["x"], p["y"] - player["y"]) for p in pickups),
            default=float("inf"),
        )

        metric = {
            "tick": state["arena"]["elapsed_ticks"],
            "inference_time_ms": round(inference_ms, 2),
            "prompt_tokens": llm_result.get("prompt_eval_count", 0),
            "completion_tokens": llm_result.get("eval_count", 0),
            "game_state_size_bytes": len(prompt.encode("utf-8")),
            "action_chosen": direction,
            "action_parse_success": parse_success,
            "llm_reasoning": llm_result["response"][:200],
            "player_hp": player["hp"],
            "enemies_alive": len(enemies),
            "threats_in_range": threats_in_range,
            "nearest_threat_dist": round(nearest_threat, 1) if nearest_threat != float("inf") else -1,
            "nearest_pickup_dist": round(nearest_pickup, 1) if nearest_pickup != float("inf") else -1,
        }
        self.metrics.log_decision(metric)
        return metric

    def run(self, max_ticks: int = None, render: bool = True) -> str:
        """Run the step-lock loop until game over or max_ticks. Returns path to saved metrics CSV."""
        import pygame
        from src.config import SCREEN_WIDTH, SCREEN_HEIGHT
        from src.game.renderer import Renderer

        screen = None
        renderer = None
        if render:
            pygame.init()
            screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            pygame.display.set_caption("Vampire Survivors AI — Step-Lock Mode")
            renderer = Renderer(screen)

        tick_count = 0
        while not self.game.is_over():
            if max_ticks and tick_count >= max_ticks:
                break

            if render:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return self.metrics.save()
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        return self.metrics.save()

            result = self.step()
            tick_count += 1

            if render and renderer:
                renderer.render(self.game.player, self.game.arena)

            # Print progress every 10 ticks
            if tick_count % 10 == 0:
                print(f"Tick {tick_count} | HP: {result['player_hp']} | "
                      f"Enemies: {result['enemies_alive']} | "
                      f"Action: {result['action_chosen']} | "
                      f"Inference: {result['inference_time_ms']:.0f}ms")

        filepath = self.metrics.save()
        summary = self.metrics.get_summary()
        print(f"\n--- Run Complete ---")
        print(f"Survived: {summary.get('total_ticks', 0)} ticks")
        print(f"Avg inference: {summary.get('avg_inference_ms', 0):.0f}ms")
        print(f"P95 inference: {summary.get('p95_inference_ms', 0):.0f}ms")
        print(f"Parse failures: {summary.get('parse_failure_rate', 0):.1%}")
        print(f"Metrics saved to: {filepath}")

        if render:
            # Show game over screen briefly
            import time as t
            t.sleep(3)
            pygame.quit()

        return filepath
