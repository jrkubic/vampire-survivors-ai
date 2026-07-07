import math
from src.config import PLAYER_SIZE, PLAYER_INVINCIBILITY_TICKS


def check_circle_collision(
    x1: float, y1: float, r1: float,
    x2: float, y2: float, r2: float,
) -> bool:
    dist = math.hypot(x2 - x1, y2 - y1)
    return dist <= r1 + r2


def apply_contact_damage(player, enemies: list) -> None:
    """Check all alive enemies for collision with player. Apply damage + invincibility."""
    if player.invincibility_timer > 0:
        return

    for enemy in enemies:
        if not enemy.alive:
            continue
        if check_circle_collision(player.x, player.y, PLAYER_SIZE,
                                   enemy.x, enemy.y, enemy.size):
            player.take_damage(enemy.contact_damage)
            player.invincibility_timer = PLAYER_INVINCIBILITY_TICKS
            return  # only take damage from one enemy per tick


def check_projectile_hits(player, projectiles: list) -> None:
    """Check enemy projectiles for collision with player."""
    if player.invincibility_timer > 0:
        return

    for proj in projectiles:
        if proj.friendly or not proj.alive:
            continue
        if check_circle_collision(player.x, player.y, PLAYER_SIZE,
                                   proj.x, proj.y, proj.size):
            player.take_damage(proj.damage)
            player.invincibility_timer = PLAYER_INVINCIBILITY_TICKS
            proj.alive = False
            return
