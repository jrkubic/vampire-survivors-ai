import math
from src.game.player import Player, DIRECTION_VECTORS


class TestPlayerMovement:
    def test_move_right(self):
        p = Player(x=100.0, y=100.0)
        p.move("right")
        assert p.x == 103.0  # PLAYER_SPEED = 3.0
        assert p.y == 100.0

    def test_move_up(self):
        p = Player(x=100.0, y=100.0)
        p.move("up")
        assert p.x == 100.0
        assert p.y == 97.0

    def test_move_diagonal_normalized(self):
        p = Player(x=0.0, y=0.0)
        p.move("up-right")
        # Diagonal movement should be normalized so total speed = PLAYER_SPEED
        distance = math.hypot(p.x, p.y)
        assert abs(distance - 3.0) < 0.01

    def test_move_none_stays_still(self):
        p = Player(x=50.0, y=50.0)
        p.move("none")
        assert p.x == 50.0
        assert p.y == 50.0

    def test_move_invalid_direction_stays_still(self):
        p = Player(x=50.0, y=50.0)
        p.move("invalid")
        assert p.x == 50.0
        assert p.y == 50.0


class TestPlayerHP:
    def test_take_damage(self):
        p = Player(x=0.0, y=0.0)
        p.take_damage(30)
        assert p.hp == 70
        assert p.alive is True

    def test_lethal_damage(self):
        p = Player(x=0.0, y=0.0)
        p.take_damage(100)
        assert p.hp == 0
        assert p.alive is False

    def test_overkill_clamps_to_zero(self):
        p = Player(x=0.0, y=0.0)
        p.take_damage(999)
        assert p.hp == 0
        assert p.alive is False

    def test_heal(self):
        p = Player(x=0.0, y=0.0)
        p.take_damage(50)
        p.heal(25)
        assert p.hp == 75

    def test_heal_clamped_to_max(self):
        p = Player(x=0.0, y=0.0)
        p.take_damage(10)
        p.heal(999)
        assert p.hp == 100


class TestPlayerAutoAttack:
    def test_attacks_nearest_enemy_in_range(self):
        from src.game.enemy import Enemy
        p = Player(x=100.0, y=100.0)
        # Enemy within range (distance=30, range=60)
        e = Enemy(x=130.0, y=100.0, enemy_type="swarmer")
        hit = p.update_attack([e])
        assert len(hit) == 1
        assert e.hp == 30 - 25  # SWARMER_HP - PLAYER_ATTACK_DAMAGE

    def test_no_attack_when_on_cooldown(self):
        from src.game.enemy import Enemy
        p = Player(x=100.0, y=100.0)
        e = Enemy(x=130.0, y=100.0, enemy_type="swarmer")
        p.update_attack([e])  # first attack triggers cooldown
        e2 = Enemy(x=130.0, y=100.0, enemy_type="swarmer")
        hit = p.update_attack([e2])
        assert len(hit) == 0  # on cooldown

    def test_no_attack_when_out_of_range(self):
        from src.game.enemy import Enemy
        p = Player(x=0.0, y=0.0)
        e = Enemy(x=500.0, y=500.0, enemy_type="swarmer")
        hit = p.update_attack([e])
        assert len(hit) == 0

    def test_cooldown_ticks_down(self):
        from src.game.enemy import Enemy
        p = Player(x=100.0, y=100.0)
        e = Enemy(x=130.0, y=100.0, enemy_type="swarmer")
        p.update_attack([e])
        assert p.attack_timer == 30
        # Tick down the cooldown
        for _ in range(30):
            p.update_attack([])
        assert p.attack_timer == 0


class TestPlayerToDict:
    def test_to_dict_contains_required_keys(self):
        p = Player(x=10.0, y=20.0)
        d = p.to_dict()
        assert d["x"] == 10.0
        assert d["y"] == 20.0
        assert d["hp"] == 100
        assert d["max_hp"] == 100
        assert "attack_range" in d
        assert "attack_cooldown" in d


class TestDirectionVectors:
    def test_all_nine_directions_exist(self):
        expected = {"up", "down", "left", "right", "up-left", "up-right",
                    "down-left", "down-right", "none"}
        assert set(DIRECTION_VECTORS.keys()) == expected

    def test_cardinal_directions_are_unit_vectors(self):
        for d in ["up", "down", "left", "right"]:
            dx, dy = DIRECTION_VECTORS[d]
            length = math.hypot(dx, dy)
            assert abs(length - 1.0) < 0.01

    def test_diagonal_directions_are_normalized(self):
        for d in ["up-left", "up-right", "down-left", "down-right"]:
            dx, dy = DIRECTION_VECTORS[d]
            length = math.hypot(dx, dy)
            assert abs(length - 1.0) < 0.01
