import math
from dataclasses import dataclass
from src.config import (
    SWARMER_SPEED, SWARMER_HP, SWARMER_CONTACT_DAMAGE, SWARMER_SIZE,
    TANK_SPEED, TANK_HP, TANK_CONTACT_DAMAGE, TANK_SIZE,
    SHOOTER_SPEED, SHOOTER_HP, SHOOTER_CONTACT_DAMAGE, SHOOTER_SIZE,
    SHOOTER_FIRE_RANGE, SHOOTER_FIRE_COOLDOWN,
)

ENEMY_STATS = {
    "swarmer": {"speed": SWARMER_SPEED, "hp": SWARMER_HP, "contact_damage": SWARMER_CONTACT_DAMAGE, "size": SWARMER_SIZE},
    "tank": {"speed": TANK_SPEED, "hp": TANK_HP, "contact_damage": TANK_CONTACT_DAMAGE, "size": TANK_SIZE},
    "shooter": {"speed": SHOOTER_SPEED, "hp": SHOOTER_HP, "contact_damage": SHOOTER_CONTACT_DAMAGE, "size": SHOOTER_SIZE},
}


@dataclass
class Enemy:
    x: float = 0.0
    y: float = 0.0
    enemy_type: str = "swarmer"
    hp: int = 0
    max_hp: int = 0
    speed: float = 0.0
    contact_damage: int = 0
    size: float = 0.0
    alive: bool = True
    fire_timer: int = 0

    def __post_init__(self):
        stats = ENEMY_STATS.get(self.enemy_type, ENEMY_STATS["swarmer"])
        if self.hp == 0:
            self.hp = stats["hp"]
        if self.max_hp == 0:
            self.max_hp = stats["hp"]
        if self.speed == 0.0:
            self.speed = stats["speed"]
        if self.contact_damage == 0:
            self.contact_damage = stats["contact_damage"]
        if self.size == 0.0:
            self.size = stats["size"]

    def take_damage(self, amount: int) -> None:
        self.hp = max(0, self.hp - amount)
        if self.hp == 0:
            self.alive = False

    def move_toward(self, target_x: float, target_y: float) -> None:
        """Move toward a target position. Full implementation in Task 2."""
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.hypot(dx, dy)
        if dist > 0:
            self.x += (dx / dist) * self.speed
            self.y += (dy / dist) * self.speed

    def to_dict(self) -> dict:
        return {
            "x": self.x, "y": self.y,
            "type": self.enemy_type,
            "hp": self.hp, "speed": self.speed,
        }
