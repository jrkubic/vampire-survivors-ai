from dataclasses import dataclass
from src.config import PICKUP_SIZE


@dataclass
class Pickup:
    x: float = 0.0
    y: float = 0.0
    pickup_type: str = "xp"  # "health" or "xp"
    size: float = PICKUP_SIZE
    alive: bool = True

    def to_dict(self) -> dict:
        return {"x": self.x, "y": self.y, "type": self.pickup_type}
