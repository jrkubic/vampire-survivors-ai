# src/game/main.py
import pygame
from src.config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, ARENA_WIDTH, ARENA_HEIGHT, WAVE_INTERVAL, PLAYER_INVINCIBILITY_TICKS
from src.game.player import Player, DIRECTION_VECTORS
from src.game.arena import Arena
from src.game.projectile import Projectile
from src.game.collision import apply_contact_damage, check_projectile_hits


class Game:
    def __init__(self):
        self.player = Player(x=ARENA_WIDTH / 2, y=ARENA_HEIGHT / 2)
        self.arena = Arena()
        self.running = True

    def reset(self) -> None:
        self.player = Player(x=ARENA_WIDTH / 2, y=ARENA_HEIGHT / 2)
        self.arena = Arena()
        self.running = True

    def tick(self, direction: str) -> dict:
        """Advance game by one tick with given movement direction. Returns game state."""
        if not self.player.alive:
            return self.arena.get_game_state(self.player)

        self.arena.elapsed_ticks += 1

        # Player movement
        self.player.move(direction)
        self.arena.clamp_to_bounds(self.player)

        # Invincibility tick
        if self.player.invincibility_timer > 0:
            self.player.invincibility_timer -= 1

        # Wave spawning
        self.arena.wave_timer += 1
        if self.arena.wave_timer >= WAVE_INTERVAL or self.arena.elapsed_ticks == 1:
            self.arena.spawn_wave(self.player)
            self.arena.wave_timer = 0

        # Enemy updates
        new_projectile_dicts = []
        for enemy in self.arena.enemies:
            proj_dicts = enemy.update(self.player.x, self.player.y)
            new_projectile_dicts.extend(proj_dicts)

        # Convert projectile dicts to Projectile objects
        for pd in new_projectile_dicts:
            self.arena.projectiles.append(Projectile(
                x=pd["x"], y=pd["y"],
                dx=pd["dx"], dy=pd["dy"],
                damage=pd["damage"], size=pd["size"],
                lifetime=pd["lifetime"], friendly=pd["friendly"],
            ))

        # Projectile updates
        for p in self.arena.projectiles:
            p.update()

        # Clean up dead projectiles
        self.arena.projectiles = [p for p in self.arena.projectiles if p.alive]

        # Collision: enemies touching player
        apply_contact_damage(self.player, self.arena.enemies)

        # Collision: enemy projectiles hitting player
        check_projectile_hits(self.player, self.arena.projectiles)

        # Player auto-attack
        hit_enemies = self.player.update_attack(self.arena.enemies)

        # Drop pickups from dead enemies
        dead_enemies = [e for e in self.arena.enemies if not e.alive]
        for e in dead_enemies:
            self.arena.drop_pickup(e.x, e.y)

        # Clean up dead enemies
        self.arena.enemies = [e for e in self.arena.enemies if e.alive]

        # Pickup collection
        self.arena.try_collect_pickups(self.player)

        return self.arena.get_game_state(self.player)

    def get_state(self) -> dict:
        return self.arena.get_game_state(self.player)

    def is_over(self) -> bool:
        return not self.player.alive

    def run_human(self) -> None:
        """Run the game with human keyboard input."""
        pygame.init()
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vampire Survivors AI — Human Mode")
        clock = pygame.time.Clock()

        from src.game.renderer import Renderer
        renderer = Renderer(screen)

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    if event.key == pygame.K_r and not self.player.alive:
                        self.reset()

            if self.player.alive:
                direction = self._get_keyboard_direction()
                self.tick(direction)

            renderer.render(self.player, self.arena)
            clock.tick(FPS)

        pygame.quit()

    def _get_keyboard_direction(self) -> str:
        keys = pygame.key.get_pressed()
        up = keys[pygame.K_w] or keys[pygame.K_UP]
        down = keys[pygame.K_s] or keys[pygame.K_DOWN]
        left = keys[pygame.K_a] or keys[pygame.K_LEFT]
        right = keys[pygame.K_d] or keys[pygame.K_RIGHT]

        if up and left:
            return "up-left"
        if up and right:
            return "up-right"
        if down and left:
            return "down-left"
        if down and right:
            return "down-right"
        if up:
            return "up"
        if down:
            return "down"
        if left:
            return "left"
        if right:
            return "right"
        return "none"
