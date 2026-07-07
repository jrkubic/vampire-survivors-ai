import math
from src.game.arena import Arena
from src.game.player import Player
from src.game.enemy import Enemy
from src.config import (
    ARENA_WIDTH, ARENA_HEIGHT, PLAYER_SIZE,
    INITIAL_ENEMIES_PER_WAVE, WAVE_INTERVAL,
)


class TestArenaBounds:
    def test_clamp_player_to_bounds(self):
        arena = Arena()
        p = Player(x=-100.0, y=-100.0)
        arena.clamp_to_bounds(p)
        assert p.x >= PLAYER_SIZE
        assert p.y >= PLAYER_SIZE

    def test_clamp_player_max_bounds(self):
        arena = Arena()
        p = Player(x=9999.0, y=9999.0)
        arena.clamp_to_bounds(p)
        assert p.x <= ARENA_WIDTH - PLAYER_SIZE
        assert p.y <= ARENA_HEIGHT - PLAYER_SIZE


class TestWaveSpawning:
    def test_first_wave_spawns_at_start(self):
        arena = Arena()
        player = Player(x=1000.0, y=1000.0)
        arena.spawn_wave(player)
        assert len(arena.enemies) == INITIAL_ENEMIES_PER_WAVE

    def test_enemies_spawn_outside_screen(self):
        arena = Arena()
        player = Player(x=1000.0, y=1000.0)
        arena.spawn_wave(player)
        for e in arena.enemies:
            dist = math.hypot(e.x - player.x, e.y - player.y)
            assert dist >= 400  # spawn at least 400px away

    def test_wave_counter_increments(self):
        arena = Arena()
        player = Player(x=1000.0, y=1000.0)
        arena.spawn_wave(player)
        assert arena.wave_number == 1
        arena.spawn_wave(player)
        assert arena.wave_number == 2


class TestPickupCollection:
    def test_collect_health_pickup(self):
        arena = Arena()
        from src.game.pickup import Pickup
        arena.pickups.append(Pickup(x=10.0, y=10.0, pickup_type="health"))
        player = Player(x=10.0, y=10.0)
        player.take_damage(50)
        arena.try_collect_pickups(player)
        assert player.hp == 75  # 50 + HEALTH_PICKUP_HEAL(25)
        assert len(arena.pickups) == 0

    def test_collect_xp_pickup(self):
        arena = Arena()
        from src.game.pickup import Pickup
        arena.pickups.append(Pickup(x=10.0, y=10.0, pickup_type="xp"))
        player = Player(x=10.0, y=10.0)
        arena.try_collect_pickups(player)
        assert player.xp == 10
        assert len(arena.pickups) == 0


class TestGameState:
    def test_get_game_state_structure(self):
        arena = Arena()
        player = Player(x=100.0, y=200.0)
        state = arena.get_game_state(player)
        assert "player" in state
        assert "enemies" in state
        assert "projectiles" in state
        assert "pickups" in state
        assert "arena" in state
        assert state["player"]["x"] == 100.0
        assert state["arena"]["width"] == ARENA_WIDTH
        assert state["arena"]["height"] == ARENA_HEIGHT
        assert "wave_number" in state["arena"]
        assert "elapsed_ticks" in state["arena"]
