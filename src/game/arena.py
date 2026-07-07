import math
import random
from dataclasses import dataclass, field
from src.config import (
    ARENA_WIDTH, ARENA_HEIGHT, PLAYER_SIZE, PICKUP_SIZE,
    WAVE_INTERVAL, INITIAL_ENEMIES_PER_WAVE, ENEMIES_PER_WAVE_INCREASE,
    HEALTH_PICKUP_HEAL, XP_PICKUP_VALUE, PICKUP_DROP_CHANCE,
)
from src.game.enemy import Enemy
from src.game.projectile import Projectile
from src.game.pickup import Pickup
from src.game.collision import check_circle_collision


@dataclass
class Arena:
    width: int = ARENA_WIDTH
    height: int = ARENA_HEIGHT
    enemies: list = field(default_factory=list)
    projectiles: list = field(default_factory=list)
    pickups: list = field(default_factory=list)
    wave_number: int = 0
    wave_timer: int = 0
    elapsed_ticks: int = 0

    def clamp_to_bounds(self, player) -> None:
        player.x = max(PLAYER_SIZE, min(self.width - PLAYER_SIZE, player.x))
        player.y = max(PLAYER_SIZE, min(self.height - PLAYER_SIZE, player.y))

    def spawn_wave(self, player) -> None:
        self.wave_number += 1
        count = INITIAL_ENEMIES_PER_WAVE + (self.wave_number - 1) * ENEMIES_PER_WAVE_INCREASE
        enemy_types = ["swarmer", "swarmer", "swarmer", "tank", "shooter"]

        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            dist = random.uniform(400, 600)
            ex = player.x + math.cos(angle) * dist
            ey = player.y + math.sin(angle) * dist
            # Clamp to arena
            ex = max(0, min(self.width, ex))
            ey = max(0, min(self.height, ey))
            etype = random.choice(enemy_types)
            self.enemies.append(Enemy(x=ex, y=ey, enemy_type=etype))

    def try_collect_pickups(self, player) -> None:
        remaining = []
        for pickup in self.pickups:
            if not pickup.alive:
                continue
            if check_circle_collision(player.x, player.y, PLAYER_SIZE,
                                      pickup.x, pickup.y, pickup.size):
                if pickup.pickup_type == "health":
                    player.heal(HEALTH_PICKUP_HEAL)
                elif pickup.pickup_type == "xp":
                    player.xp += XP_PICKUP_VALUE
            else:
                remaining.append(pickup)
        self.pickups = remaining

    def drop_pickup(self, x: float, y: float) -> None:
        if random.random() < PICKUP_DROP_CHANCE:
            ptype = random.choice(["health", "xp"])
            self.pickups.append(Pickup(x=x, y=y, pickup_type=ptype))

    def get_game_state(self, player) -> dict:
        return {
            "player": player.to_dict(),
            "enemies": [e.to_dict() for e in self.enemies if e.alive],
            "projectiles": [p.to_dict() for p in self.projectiles if p.alive],
            "pickups": [p.to_dict() for p in self.pickups if p.alive],
            "arena": {
                "width": self.width,
                "height": self.height,
                "elapsed_ticks": self.elapsed_ticks,
                "wave_number": self.wave_number,
            },
        }
