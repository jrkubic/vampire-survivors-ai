import math
from dataclasses import dataclass, field
from src.config import (
    PLAYER_SPEED, PLAYER_HP, PLAYER_ATTACK_RANGE,
    PLAYER_ATTACK_DAMAGE, PLAYER_ATTACK_COOLDOWN,
)

DIRECTION_VECTORS = {
    "up": (0.0, -1.0),
    "down": (0.0, 1.0),
    "left": (-1.0, 0.0),
    "right": (1.0, 0.0),
    "up-left": (-math.sqrt(2) / 2, -math.sqrt(2) / 2),
    "up-right": (math.sqrt(2) / 2, -math.sqrt(2) / 2),
    "down-left": (-math.sqrt(2) / 2, math.sqrt(2) / 2),
    "down-right": (math.sqrt(2) / 2, math.sqrt(2) / 2),
    "none": (0.0, 0.0),
}


@dataclass
class Player:
    x: float = 0.0
    y: float = 0.0
    hp: int = PLAYER_HP
    max_hp: int = PLAYER_HP
    speed: float = PLAYER_SPEED
    attack_range: float = PLAYER_ATTACK_RANGE
    attack_damage: int = PLAYER_ATTACK_DAMAGE
    attack_cooldown: int = PLAYER_ATTACK_COOLDOWN
    attack_timer: int = 0
    xp: int = 0
    alive: bool = True
    invincibility_timer: int = 0

    def move(self, direction: str) -> None:
        dx, dy = DIRECTION_VECTORS.get(direction, (0.0, 0.0))
        self.x += dx * self.speed
        self.y += dy * self.speed

    def take_damage(self, amount: int) -> None:
        if self.invincibility_timer > 0:
            return
        self.hp = max(0, self.hp - amount)
        if self.hp == 0:
            self.alive = False

    def heal(self, amount: int) -> None:
        self.hp = min(self.hp + amount, self.max_hp)

    def update_attack(self, enemies: list) -> list:
        """Auto-attack nearest enemy in range. Returns list of enemies hit."""
        if self.attack_timer > 0:
            self.attack_timer -= 1
            return []

        nearest = None
        nearest_dist = float("inf")
        for enemy in enemies:
            if not enemy.alive:
                continue
            dist = math.hypot(enemy.x - self.x, enemy.y - self.y)
            if dist <= self.attack_range and dist < nearest_dist:
                nearest = enemy
                nearest_dist = dist

        if nearest is not None:
            nearest.take_damage(self.attack_damage)
            self.attack_timer = self.attack_cooldown
            return [nearest]
        return []

    def to_dict(self) -> dict:
        return {
            "x": self.x,
            "y": self.y,
            "hp": self.hp,
            "max_hp": self.max_hp,
            "attack_range": self.attack_range,
            "attack_cooldown": self.attack_timer,
        }
