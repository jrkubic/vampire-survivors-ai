from dataclasses import dataclass
from src.config import PROJECTILE_SPEED, PROJECTILE_DAMAGE, PROJECTILE_SIZE, PROJECTILE_LIFETIME


@dataclass
class Projectile:
    x: float = 0.0
    y: float = 0.0
    dx: float = 0.0
    dy: float = 0.0
    damage: int = PROJECTILE_DAMAGE
    size: float = PROJECTILE_SIZE
    lifetime: int = PROJECTILE_LIFETIME
    friendly: bool = False
    alive: bool = True

    def update(self) -> None:
        self.x += self.dx
        self.y += self.dy
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.alive = False

    def to_dict(self) -> dict:
        return {
            "x": self.x,
            "y": self.y,
            "dx": self.dx,
            "dy": self.dy,
            "damage": self.damage,
            "friendly": self.friendly,
        }
