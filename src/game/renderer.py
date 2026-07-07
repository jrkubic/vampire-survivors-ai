# src/game/renderer.py
import pygame
from src.config import SCREEN_WIDTH, SCREEN_HEIGHT, PLAYER_SIZE, PLAYER_ATTACK_RANGE

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
DARK_GRAY = (30, 30, 30)
GRID_COLOR = (40, 40, 40)
PLAYER_COLOR = (80, 180, 255)
PLAYER_ATTACK_COLOR = (80, 180, 255, 40)
SWARMER_COLOR = (255, 80, 80)
TANK_COLOR = (180, 100, 50)
SHOOTER_COLOR = (180, 50, 180)
PROJECTILE_COLOR = (255, 255, 80)
HEALTH_COLOR = (80, 255, 80)
XP_COLOR = (80, 80, 255)
HP_BAR_BG = (60, 60, 60)
HP_BAR_FG = (80, 255, 80)
HP_BAR_LOW = (255, 80, 80)

ENEMY_COLORS = {
    "swarmer": SWARMER_COLOR,
    "tank": TANK_COLOR,
    "shooter": SHOOTER_COLOR,
}


class Renderer:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.font = pygame.font.SysFont("consolas", 16)
        self.big_font = pygame.font.SysFont("consolas", 32)

    def render(self, player, arena) -> None:
        self.screen.fill(DARK_GRAY)

        # Camera offset: center player on screen
        cam_x = player.x - SCREEN_WIDTH // 2
        cam_y = player.y - SCREEN_HEIGHT // 2

        self._draw_grid(cam_x, cam_y)
        self._draw_arena_border(arena, cam_x, cam_y)
        self._draw_pickups(arena.pickups, cam_x, cam_y)
        self._draw_enemies(arena.enemies, cam_x, cam_y)
        self._draw_projectiles(arena.projectiles, cam_x, cam_y)
        self._draw_player(player, cam_x, cam_y)
        self._draw_hud(player, arena)

        if not player.alive:
            self._draw_game_over(player, arena)

        pygame.display.flip()

    def _draw_grid(self, cam_x: float, cam_y: float) -> None:
        grid_size = 100
        start_x = int(-cam_x % grid_size)
        start_y = int(-cam_y % grid_size)
        for x in range(start_x, SCREEN_WIDTH, grid_size):
            pygame.draw.line(self.screen, GRID_COLOR, (x, 0), (x, SCREEN_HEIGHT))
        for y in range(start_y, SCREEN_HEIGHT, grid_size):
            pygame.draw.line(self.screen, GRID_COLOR, (0, y), (SCREEN_WIDTH, y))

    def _draw_arena_border(self, arena, cam_x: float, cam_y: float) -> None:
        rect = pygame.Rect(-cam_x, -cam_y, arena.width, arena.height)
        pygame.draw.rect(self.screen, WHITE, rect, 2)

    def _draw_player(self, player, cam_x: float, cam_y: float) -> None:
        sx = int(player.x - cam_x)
        sy = int(player.y - cam_y)

        # Attack range circle
        attack_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.circle(attack_surface, (80, 180, 255, 30), (sx, sy), int(PLAYER_ATTACK_RANGE))
        self.screen.blit(attack_surface, (0, 0))

        # Player body
        color = PLAYER_COLOR if player.invincibility_timer % 4 < 2 else WHITE
        pygame.draw.circle(self.screen, color, (sx, sy), int(PLAYER_SIZE))

    def _draw_enemies(self, enemies: list, cam_x: float, cam_y: float) -> None:
        for e in enemies:
            if not e.alive:
                continue
            sx = int(e.x - cam_x)
            sy = int(e.y - cam_y)
            color = ENEMY_COLORS.get(e.enemy_type, SWARMER_COLOR)
            pygame.draw.circle(self.screen, color, (sx, sy), int(e.size))

    def _draw_projectiles(self, projectiles: list, cam_x: float, cam_y: float) -> None:
        for p in projectiles:
            if not p.alive:
                continue
            sx = int(p.x - cam_x)
            sy = int(p.y - cam_y)
            pygame.draw.circle(self.screen, PROJECTILE_COLOR, (sx, sy), int(p.size))

    def _draw_pickups(self, pickups: list, cam_x: float, cam_y: float) -> None:
        for p in pickups:
            if not p.alive:
                continue
            sx = int(p.x - cam_x)
            sy = int(p.y - cam_y)
            color = HEALTH_COLOR if p.pickup_type == "health" else XP_COLOR
            pygame.draw.rect(self.screen, color, (sx - 5, sy - 5, 10, 10))

    def _draw_hud(self, player, arena) -> None:
        # HP bar
        bar_w, bar_h = 200, 16
        bar_x, bar_y = 10, 10
        ratio = player.hp / player.max_hp
        color = HP_BAR_FG if ratio > 0.3 else HP_BAR_LOW
        pygame.draw.rect(self.screen, HP_BAR_BG, (bar_x, bar_y, bar_w, bar_h))
        pygame.draw.rect(self.screen, color, (bar_x, bar_y, int(bar_w * ratio), bar_h))
        hp_text = self.font.render(f"HP: {player.hp}/{player.max_hp}", True, WHITE)
        self.screen.blit(hp_text, (bar_x + bar_w + 10, bar_y - 2))

        # Stats
        wave_text = self.font.render(f"Wave: {arena.wave_number}", True, WHITE)
        xp_text = self.font.render(f"XP: {player.xp}", True, WHITE)
        time_text = self.font.render(f"Ticks: {arena.elapsed_ticks}", True, WHITE)
        enemies_text = self.font.render(f"Enemies: {sum(1 for e in arena.enemies if e.alive)}", True, WHITE)
        self.screen.blit(wave_text, (10, 35))
        self.screen.blit(xp_text, (10, 55))
        self.screen.blit(time_text, (10, 75))
        self.screen.blit(enemies_text, (10, 95))

    def _draw_game_over(self, player, arena) -> None:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        go_text = self.big_font.render("GAME OVER", True, (255, 80, 80))
        score_text = self.font.render(
            f"Survived {arena.elapsed_ticks} ticks | Wave {arena.wave_number} | XP: {player.xp}",
            True, WHITE
        )
        restart_text = self.font.render("Press R to restart or ESC to quit", True, WHITE)
        self.screen.blit(go_text, (SCREEN_WIDTH // 2 - go_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 30))
