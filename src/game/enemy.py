# src/game/enemy.py
import math
from dataclasses import dataclass
from src.config import (
    SWARMER_SPEED, SWARMER_HP, SWARMER_CONTACT_DAMAGE, SWARMER_SIZE,
    TANK_SPEED, TANK_HP, TANK_CONTACT_DAMAGE, TANK_SIZE,
    SHOOTER_SPEED, SHOOTER_HP, SHOOTER_CONTACT_DAMAGE, SHOOTER_SIZE,
    SHOOTER_FIRE_RANGE, SHOOTER_FIRE_COOLDOWN,
    PROJECTILE_SPEED, PROJECTILE_DAMAGE, PROJECTILE_SIZE, PROJECTILE_LIFETIME,
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
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.hypot(dx, dy)
        if dist > 0:
            self.x += (dx / dist) * self.speed
            self.y += (dy / dist) * self.speed

    def update(self, player_x: float, player_y: float) -> list:
        """Update enemy for one tick. Returns list of new projectile dicts."""
        if not self.alive:
            return []

        dist_to_player = math.hypot(player_x - self.x, player_y - self.y)

        if self.enemy_type == "shooter":
            return self._update_shooter(player_x, player_y, dist_to_player)

        # Swarmers and tanks just move toward player
        self.move_toward(player_x, player_y)
        return []

    def _update_shooter(self, player_x: float, player_y: float, dist: float) -> list:
        if self.fire_timer > 0:
            self.fire_timer -= 1

        if dist <= SHOOTER_FIRE_RANGE:
            # In range — stop and fire if off cooldown
            if self.fire_timer <= 0:
                self.fire_timer = SHOOTER_FIRE_COOLDOWN
                dx = player_x - self.x
                dy = player_y - self.y
                length = math.hypot(dx, dy)
                if length > 0:
                    return [{
                        "x": self.x,
                        "y": self.y,
                        "dx": (dx / length) * PROJECTILE_SPEED,
                        "dy": (dy / length) * PROJECTILE_SPEED,
                        "damage": PROJECTILE_DAMAGE,
                        "size": PROJECTILE_SIZE,
                        "lifetime": PROJECTILE_LIFETIME,
                        "friendly": False,
                    }]
            return []
        else:
            # Out of range — move toward player
            self.move_toward(player_x, player_y)
            return []

    def to_dict(self) -> dict:
        return {
            "x": self.x,
            "y": self.y,
            "type": self.enemy_type,
            "hp": self.hp,
            "speed": self.speed,
        }
