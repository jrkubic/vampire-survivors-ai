import math
from src.game.enemy import Enemy
from src.config import (
    SWARMER_SPEED, SWARMER_HP, SWARMER_CONTACT_DAMAGE,
    TANK_SPEED, TANK_HP,
    SHOOTER_SPEED, SHOOTER_HP, SHOOTER_FIRE_RANGE, SHOOTER_FIRE_COOLDOWN,
)


class TestEnemyCreation:
    def test_swarmer_stats(self):
        e = Enemy(x=0.0, y=0.0, enemy_type="swarmer")
        assert e.hp == SWARMER_HP
        assert e.speed == SWARMER_SPEED
        assert e.contact_damage == SWARMER_CONTACT_DAMAGE

    def test_tank_stats(self):
        e = Enemy(x=0.0, y=0.0, enemy_type="tank")
        assert e.hp == TANK_HP
        assert e.speed == TANK_SPEED

    def test_shooter_stats(self):
        e = Enemy(x=0.0, y=0.0, enemy_type="shooter")
        assert e.hp == SHOOTER_HP
        assert e.speed == SHOOTER_SPEED


class TestEnemyMovement:
    def test_swarmer_moves_toward_player(self):
        e = Enemy(x=0.0, y=0.0, enemy_type="swarmer")
        e.move_toward(100.0, 0.0)
        assert e.x > 0.0  # moved right toward player
        assert abs(e.x - SWARMER_SPEED) < 0.01

    def test_tank_moves_slower(self):
        e = Enemy(x=0.0, y=0.0, enemy_type="tank")
        e.move_toward(100.0, 0.0)
        assert abs(e.x - TANK_SPEED) < 0.01

    def test_diagonal_movement_normalized(self):
        e = Enemy(x=0.0, y=0.0, enemy_type="swarmer")
        e.move_toward(100.0, 100.0)
        dist = math.hypot(e.x, e.y)
        assert abs(dist - SWARMER_SPEED) < 0.01


class TestShooterBehavior:
    def test_shooter_moves_when_far_from_player(self):
        e = Enemy(x=0.0, y=0.0, enemy_type="shooter")
        projectiles = e.update(500.0, 0.0)  # player is far away
        assert e.x > 0.0  # moved toward player
        assert len(projectiles) == 0  # too far to fire

    def test_shooter_stops_and_fires_when_in_range(self):
        e = Enemy(x=0.0, y=0.0, enemy_type="shooter")
        # Player within fire range
        projectiles = e.update(SHOOTER_FIRE_RANGE - 10, 0.0)
        assert e.x == 0.0  # didn't move — in firing range
        assert len(projectiles) == 1

    def test_shooter_respects_fire_cooldown(self):
        e = Enemy(x=0.0, y=0.0, enemy_type="shooter")
        e.update(SHOOTER_FIRE_RANGE - 10, 0.0)  # fires
        projectiles = e.update(SHOOTER_FIRE_RANGE - 10, 0.0)  # on cooldown
        assert len(projectiles) == 0


class TestEnemyUpdate:
    def test_swarmer_update_moves_toward_player(self):
        e = Enemy(x=0.0, y=0.0, enemy_type="swarmer")
        projectiles = e.update(100.0, 0.0)
        assert e.x > 0.0
        assert len(projectiles) == 0  # swarmers don't fire

    def test_tank_update_moves_toward_player(self):
        e = Enemy(x=0.0, y=0.0, enemy_type="tank")
        projectiles = e.update(100.0, 0.0)
        assert e.x > 0.0
        assert len(projectiles) == 0  # tanks don't fire


class TestEnemyDamage:
    def test_take_damage(self):
        e = Enemy(x=0.0, y=0.0, enemy_type="swarmer")
        e.take_damage(10)
        assert e.hp == SWARMER_HP - 10
        assert e.alive is True

    def test_lethal_damage(self):
        e = Enemy(x=0.0, y=0.0, enemy_type="swarmer")
        e.take_damage(SWARMER_HP)
        assert e.hp == 0
        assert e.alive is False


class TestEnemyToDict:
    def test_to_dict(self):
        e = Enemy(x=10.0, y=20.0, enemy_type="tank")
        d = e.to_dict()
        assert d["x"] == 10.0
        assert d["y"] == 20.0
        assert d["type"] == "tank"
        assert d["hp"] == TANK_HP
