from src.game.projectile import Projectile


class TestProjectileMovement:
    def test_moves_by_velocity(self):
        p = Projectile(x=0.0, y=0.0, dx=4.0, dy=0.0)
        p.update()
        assert p.x == 4.0
        assert p.y == 0.0

    def test_lifetime_decreases(self):
        p = Projectile(x=0.0, y=0.0, dx=1.0, dy=0.0, lifetime=10)
        p.update()
        assert p.lifetime == 9

    def test_expires_when_lifetime_zero(self):
        p = Projectile(x=0.0, y=0.0, dx=1.0, dy=0.0, lifetime=1)
        p.update()
        assert p.alive is False

    def test_to_dict(self):
        p = Projectile(x=10.0, y=20.0, dx=1.0, dy=-1.0, damage=10)
        d = p.to_dict()
        assert d["x"] == 10.0
        assert d["y"] == 20.0
        assert d["dx"] == 1.0
        assert d["dy"] == -1.0
        assert d["damage"] == 10
        assert d["friendly"] is False
