from src.game.pickup import Pickup
from src.game.player import Player
from src.config import HEALTH_PICKUP_HEAL, XP_PICKUP_VALUE, PICKUP_SIZE, PLAYER_SIZE


class TestPickup:
    def test_health_pickup_to_dict(self):
        p = Pickup(x=10.0, y=20.0, pickup_type="health")
        d = p.to_dict()
        assert d == {"x": 10.0, "y": 20.0, "type": "health"}

    def test_xp_pickup_to_dict(self):
        p = Pickup(x=5.0, y=5.0, pickup_type="xp")
        d = p.to_dict()
        assert d["type"] == "xp"
