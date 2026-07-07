from src.agent.state_serializer import serialize_game_state


def _make_state(
    player=None, enemies=None, projectiles=None, pickups=None, arena=None
):
    return {
        "player": player or {"x": 500.0, "y": 500.0, "hp": 100, "max_hp": 100, "attack_range": 60.0, "attack_cooldown": 0},
        "enemies": enemies or [],
        "projectiles": projectiles or [],
        "pickups": pickups or [],
        "arena": arena or {"width": 2000, "height": 2000, "elapsed_ticks": 100, "wave_number": 2},
    }


class TestSerializeGameState:
    def test_includes_player_position(self):
        state = _make_state(player={"x": 200.0, "y": 300.0, "hp": 65, "max_hp": 100, "attack_range": 60.0, "attack_cooldown": 0})
        prompt = serialize_game_state(state)
        assert "(200, 300)" in prompt
        assert "65/100" in prompt

    def test_includes_enemy_info(self):
        state = _make_state(enemies=[
            {"x": 230.0, "y": 500.0, "type": "swarmer", "hp": 30, "speed": 2.5},
            {"x": 700.0, "y": 500.0, "type": "tank", "hp": 150, "speed": 1.0},
        ])
        prompt = serialize_game_state(state)
        assert "Swarmer" in prompt or "swarmer" in prompt.lower()
        assert "Tank" in prompt or "tank" in prompt.lower()

    def test_includes_projectile_info(self):
        state = _make_state(projectiles=[
            {"x": 480.0, "y": 500.0, "dx": -4.0, "dy": 0.0, "damage": 10, "friendly": False},
        ])
        prompt = serialize_game_state(state)
        assert "projectile" in prompt.lower()

    def test_includes_pickup_info(self):
        state = _make_state(pickups=[
            {"x": 600.0, "y": 600.0, "type": "health"},
        ])
        prompt = serialize_game_state(state)
        assert "health" in prompt.lower() or "Health" in prompt

    def test_includes_direction_instruction(self):
        prompt = serialize_game_state(_make_state())
        assert "up" in prompt and "down" in prompt and "left" in prompt and "right" in prompt

    def test_includes_arena_bounds_info(self):
        state = _make_state(
            player={"x": 50.0, "y": 1000.0, "hp": 100, "max_hp": 100, "attack_range": 60.0, "attack_cooldown": 0}
        )
        prompt = serialize_game_state(state)
        # Player is 50px from WEST wall — should mention nearness to wall
        assert "wall" in prompt.lower() or "bound" in prompt.lower() or "edge" in prompt.lower()

    def test_empty_enemies_says_no_enemies(self):
        state = _make_state(enemies=[])
        prompt = serialize_game_state(state)
        assert "no enemies" in prompt.lower() or "0 enemies" in prompt.lower()
