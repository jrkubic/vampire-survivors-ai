from src.game.collision import check_circle_collision, apply_contact_damage
from src.game.player import Player
from src.game.enemy import Enemy
from src.config import PLAYER_SIZE, SWARMER_SIZE, PLAYER_INVINCIBILITY_TICKS


class TestCircleCollision:
    def test_overlapping_circles(self):
        assert check_circle_collision(0, 0, 10, 5, 0, 10) is True

    def test_touching_circles(self):
        assert check_circle_collision(0, 0, 10, 20, 0, 10) is True

    def test_separated_circles(self):
        assert check_circle_collision(0, 0, 10, 100, 0, 10) is False


class TestContactDamage:
    def test_enemy_damages_player_on_overlap(self):
        p = Player(x=0.0, y=0.0)
        e = Enemy(x=5.0, y=0.0, enemy_type="swarmer")  # within collision range
        apply_contact_damage(p, [e])
        assert p.hp < 100

    def test_invincibility_prevents_damage(self):
        p = Player(x=0.0, y=0.0)
        p.invincibility_timer = 10
        e = Enemy(x=5.0, y=0.0, enemy_type="swarmer")
        apply_contact_damage(p, [e])
        assert p.hp == 100

    def test_contact_triggers_invincibility(self):
        p = Player(x=0.0, y=0.0)
        e = Enemy(x=5.0, y=0.0, enemy_type="swarmer")
        apply_contact_damage(p, [e])
        assert p.invincibility_timer == PLAYER_INVINCIBILITY_TICKS

    def test_dead_enemy_no_damage(self):
        p = Player(x=0.0, y=0.0)
        e = Enemy(x=5.0, y=0.0, enemy_type="swarmer")
        e.alive = False
        apply_contact_damage(p, [e])
        assert p.hp == 100
