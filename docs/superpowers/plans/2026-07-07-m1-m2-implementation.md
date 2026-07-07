# M1 + M2 Implementation Plan: Pygame VS Clone & Step-Lock AI

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a playable Vampire Survivors clone in Pygame, then integrate a locally-run LLM (Ollama + Llama 3.1 8B) that plays the game via step-lock control loop with per-decision metric logging.

**Architecture:** Three-layer system — Game Layer (Pygame entities + logic, no rendering dependency for core logic), Agent Layer (state serializer + action parser + controller), LLM Layer (Ollama REST API). All game logic is pure Python math testable without Pygame. Rendering is isolated in `renderer.py`.

**Tech Stack:** Python 3.10+, Pygame 2.5+, requests, pandas, matplotlib, pytest, Ollama

## Global Constraints

- Python 3.10+ required (dataclasses, match statements)
- All game logic must be testable without a Pygame display
- Rendering is isolated in `renderer.py` — no other game module imports `pygame`
- All entity positions use float (x, y) coordinates
- Arena coordinate space: (0, 0) is top-left, y increases downward
- `pytest` for all tests, `unittest.mock` for mocking (no extra deps)
- Commit after every task

---

## File Map

### Created in this plan:

| File | Responsibility | Created in Task |
|---|---|---|
| `src/__init__.py` | Package init | 1 |
| `src/config.py` | All game constants and tunable values | 1 |
| `src/game/__init__.py` | Package init | 1 |
| `src/game/player.py` | Player entity: movement, HP, auto-attack | 1 |
| `src/game/enemy.py` | 3 enemy types, movement AI, contact damage | 2 |
| `src/game/projectile.py` | Projectile movement, lifetime | 3 |
| `src/game/collision.py` | Circle-circle collision, contact damage | 3 |
| `src/game/pickup.py` | Health/XP pickups, collection | 4 |
| `src/game/arena.py` | Arena bounds, wave spawner, game state export | 4 |
| `src/game/main.py` | Game loop, input handling, mode switching | 5 |
| `src/game/renderer.py` | All Pygame drawing code | 5 |
| `src/agent/__init__.py` | Package init | 6 |
| `src/agent/llm_client.py` | Ollama REST API wrapper | 6 |
| `src/agent/action_parser.py` | LLM response → direction string | 6 |
| `src/agent/state_serializer.py` | GameState dict → natural language prompt | 7 |
| `src/agent/controller.py` | Step-lock agent loop | 8 |
| `src/metrics/__init__.py` | Package init | 8 |
| `src/metrics/collector.py` | Per-decision CSV metric logging | 8 |
| `scripts/run_human.py` | Entry point: human plays the game | 5 |
| `scripts/run_ai.py` | Entry point: LLM plays the game | 8 |
| `tests/conftest.py` | Shared fixtures | 1 |
| `tests/game/test_player.py` | Player unit tests | 1 |
| `tests/game/test_enemy.py` | Enemy unit tests | 2 |
| `tests/game/test_projectile.py` | Projectile unit tests | 3 |
| `tests/game/test_collision.py` | Collision unit tests | 3 |
| `tests/game/test_pickup.py` | Pickup unit tests | 4 |
| `tests/game/test_arena.py` | Arena + wave spawner tests | 4 |
| `tests/agent/test_llm_client.py` | Ollama client tests (mocked) | 6 |
| `tests/agent/test_action_parser.py` | Action parser tests | 6 |
| `tests/agent/test_state_serializer.py` | State serializer tests | 7 |
| `tests/agent/test_controller.py` | Step-lock controller tests (mocked) | 8 |
| `tests/metrics/test_collector.py` | Metric collector tests | 8 |

---

### Task 1: Player Entity

**Files:**
- Create: `src/config.py`
- Create: `src/game/__init__.py`
- Create: `src/game/player.py`
- Create: `tests/conftest.py`
- Create: `tests/game/__init__.py`
- Create: `tests/game/test_player.py`

**Interfaces:**
- Consumes: nothing (first task)
- Produces:
  - `Player(x: float, y: float)` — dataclass with `move(direction: str)`, `take_damage(amount: int)`, `heal(amount: int)`, `update_attack(enemies: list) -> list[Enemy]`, `to_dict() -> dict`
  - `DIRECTION_VECTORS: dict[str, tuple[float, float]]` — maps direction strings to (dx, dy) unit vectors
  - Config constants: `PLAYER_SPEED`, `PLAYER_HP`, `PLAYER_ATTACK_RANGE`, `PLAYER_ATTACK_DAMAGE`, `PLAYER_ATTACK_COOLDOWN`, `PLAYER_SIZE`, all enemy/arena/pickup constants

- [ ] **Step 1: Create config.py with all game constants**

```python
# src/config.py

# --- Screen ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# --- Arena ---
ARENA_WIDTH = 2000
ARENA_HEIGHT = 2000

# --- Player ---
PLAYER_SPEED = 3.0
PLAYER_HP = 100
PLAYER_ATTACK_RANGE = 60.0
PLAYER_ATTACK_DAMAGE = 25
PLAYER_ATTACK_COOLDOWN = 30  # ticks
PLAYER_SIZE = 16.0  # collision radius
PLAYER_INVINCIBILITY_TICKS = 30

# --- Enemies ---
SWARMER_SPEED = 2.5
SWARMER_HP = 30
SWARMER_CONTACT_DAMAGE = 5
SWARMER_SIZE = 10.0

TANK_SPEED = 1.0
TANK_HP = 150
TANK_CONTACT_DAMAGE = 15
TANK_SIZE = 20.0

SHOOTER_SPEED = 1.5
SHOOTER_HP = 50
SHOOTER_CONTACT_DAMAGE = 5
SHOOTER_SIZE = 14.0
SHOOTER_FIRE_RANGE = 200.0
SHOOTER_FIRE_COOLDOWN = 60  # ticks

# --- Projectiles ---
PROJECTILE_SPEED = 4.0
PROJECTILE_DAMAGE = 10
PROJECTILE_SIZE = 5.0
PROJECTILE_LIFETIME = 180  # ticks before despawn

# --- Pickups ---
HEALTH_PICKUP_HEAL = 25
XP_PICKUP_VALUE = 10
PICKUP_SIZE = 8.0
PICKUP_DROP_CHANCE = 0.3  # 30% chance enemy drops a pickup on death

# --- Waves ---
WAVE_INTERVAL = 300  # ticks between waves
INITIAL_ENEMIES_PER_WAVE = 5
ENEMIES_PER_WAVE_INCREASE = 2

# --- LLM ---
OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3.1:8b"
LLM_TEMPERATURE = 0.3
LLM_NUM_PREDICT = 100
```

- [ ] **Step 2: Create package init files**

```python
# src/__init__.py
# (empty)
```

```python
# src/game/__init__.py
# (empty)
```

```python
# tests/__init__.py
# (empty)
```

```python
# tests/game/__init__.py
# (empty)
```

```python
# tests/conftest.py
# Shared test fixtures
```

- [ ] **Step 3: Write failing tests for Player**

```python
# tests/game/test_player.py
import math
from src.game.player import Player, DIRECTION_VECTORS


class TestPlayerMovement:
    def test_move_right(self):
        p = Player(x=100.0, y=100.0)
        p.move("right")
        assert p.x == 103.0  # PLAYER_SPEED = 3.0
        assert p.y == 100.0

    def test_move_up(self):
        p = Player(x=100.0, y=100.0)
        p.move("up")
        assert p.x == 100.0
        assert p.y == 97.0

    def test_move_diagonal_normalized(self):
        p = Player(x=0.0, y=0.0)
        p.move("up-right")
        # Diagonal movement should be normalized so total speed = PLAYER_SPEED
        distance = math.hypot(p.x, p.y)
        assert abs(distance - 3.0) < 0.01

    def test_move_none_stays_still(self):
        p = Player(x=50.0, y=50.0)
        p.move("none")
        assert p.x == 50.0
        assert p.y == 50.0

    def test_move_invalid_direction_stays_still(self):
        p = Player(x=50.0, y=50.0)
        p.move("invalid")
        assert p.x == 50.0
        assert p.y == 50.0


class TestPlayerHP:
    def test_take_damage(self):
        p = Player(x=0.0, y=0.0)
        p.take_damage(30)
        assert p.hp == 70
        assert p.alive is True

    def test_lethal_damage(self):
        p = Player(x=0.0, y=0.0)
        p.take_damage(100)
        assert p.hp == 0
        assert p.alive is False

    def test_overkill_clamps_to_zero(self):
        p = Player(x=0.0, y=0.0)
        p.take_damage(999)
        assert p.hp == 0
        assert p.alive is False

    def test_heal(self):
        p = Player(x=0.0, y=0.0)
        p.take_damage(50)
        p.heal(25)
        assert p.hp == 75

    def test_heal_clamped_to_max(self):
        p = Player(x=0.0, y=0.0)
        p.take_damage(10)
        p.heal(999)
        assert p.hp == 100


class TestPlayerAutoAttack:
    def test_attacks_nearest_enemy_in_range(self):
        from src.game.enemy import Enemy
        p = Player(x=100.0, y=100.0)
        # Enemy within range (distance=30, range=60)
        e = Enemy(x=130.0, y=100.0, enemy_type="swarmer")
        hit = p.update_attack([e])
        assert len(hit) == 1
        assert e.hp == 30 - 25  # SWARMER_HP - PLAYER_ATTACK_DAMAGE

    def test_no_attack_when_on_cooldown(self):
        from src.game.enemy import Enemy
        p = Player(x=100.0, y=100.0)
        e = Enemy(x=130.0, y=100.0, enemy_type="swarmer")
        p.update_attack([e])  # first attack triggers cooldown
        e2 = Enemy(x=130.0, y=100.0, enemy_type="swarmer")
        hit = p.update_attack([e2])
        assert len(hit) == 0  # on cooldown

    def test_no_attack_when_out_of_range(self):
        from src.game.enemy import Enemy
        p = Player(x=0.0, y=0.0)
        e = Enemy(x=500.0, y=500.0, enemy_type="swarmer")
        hit = p.update_attack([e])
        assert len(hit) == 0

    def test_cooldown_ticks_down(self):
        from src.game.enemy import Enemy
        p = Player(x=100.0, y=100.0)
        e = Enemy(x=130.0, y=100.0, enemy_type="swarmer")
        p.update_attack([e])
        assert p.attack_timer == 30
        # Tick down the cooldown
        for _ in range(30):
            p.update_attack([])
        assert p.attack_timer == 0


class TestPlayerToDict:
    def test_to_dict_contains_required_keys(self):
        p = Player(x=10.0, y=20.0)
        d = p.to_dict()
        assert d["x"] == 10.0
        assert d["y"] == 20.0
        assert d["hp"] == 100
        assert d["max_hp"] == 100
        assert "attack_range" in d
        assert "attack_cooldown" in d


class TestDirectionVectors:
    def test_all_nine_directions_exist(self):
        expected = {"up", "down", "left", "right", "up-left", "up-right",
                    "down-left", "down-right", "none"}
        assert set(DIRECTION_VECTORS.keys()) == expected

    def test_cardinal_directions_are_unit_vectors(self):
        for d in ["up", "down", "left", "right"]:
            dx, dy = DIRECTION_VECTORS[d]
            length = math.hypot(dx, dy)
            assert abs(length - 1.0) < 0.01

    def test_diagonal_directions_are_normalized(self):
        for d in ["up-left", "up-right", "down-left", "down-right"]:
            dx, dy = DIRECTION_VECTORS[d]
            length = math.hypot(dx, dy)
            assert abs(length - 1.0) < 0.01
```

- [ ] **Step 4: Run tests to verify they fail**

Run: `cd "c:/Jake Old PC Docs/Resumes/vampire-survivors-ai" && python -m pytest tests/game/test_player.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'src.game.player'`

- [ ] **Step 5: Implement Player**

```python
# src/game/player.py
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
```

- [ ] **Step 6: Create minimal Enemy stub so Player tests can import it**

Player's `update_attack` tests import `Enemy`. Create a minimal stub that Task 2 will flesh out:

```python
# src/game/enemy.py
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
```

- [ ] **Step 7: Run tests to verify they pass**

Run: `cd "c:/Jake Old PC Docs/Resumes/vampire-survivors-ai" && python -m pytest tests/game/test_player.py -v`
Expected: All 16 tests PASS

- [ ] **Step 8: Commit**

```bash
cd "c:/Jake Old PC Docs/Resumes/vampire-survivors-ai"
git add src/__init__.py src/config.py src/game/__init__.py src/game/player.py src/game/enemy.py tests/__init__.py tests/conftest.py tests/game/__init__.py tests/game/test_player.py
git commit -m "feat(m1): add Player entity with movement, HP, and auto-attack"
```

---

### Task 2: Enemy System

**Files:**
- Modify: `src/game/enemy.py` (flesh out from stub)
- Create: `tests/game/test_enemy.py`

**Interfaces:**
- Consumes: `Player.x`, `Player.y` for movement targeting
- Produces:
  - `Enemy(x, y, enemy_type)` — dataclass with `move_toward(target_x, target_y)`, `update(player_x, player_y) -> list[Projectile]`, `take_damage(amount)`, `to_dict()`
  - `enemy_type` is one of `"swarmer"`, `"tank"`, `"shooter"`
  - `update()` returns a list of `Projectile` objects (empty for swarmer/tank, one projectile when shooter fires)

- [ ] **Step 1: Write failing tests for Enemy**

```python
# tests/game/test_enemy.py
import math
from src.game.enemy import Enemy
from src.config import (
    SWARMER_SPEED, SWARMER_HP, SWARMER_CONTACT_DAMAGE,
    TANK_SPEED, TANK_HP,
    SHOOTER_SPEED, SHOOTER_HP, SHOOTER_FIRE_RANGE, SHOOTER_FIRE_COOLDOWN,
)


class TestEnemyCreation:
    def test_swarmer_stats(self):
        e = Enemy(x=0.0, y=0.0, enemy_type="swarmer")
        assert e.hp == SWARMER_HP
        assert e.speed == SWARMER_SPEED
        assert e.contact_damage == SWARMER_CONTACT_DAMAGE

    def test_tank_stats(self):
        e = Enemy(x=0.0, y=0.0, enemy_type="tank")
        assert e.hp == TANK_HP
        assert e.speed == TANK_SPEED

    def test_shooter_stats(self):
        e = Enemy(x=0.0, y=0.0, enemy_type="shooter")
        assert e.hp == SHOOTER_HP
        assert e.speed == SHOOTER_SPEED


class TestEnemyMovement:
    def test_swarmer_moves_toward_player(self):
        e = Enemy(x=0.0, y=0.0, enemy_type="swarmer")
        e.move_toward(100.0, 0.0)
        assert e.x > 0.0  # moved right toward player
        assert abs(e.x - SWARMER_SPEED) < 0.01

    def test_tank_moves_slower(self):
        e = Enemy(x=0.0, y=0.0, enemy_type="tank")
        e.move_toward(100.0, 0.0)
        assert abs(e.x - TANK_SPEED) < 0.01

    def test_diagonal_movement_normalized(self):
        e = Enemy(x=0.0, y=0.0, enemy_type="swarmer")
        e.move_toward(100.0, 100.0)
        dist = math.hypot(e.x, e.y)
        assert abs(dist - SWARMER_SPEED) < 0.01


class TestShooterBehavior:
    def test_shooter_moves_when_far_from_player(self):
        e = Enemy(x=0.0, y=0.0, enemy_type="shooter")
        projectiles = e.update(500.0, 0.0)  # player is far away
        assert e.x > 0.0  # moved toward player
        assert len(projectiles) == 0  # too far to fire

    def test_shooter_stops_and_fires_when_in_range(self):
        e = Enemy(x=0.0, y=0.0, enemy_type="shooter")
        # Player within fire range
        projectiles = e.update(SHOOTER_FIRE_RANGE - 10, 0.0)
        assert e.x == 0.0  # didn't move — in firing range
        assert len(projectiles) == 1

    def test_shooter_respects_fire_cooldown(self):
        e = Enemy(x=0.0, y=0.0, enemy_type="shooter")
        e.update(SHOOTER_FIRE_RANGE - 10, 0.0)  # fires
        projectiles = e.update(SHOOTER_FIRE_RANGE - 10, 0.0)  # on cooldown
        assert len(projectiles) == 0


class TestEnemyUpdate:
    def test_swarmer_update_moves_toward_player(self):
        e = Enemy(x=0.0, y=0.0, enemy_type="swarmer")
        projectiles = e.update(100.0, 0.0)
        assert e.x > 0.0
        assert len(projectiles) == 0  # swarmers don't fire

    def test_tank_update_moves_toward_player(self):
        e = Enemy(x=0.0, y=0.0, enemy_type="tank")
        projectiles = e.update(100.0, 0.0)
        assert e.x > 0.0
        assert len(projectiles) == 0  # tanks don't fire


class TestEnemyDamage:
    def test_take_damage(self):
        e = Enemy(x=0.0, y=0.0, enemy_type="swarmer")
        e.take_damage(10)
        assert e.hp == SWARMER_HP - 10
        assert e.alive is True

    def test_lethal_damage(self):
        e = Enemy(x=0.0, y=0.0, enemy_type="swarmer")
        e.take_damage(SWARMER_HP)
        assert e.hp == 0
        assert e.alive is False


class TestEnemyToDict:
    def test_to_dict(self):
        e = Enemy(x=10.0, y=20.0, enemy_type="tank")
        d = e.to_dict()
        assert d["x"] == 10.0
        assert d["y"] == 20.0
        assert d["type"] == "tank"
        assert d["hp"] == TANK_HP
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd "c:/Jake Old PC Docs/Resumes/vampire-survivors-ai" && python -m pytest tests/game/test_enemy.py -v`
Expected: FAIL — `Enemy` has no `update` method yet

- [ ] **Step 3: Add `update` method to Enemy**

Modify `src/game/enemy.py` — add the `update` method and import `Projectile` (from Task 3, create forward reference):

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd "c:/Jake Old PC Docs/Resumes/vampire-survivors-ai" && python -m pytest tests/game/test_enemy.py tests/game/test_player.py -v`
Expected: All tests PASS (both player and enemy)

- [ ] **Step 5: Commit**

```bash
cd "c:/Jake Old PC Docs/Resumes/vampire-survivors-ai"
git add src/game/enemy.py tests/game/test_enemy.py
git commit -m "feat(m1): add Enemy system with swarmer, tank, and shooter types"
```

---

### Task 3: Projectile & Collision System

**Files:**
- Create: `src/game/projectile.py`
- Create: `src/game/collision.py`
- Create: `tests/game/test_projectile.py`
- Create: `tests/game/test_collision.py`

**Interfaces:**
- Consumes: Projectile dicts from `Enemy.update()` `{"x", "y", "dx", "dy", "damage", "size", "lifetime", "friendly"}`
- Produces:
  - `Projectile(x, y, dx, dy, damage, size, lifetime, friendly)` — dataclass with `update()`, `to_dict()`
  - `check_circle_collision(x1, y1, r1, x2, y2, r2) -> bool`
  - `apply_contact_damage(player: Player, enemies: list[Enemy]) -> None`

- [ ] **Step 1: Write failing tests**

```python
# tests/game/test_projectile.py
from src.game.projectile import Projectile


class TestProjectileMovement:
    def test_moves_by_velocity(self):
        p = Projectile(x=0.0, y=0.0, dx=4.0, dy=0.0)
        p.update()
        assert p.x == 4.0
        assert p.y == 0.0

    def test_lifetime_decreases(self):
        p = Projectile(x=0.0, y=0.0, dx=1.0, dy=0.0, lifetime=10)
        p.update()
        assert p.lifetime == 9

    def test_expires_when_lifetime_zero(self):
        p = Projectile(x=0.0, y=0.0, dx=1.0, dy=0.0, lifetime=1)
        p.update()
        assert p.alive is False

    def test_to_dict(self):
        p = Projectile(x=10.0, y=20.0, dx=1.0, dy=-1.0, damage=10)
        d = p.to_dict()
        assert d["x"] == 10.0
        assert d["y"] == 20.0
        assert d["dx"] == 1.0
        assert d["dy"] == -1.0
        assert d["damage"] == 10
        assert d["friendly"] is False
```

```python
# tests/game/test_collision.py
from src.game.collision import check_circle_collision, apply_contact_damage
from src.game.player import Player
from src.game.enemy import Enemy
from src.config import PLAYER_SIZE, SWARMER_SIZE, PLAYER_INVINCIBILITY_TICKS


class TestCircleCollision:
    def test_overlapping_circles(self):
        assert check_circle_collision(0, 0, 10, 5, 0, 10) is True

    def test_touching_circles(self):
        assert check_circle_collision(0, 0, 10, 20, 0, 10) is True

    def test_separated_circles(self):
        assert check_circle_collision(0, 0, 10, 100, 0, 10) is False


class TestContactDamage:
    def test_enemy_damages_player_on_overlap(self):
        p = Player(x=0.0, y=0.0)
        e = Enemy(x=5.0, y=0.0, enemy_type="swarmer")  # within collision range
        apply_contact_damage(p, [e])
        assert p.hp < 100

    def test_invincibility_prevents_damage(self):
        p = Player(x=0.0, y=0.0)
        p.invincibility_timer = 10
        e = Enemy(x=5.0, y=0.0, enemy_type="swarmer")
        apply_contact_damage(p, [e])
        assert p.hp == 100

    def test_contact_triggers_invincibility(self):
        p = Player(x=0.0, y=0.0)
        e = Enemy(x=5.0, y=0.0, enemy_type="swarmer")
        apply_contact_damage(p, [e])
        assert p.invincibility_timer == PLAYER_INVINCIBILITY_TICKS

    def test_dead_enemy_no_damage(self):
        p = Player(x=0.0, y=0.0)
        e = Enemy(x=5.0, y=0.0, enemy_type="swarmer")
        e.alive = False
        apply_contact_damage(p, [e])
        assert p.hp == 100
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd "c:/Jake Old PC Docs/Resumes/vampire-survivors-ai" && python -m pytest tests/game/test_projectile.py tests/game/test_collision.py -v`
Expected: FAIL — modules don't exist

- [ ] **Step 3: Implement Projectile**

```python
# src/game/projectile.py
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
```

- [ ] **Step 4: Implement collision helpers**

```python
# src/game/collision.py
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
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd "c:/Jake Old PC Docs/Resumes/vampire-survivors-ai" && python -m pytest tests/game/test_projectile.py tests/game/test_collision.py -v`
Expected: All tests PASS

- [ ] **Step 6: Run full test suite to check no regressions**

Run: `cd "c:/Jake Old PC Docs/Resumes/vampire-survivors-ai" && python -m pytest tests/ -v`
Expected: All tests PASS

- [ ] **Step 7: Commit**

```bash
cd "c:/Jake Old PC Docs/Resumes/vampire-survivors-ai"
git add src/game/projectile.py src/game/collision.py tests/game/test_projectile.py tests/game/test_collision.py
git commit -m "feat(m1): add projectile system and circle collision detection"
```

---

### Task 4: Pickups, Arena & Game State Export

**Files:**
- Create: `src/game/pickup.py`
- Create: `src/game/arena.py`
- Create: `tests/game/test_pickup.py`
- Create: `tests/game/test_arena.py`

**Interfaces:**
- Consumes: `Player`, `Enemy`, `Projectile` from earlier tasks
- Produces:
  - `Pickup(x, y, pickup_type)` — dataclass with `to_dict()`
  - `Arena` — class with `update(player) -> None`, `get_game_state() -> dict`, `spawn_wave()`, `clamp_to_bounds(player)`, `try_collect_pickups(player)`
  - `Arena.get_game_state() -> dict` returns the full state dict matching the spec's `GameState` interface

- [ ] **Step 1: Write failing tests**

```python
# tests/game/test_pickup.py
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
```

```python
# tests/game/test_arena.py
import math
from src.game.arena import Arena
from src.game.player import Player
from src.game.enemy import Enemy
from src.config import (
    ARENA_WIDTH, ARENA_HEIGHT, PLAYER_SIZE,
    INITIAL_ENEMIES_PER_WAVE, WAVE_INTERVAL,
)


class TestArenaBounds:
    def test_clamp_player_to_bounds(self):
        arena = Arena()
        p = Player(x=-100.0, y=-100.0)
        arena.clamp_to_bounds(p)
        assert p.x >= PLAYER_SIZE
        assert p.y >= PLAYER_SIZE

    def test_clamp_player_max_bounds(self):
        arena = Arena()
        p = Player(x=9999.0, y=9999.0)
        arena.clamp_to_bounds(p)
        assert p.x <= ARENA_WIDTH - PLAYER_SIZE
        assert p.y <= ARENA_HEIGHT - PLAYER_SIZE


class TestWaveSpawning:
    def test_first_wave_spawns_at_start(self):
        arena = Arena()
        player = Player(x=1000.0, y=1000.0)
        arena.spawn_wave(player)
        assert len(arena.enemies) == INITIAL_ENEMIES_PER_WAVE

    def test_enemies_spawn_outside_screen(self):
        arena = Arena()
        player = Player(x=1000.0, y=1000.0)
        arena.spawn_wave(player)
        for e in arena.enemies:
            dist = math.hypot(e.x - player.x, e.y - player.y)
            assert dist >= 400  # spawn at least 400px away

    def test_wave_counter_increments(self):
        arena = Arena()
        player = Player(x=1000.0, y=1000.0)
        arena.spawn_wave(player)
        assert arena.wave_number == 1
        arena.spawn_wave(player)
        assert arena.wave_number == 2


class TestPickupCollection:
    def test_collect_health_pickup(self):
        arena = Arena()
        from src.game.pickup import Pickup
        arena.pickups.append(Pickup(x=10.0, y=10.0, pickup_type="health"))
        player = Player(x=10.0, y=10.0)
        player.take_damage(50)
        arena.try_collect_pickups(player)
        assert player.hp == 75  # 50 + HEALTH_PICKUP_HEAL(25)
        assert len(arena.pickups) == 0

    def test_collect_xp_pickup(self):
        arena = Arena()
        from src.game.pickup import Pickup
        arena.pickups.append(Pickup(x=10.0, y=10.0, pickup_type="xp"))
        player = Player(x=10.0, y=10.0)
        arena.try_collect_pickups(player)
        assert player.xp == 10
        assert len(arena.pickups) == 0


class TestGameState:
    def test_get_game_state_structure(self):
        arena = Arena()
        player = Player(x=100.0, y=200.0)
        state = arena.get_game_state(player)
        assert "player" in state
        assert "enemies" in state
        assert "projectiles" in state
        assert "pickups" in state
        assert "arena" in state
        assert state["player"]["x"] == 100.0
        assert state["arena"]["width"] == ARENA_WIDTH
        assert state["arena"]["height"] == ARENA_HEIGHT
        assert "wave_number" in state["arena"]
        assert "elapsed_ticks" in state["arena"]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd "c:/Jake Old PC Docs/Resumes/vampire-survivors-ai" && python -m pytest tests/game/test_pickup.py tests/game/test_arena.py -v`
Expected: FAIL — modules don't exist

- [ ] **Step 3: Implement Pickup**

```python
# src/game/pickup.py
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
```

- [ ] **Step 4: Implement Arena**

```python
# src/game/arena.py
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
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd "c:/Jake Old PC Docs/Resumes/vampire-survivors-ai" && python -m pytest tests/game/test_pickup.py tests/game/test_arena.py -v`
Expected: All tests PASS

- [ ] **Step 6: Run full test suite**

Run: `cd "c:/Jake Old PC Docs/Resumes/vampire-survivors-ai" && python -m pytest tests/ -v`
Expected: All tests PASS

- [ ] **Step 7: Commit**

```bash
cd "c:/Jake Old PC Docs/Resumes/vampire-survivors-ai"
git add src/game/pickup.py src/game/arena.py tests/game/test_pickup.py tests/game/test_arena.py
git commit -m "feat(m1): add pickups, arena bounds, wave spawner, and game state export"
```

---

### Task 5: Renderer, Game Loop & Human Play Mode

**Files:**
- Create: `src/game/renderer.py`
- Create: `src/game/main.py`
- Create: `scripts/run_human.py`

**Interfaces:**
- Consumes: `Player`, `Enemy`, `Projectile`, `Pickup`, `Arena` from Tasks 1-4
- Produces:
  - `Renderer(screen)` — draws all entities, HUD, camera offset
  - `Game(mode="human"|"ai")` — main game loop class with `run()`, `tick(direction: str)`, `get_state() -> dict`, `is_over() -> bool`
  - `scripts/run_human.py` — runnable entry point

This task has no automated tests — it's Pygame rendering and input handling. Verified by running the game manually.

- [ ] **Step 1: Implement Renderer**

```python
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
```

- [ ] **Step 2: Implement Game loop**

```python
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
```

- [ ] **Step 3: Create run_human.py entry point**

```python
# scripts/run_human.py
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.game.main import Game

if __name__ == "__main__":
    game = Game()
    game.run_human()
```

- [ ] **Step 4: Manual test — run the game**

Run: `cd "c:/Jake Old PC Docs/Resumes/vampire-survivors-ai" && python scripts/run_human.py`

Verify:
- Window opens at 800x600
- Player (blue circle) appears at center of arena
- WASD moves player
- Enemies spawn in waves from edges
- Player auto-attacks nearby enemies (attack range circle visible)
- Projectiles fire from shooters (yellow dots)
- Health/XP pickups drop from dead enemies
- HP bar and stats display in top-left
- Game over screen on death, R to restart, ESC to quit

- [ ] **Step 5: Run full test suite to ensure no regressions**

Run: `cd "c:/Jake Old PC Docs/Resumes/vampire-survivors-ai" && python -m pytest tests/ -v`
Expected: All tests PASS

- [ ] **Step 6: Commit**

```bash
cd "c:/Jake Old PC Docs/Resumes/vampire-survivors-ai"
git add src/game/renderer.py src/game/main.py scripts/run_human.py
git commit -m "feat(m1): add renderer, game loop, and human play mode

Milestone 1 complete — playable Vampire Survivors clone with WASD
movement, auto-attack, 3 enemy types, projectiles, pickups, and HUD."
```

---

### Task 6: LLM Client & Action Parser

**Files:**
- Create: `src/agent/__init__.py`
- Create: `src/agent/llm_client.py`
- Create: `src/agent/action_parser.py`
- Create: `tests/agent/__init__.py`
- Create: `tests/agent/test_llm_client.py`
- Create: `tests/agent/test_action_parser.py`

**Interfaces:**
- Consumes: Nothing from game layer (standalone)
- Produces:
  - `OllamaClient(url, model)` — with `generate(prompt: str) -> dict` returning `{"response": str, "prompt_eval_count": int, "eval_count": int}`
  - `parse_action(llm_response: str) -> tuple[str, bool]` — returns `(direction, parse_success)`

- [ ] **Step 1: Write failing tests**

```python
# tests/agent/__init__.py
# (empty)
```

```python
# tests/agent/test_action_parser.py
from src.agent.action_parser import parse_action


class TestParseAction:
    def test_simple_direction(self):
        direction, success = parse_action("up")
        assert direction == "up"
        assert success is True

    def test_direction_in_sentence(self):
        direction, success = parse_action("I should move up-right to avoid the enemies.")
        assert direction == "up-right"
        assert success is True

    def test_direction_with_reasoning(self):
        direction, success = parse_action(
            "The biggest threat is from the north. I'll move down-left to escape.\n\ndown-left"
        )
        assert direction == "down-left"
        assert success is True

    def test_none_direction(self):
        direction, success = parse_action("I'll stay still. none")
        assert direction == "none"
        assert success is True

    def test_malformed_defaults_to_none(self):
        direction, success = parse_action("I'm not sure what to do here.")
        assert direction == "none"
        assert success is False

    def test_empty_response_defaults_to_none(self):
        direction, success = parse_action("")
        assert direction == "none"
        assert success is False

    def test_case_insensitive(self):
        direction, success = parse_action("UP-RIGHT")
        assert direction == "up-right"
        assert success is True

    def test_prefers_last_direction_found(self):
        direction, success = parse_action("I could go up but actually down is better. down")
        assert direction == "down"
        assert success is True
```

```python
# tests/agent/test_llm_client.py
from unittest.mock import patch, MagicMock
from src.agent.llm_client import OllamaClient


class TestOllamaClient:
    def test_generate_returns_response(self):
        client = OllamaClient()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "response": "I should move up to avoid the swarmers.\n\nup",
            "prompt_eval_count": 150,
            "eval_count": 30,
        }
        with patch("requests.post", return_value=mock_response):
            result = client.generate("test prompt")
            assert result["response"] == "I should move up to avoid the swarmers.\n\nup"
            assert result["prompt_eval_count"] == 150
            assert result["eval_count"] == 30

    def test_generate_handles_connection_error(self):
        client = OllamaClient()
        with patch("requests.post", side_effect=ConnectionError("refused")):
            result = client.generate("test prompt")
            assert result["response"] == ""
            assert result["error"] is not None

    def test_generate_handles_timeout(self):
        client = OllamaClient()
        with patch("requests.post", side_effect=TimeoutError("timeout")):
            result = client.generate("test prompt")
            assert result["response"] == ""
            assert result["error"] is not None
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd "c:/Jake Old PC Docs/Resumes/vampire-survivors-ai" && python -m pytest tests/agent/ -v`
Expected: FAIL — modules don't exist

- [ ] **Step 3: Implement action_parser**

```python
# src/agent/action_parser.py
import re

VALID_DIRECTIONS = [
    "up-left", "up-right", "down-left", "down-right",
    "up", "down", "left", "right", "none",
]

# Ordered longest-first so compound directions match before simple ones
_DIRECTION_PATTERN = re.compile(
    r"\b(" + "|".join(VALID_DIRECTIONS) + r")\b",
    re.IGNORECASE,
)


def parse_action(llm_response: str) -> tuple[str, bool]:
    """Extract a movement direction from LLM response text.

    Returns (direction, parse_success). If no valid direction is found,
    returns ("none", False).
    """
    if not llm_response.strip():
        return "none", False

    matches = _DIRECTION_PATTERN.findall(llm_response)
    if matches:
        return matches[-1].lower(), True

    return "none", False
```

- [ ] **Step 4: Implement llm_client**

```python
# src/agent/llm_client.py
import requests
from src.config import OLLAMA_URL, OLLAMA_MODEL, LLM_TEMPERATURE, LLM_NUM_PREDICT


class OllamaClient:
    def __init__(self, url: str = OLLAMA_URL, model: str = OLLAMA_MODEL):
        self.url = url
        self.model = model

    def generate(self, prompt: str) -> dict:
        """Send prompt to Ollama and return response dict.

        Returns dict with keys: response, prompt_eval_count, eval_count.
        On error, response="" and error=<error message>.
        """
        try:
            resp = requests.post(
                f"{self.url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": LLM_TEMPERATURE,
                        "num_predict": LLM_NUM_PREDICT,
                    },
                },
                timeout=30,
            )
            data = resp.json()
            return {
                "response": data.get("response", ""),
                "prompt_eval_count": data.get("prompt_eval_count", 0),
                "eval_count": data.get("eval_count", 0),
                "error": None,
            }
        except Exception as e:
            return {
                "response": "",
                "prompt_eval_count": 0,
                "eval_count": 0,
                "error": str(e),
            }
```

```python
# src/agent/__init__.py
# (empty)
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd "c:/Jake Old PC Docs/Resumes/vampire-survivors-ai" && python -m pytest tests/agent/ -v`
Expected: All tests PASS

- [ ] **Step 6: Run full test suite**

Run: `cd "c:/Jake Old PC Docs/Resumes/vampire-survivors-ai" && python -m pytest tests/ -v`
Expected: All tests PASS

- [ ] **Step 7: Commit**

```bash
cd "c:/Jake Old PC Docs/Resumes/vampire-survivors-ai"
git add src/agent/__init__.py src/agent/llm_client.py src/agent/action_parser.py tests/agent/__init__.py tests/agent/test_llm_client.py tests/agent/test_action_parser.py
git commit -m "feat(m2): add Ollama client and action parser"
```

---

### Task 7: State Serializer

**Files:**
- Create: `src/agent/state_serializer.py`
- Create: `tests/agent/test_state_serializer.py`

**Interfaces:**
- Consumes: `Arena.get_game_state(player) -> dict` (the GameState dict from Task 4)
- Produces:
  - `serialize_game_state(state: dict) -> str` — returns the natural language prompt string

- [ ] **Step 1: Write failing tests**

```python
# tests/agent/test_state_serializer.py
from src.agent.state_serializer import serialize_game_state


def _make_state(
    player=None, enemies=None, projectiles=None, pickups=None, arena=None
):
    return {
        "player": player or {"x": 500.0, "y": 500.0, "hp": 100, "max_hp": 100, "attack_range": 60.0, "attack_cooldown": 0},
        "enemies": enemies or [],
        "projectiles": projectiles or [],
        "pickups": pickups or [],
        "arena": arena or {"width": 2000, "height": 2000, "elapsed_ticks": 100, "wave_number": 2},
    }


class TestSerializeGameState:
    def test_includes_player_position(self):
        state = _make_state(player={"x": 200.0, "y": 300.0, "hp": 65, "max_hp": 100, "attack_range": 60.0, "attack_cooldown": 0})
        prompt = serialize_game_state(state)
        assert "(200, 300)" in prompt
        assert "65/100" in prompt

    def test_includes_enemy_info(self):
        state = _make_state(enemies=[
            {"x": 230.0, "y": 500.0, "type": "swarmer", "hp": 30, "speed": 2.5},
            {"x": 700.0, "y": 500.0, "type": "tank", "hp": 150, "speed": 1.0},
        ])
        prompt = serialize_game_state(state)
        assert "Swarmer" in prompt or "swarmer" in prompt.lower()
        assert "Tank" in prompt or "tank" in prompt.lower()

    def test_includes_projectile_info(self):
        state = _make_state(projectiles=[
            {"x": 480.0, "y": 500.0, "dx": -4.0, "dy": 0.0, "damage": 10, "friendly": False},
        ])
        prompt = serialize_game_state(state)
        assert "projectile" in prompt.lower()

    def test_includes_pickup_info(self):
        state = _make_state(pickups=[
            {"x": 600.0, "y": 600.0, "type": "health"},
        ])
        prompt = serialize_game_state(state)
        assert "health" in prompt.lower() or "Health" in prompt

    def test_includes_direction_instruction(self):
        prompt = serialize_game_state(_make_state())
        assert "up" in prompt and "down" in prompt and "left" in prompt and "right" in prompt

    def test_includes_arena_bounds_info(self):
        state = _make_state(
            player={"x": 50.0, "y": 1000.0, "hp": 100, "max_hp": 100, "attack_range": 60.0, "attack_cooldown": 0}
        )
        prompt = serialize_game_state(state)
        # Player is 50px from WEST wall — should mention nearness to wall
        assert "wall" in prompt.lower() or "bound" in prompt.lower() or "edge" in prompt.lower()

    def test_empty_enemies_says_no_enemies(self):
        state = _make_state(enemies=[])
        prompt = serialize_game_state(state)
        assert "no enemies" in prompt.lower() or "0 enemies" in prompt.lower()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd "c:/Jake Old PC Docs/Resumes/vampire-survivors-ai" && python -m pytest tests/agent/test_state_serializer.py -v`
Expected: FAIL — module doesn't exist

- [ ] **Step 3: Implement state_serializer**

```python
# src/agent/state_serializer.py
import math

SYSTEM_PROMPT = """You are an AI playing a Vampire Survivors-style game. Your character auto-attacks nearby enemies. You ONLY control movement.

Respond with EXACTLY one direction: up, down, left, right, up-left, up-right, down-left, down-right, or none.
Think briefly about the biggest threat, then choose."""


def _relative_direction(dx: float, dy: float) -> str:
    """Convert (dx, dy) offset into a cardinal/ordinal direction name."""
    if abs(dx) < 1 and abs(dy) < 1:
        return "HERE"
    angle = math.atan2(-dy, dx)  # -dy because y increases downward
    deg = math.degrees(angle) % 360
    if deg < 22.5 or deg >= 337.5:
        return "EAST"
    elif deg < 67.5:
        return "NORTHEAST"
    elif deg < 112.5:
        return "NORTH"
    elif deg < 157.5:
        return "NORTHWEST"
    elif deg < 202.5:
        return "WEST"
    elif deg < 247.5:
        return "SOUTHWEST"
    elif deg < 292.5:
        return "SOUTH"
    else:
        return "SOUTHEAST"


def _describe_enemies(enemies: list, player_x: float, player_y: float) -> str:
    if not enemies:
        return "- No enemies nearby."

    # Group by type and direction
    by_type = {}
    for e in enemies:
        etype = e["type"].capitalize()
        dist = math.hypot(e["x"] - player_x, e["y"] - player_y)
        direction = _relative_direction(e["x"] - player_x, e["y"] - player_y)
        by_type.setdefault(etype, []).append((dist, direction))

    lines = [f"- {len(enemies)} enemies nearby:"]
    for etype, entries in by_type.items():
        entries.sort(key=lambda x: x[0])
        closest_dist = int(entries[0][0])
        dirs = set(d for _, d in entries)
        dir_str = ", ".join(sorted(dirs))
        lines.append(f"  - {len(entries)} {etype}(s) from the {dir_str} (closest: {closest_dist}px)")
    return "\n".join(lines)


def _describe_projectiles(projectiles: list, player_x: float, player_y: float) -> str:
    hostile = [p for p in projectiles if not p.get("friendly", False)]
    if not hostile:
        return "- No incoming projectiles."

    lines = [f"- {len(hostile)} projectile(s) incoming:"]
    for p in hostile:
        dist = math.hypot(p["x"] - player_x, p["y"] - player_y)
        direction = _relative_direction(p["x"] - player_x, p["y"] - player_y)
        speed = math.hypot(p.get("dx", 0), p.get("dy", 0))
        eta = int(dist / speed) if speed > 0 else 999
        lines.append(f"  - From the {direction}, {int(dist)}px away (~{eta} ticks)")
    return "\n".join(lines)


def _describe_pickups(pickups: list, player_x: float, player_y: float) -> str:
    if not pickups:
        return "- No pickups nearby."

    lines = ["- Pickups:"]
    for p in pickups:
        dist = int(math.hypot(p["x"] - player_x, p["y"] - player_y))
        direction = _relative_direction(p["x"] - player_x, p["y"] - player_y)
        ptype = "Health potion" if p["type"] == "health" else "XP gem"
        lines.append(f"  - {ptype} {dist}px to the {direction}")
    return "\n".join(lines)


def _describe_arena_bounds(player_x: float, player_y: float, width: int, height: int) -> str:
    walls = []
    if player_x < 200:
        walls.append(f"{int(player_x)}px from WEST edge")
    if player_x > width - 200:
        walls.append(f"{int(width - player_x)}px from EAST edge")
    if player_y < 200:
        walls.append(f"{int(player_y)}px from NORTH edge")
    if player_y > height - 200:
        walls.append(f"{int(height - player_y)}px from SOUTH edge")
    if walls:
        return "- Arena bounds: " + ", ".join(walls)
    return "- Arena bounds: far from all edges"


def serialize_game_state(state: dict) -> str:
    player = state["player"]
    px, py = player["x"], player["y"]
    arena = state["arena"]

    sections = [
        SYSTEM_PROMPT,
        "",
        "CURRENT STATE:",
        f"- Your position: ({int(px)}, {int(py)}), HP: {player['hp']}/{player['max_hp']}",
        _describe_enemies(state["enemies"], px, py),
        _describe_projectiles(state["projectiles"], px, py),
        _describe_pickups(state["pickups"], px, py),
        _describe_arena_bounds(px, py, arena["width"], arena["height"]),
        f"- Wave: {arena['wave_number']}, Ticks survived: {arena['elapsed_ticks']}",
    ]

    return "\n".join(sections)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd "c:/Jake Old PC Docs/Resumes/vampire-survivors-ai" && python -m pytest tests/agent/test_state_serializer.py -v`
Expected: All tests PASS

- [ ] **Step 5: Run full test suite**

Run: `cd "c:/Jake Old PC Docs/Resumes/vampire-survivors-ai" && python -m pytest tests/ -v`
Expected: All tests PASS

- [ ] **Step 6: Commit**

```bash
cd "c:/Jake Old PC Docs/Resumes/vampire-survivors-ai"
git add src/agent/state_serializer.py tests/agent/test_state_serializer.py
git commit -m "feat(m2): add game state serializer for natural language prompts"
```

---

### Task 8: Step-Lock Controller, Metrics Collector & AI Play Mode

**Files:**
- Create: `src/agent/controller.py`
- Create: `src/metrics/__init__.py`
- Create: `src/metrics/collector.py`
- Create: `scripts/run_ai.py`
- Create: `tests/metrics/__init__.py`
- Create: `tests/metrics/test_collector.py`
- Create: `tests/agent/test_controller.py`

**Interfaces:**
- Consumes:
  - `Game.tick(direction) -> dict`, `Game.get_state() -> dict`, `Game.is_over() -> bool` from Task 5
  - `OllamaClient.generate(prompt) -> dict` from Task 6
  - `parse_action(response) -> tuple[str, bool]` from Task 6
  - `serialize_game_state(state) -> str` from Task 7
- Produces:
  - `StepLockController(game: Game, client: OllamaClient)` with `run() -> None`, `step() -> dict`
  - `MetricsCollector(run_id: str)` with `log_decision(metric: dict)`, `save() -> str`
  - `scripts/run_ai.py` — runnable entry point

- [ ] **Step 1: Write failing tests for MetricsCollector**

```python
# tests/metrics/__init__.py
# (empty)
```

```python
# tests/metrics/test_collector.py
import os
import csv
from src.metrics.collector import MetricsCollector


class TestMetricsCollector:
    def test_log_decision_stores_metrics(self):
        mc = MetricsCollector(run_id="test_run")
        mc.log_decision({
            "tick": 1,
            "inference_time_ms": 250.5,
            "action_chosen": "up",
            "action_parse_success": True,
            "player_hp": 100,
        })
        assert len(mc.decisions) == 1
        assert mc.decisions[0]["tick"] == 1

    def test_save_creates_csv(self, tmp_path):
        mc = MetricsCollector(run_id="test_run", output_dir=str(tmp_path))
        mc.log_decision({"tick": 1, "action_chosen": "up", "inference_time_ms": 100.0})
        mc.log_decision({"tick": 2, "action_chosen": "down", "inference_time_ms": 150.0})
        filepath = mc.save()
        assert os.path.exists(filepath)
        with open(filepath) as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        assert len(rows) == 2
        assert rows[0]["tick"] == "1"
        assert rows[1]["action_chosen"] == "down"

    def test_get_summary(self):
        mc = MetricsCollector(run_id="test_run")
        mc.log_decision({"tick": 1, "inference_time_ms": 100.0, "action_parse_success": True, "player_hp": 100})
        mc.log_decision({"tick": 2, "inference_time_ms": 200.0, "action_parse_success": True, "player_hp": 80})
        mc.log_decision({"tick": 3, "inference_time_ms": 300.0, "action_parse_success": False, "player_hp": 60})
        summary = mc.get_summary()
        assert summary["total_ticks"] == 3
        assert summary["avg_inference_ms"] == 200.0
        assert abs(summary["parse_failure_rate"] - 1/3) < 0.01
```

- [ ] **Step 2: Write failing tests for StepLockController**

```python
# tests/agent/test_controller.py
from unittest.mock import MagicMock, patch
from src.agent.controller import StepLockController


class TestStepLockController:
    def _make_controller(self):
        game = MagicMock()
        game.is_over.side_effect = [False, False, True]  # run for 2 ticks
        game.get_state.return_value = {
            "player": {"x": 100, "y": 100, "hp": 100, "max_hp": 100, "attack_range": 60, "attack_cooldown": 0},
            "enemies": [],
            "projectiles": [],
            "pickups": [],
            "arena": {"width": 2000, "height": 2000, "elapsed_ticks": 1, "wave_number": 1},
        }
        game.tick.return_value = game.get_state.return_value

        client = MagicMock()
        client.generate.return_value = {
            "response": "I see no threats. none",
            "prompt_eval_count": 50,
            "eval_count": 10,
            "error": None,
        }

        return StepLockController(game=game, client=client), game, client

    def test_step_calls_llm_and_ticks_game(self):
        ctrl, game, client = self._make_controller()
        result = ctrl.step()
        assert client.generate.called
        assert game.tick.called
        assert result["action_chosen"] == "none"
        assert result["inference_time_ms"] >= 0

    def test_step_logs_metrics(self):
        ctrl, game, client = self._make_controller()
        ctrl.step()
        assert len(ctrl.metrics.decisions) == 1

    def test_step_handles_llm_error(self):
        ctrl, game, client = self._make_controller()
        client.generate.return_value = {"response": "", "prompt_eval_count": 0, "eval_count": 0, "error": "connection refused"}
        result = ctrl.step()
        assert result["action_chosen"] == "none"
        assert result["action_parse_success"] is False
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `cd "c:/Jake Old PC Docs/Resumes/vampire-survivors-ai" && python -m pytest tests/metrics/test_collector.py tests/agent/test_controller.py -v`
Expected: FAIL — modules don't exist

- [ ] **Step 4: Implement MetricsCollector**

```python
# src/metrics/__init__.py
# (empty)
```

```python
# src/metrics/collector.py
import csv
import os
import time
from dataclasses import dataclass, field


class MetricsCollector:
    def __init__(self, run_id: str, output_dir: str = "data/runs"):
        self.run_id = run_id
        self.output_dir = output_dir
        self.decisions: list[dict] = []
        self.start_time = time.time()

    def log_decision(self, metric: dict) -> None:
        metric.setdefault("timestamp", time.time() - self.start_time)
        self.decisions.append(metric)

    def save(self) -> str:
        os.makedirs(self.output_dir, exist_ok=True)
        filepath = os.path.join(self.output_dir, f"{self.run_id}.csv")
        if not self.decisions:
            return filepath

        fieldnames = list(self.decisions[0].keys())
        # Ensure all keys from all decisions are included
        for d in self.decisions:
            for k in d:
                if k not in fieldnames:
                    fieldnames.append(k)

        with open(filepath, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(self.decisions)

        return filepath

    def get_summary(self) -> dict:
        if not self.decisions:
            return {}

        inference_times = [d.get("inference_time_ms", 0) for d in self.decisions]
        parse_results = [d.get("action_parse_success", True) for d in self.decisions]
        failures = sum(1 for p in parse_results if not p)

        sorted_times = sorted(inference_times)
        p95_idx = int(len(sorted_times) * 0.95)

        return {
            "total_ticks": len(self.decisions),
            "avg_inference_ms": sum(inference_times) / len(inference_times),
            "p95_inference_ms": sorted_times[min(p95_idx, len(sorted_times) - 1)],
            "parse_failure_rate": failures / len(self.decisions),
            "total_tokens": sum(
                d.get("prompt_tokens", 0) + d.get("completion_tokens", 0)
                for d in self.decisions
            ),
        }
```

- [ ] **Step 5: Implement StepLockController**

```python
# src/agent/controller.py
import time
import math
from src.agent.llm_client import OllamaClient
from src.agent.state_serializer import serialize_game_state
from src.agent.action_parser import parse_action
from src.metrics.collector import MetricsCollector


class StepLockController:
    def __init__(self, game, client: OllamaClient = None, run_id: str = None):
        self.game = game
        self.client = client or OllamaClient()
        self.run_id = run_id or f"ai_run_{int(time.time())}"
        self.metrics = MetricsCollector(run_id=self.run_id)

    def step(self) -> dict:
        """Execute one step-lock cycle: get state → LLM → action → tick."""
        state = self.game.get_state()
        prompt = serialize_game_state(state)

        start = time.perf_counter()
        llm_result = self.client.generate(prompt)
        inference_ms = (time.perf_counter() - start) * 1000

        direction, parse_success = parse_action(llm_result["response"])

        self.game.tick(direction)

        # Compute contextual metrics
        player = state["player"]
        enemies = state["enemies"]
        pickups = state["pickups"]
        threats_in_range = sum(
            1 for e in enemies
            if math.hypot(e["x"] - player["x"], e["y"] - player["y"]) <= player["attack_range"] * 2
        )
        nearest_threat = min(
            (math.hypot(e["x"] - player["x"], e["y"] - player["y"]) for e in enemies),
            default=float("inf"),
        )
        nearest_pickup = min(
            (math.hypot(p["x"] - player["x"], p["y"] - player["y"]) for p in pickups),
            default=float("inf"),
        )

        metric = {
            "tick": state["arena"]["elapsed_ticks"],
            "inference_time_ms": round(inference_ms, 2),
            "prompt_tokens": llm_result.get("prompt_eval_count", 0),
            "completion_tokens": llm_result.get("eval_count", 0),
            "game_state_size_bytes": len(prompt.encode("utf-8")),
            "action_chosen": direction,
            "action_parse_success": parse_success,
            "llm_reasoning": llm_result["response"][:200],
            "player_hp": player["hp"],
            "enemies_alive": len(enemies),
            "threats_in_range": threats_in_range,
            "nearest_threat_dist": round(nearest_threat, 1) if nearest_threat != float("inf") else -1,
            "nearest_pickup_dist": round(nearest_pickup, 1) if nearest_pickup != float("inf") else -1,
        }
        self.metrics.log_decision(metric)
        return metric

    def run(self, max_ticks: int = None, render: bool = True) -> str:
        """Run the step-lock loop until game over or max_ticks. Returns path to saved metrics CSV."""
        import pygame
        from src.config import SCREEN_WIDTH, SCREEN_HEIGHT
        from src.game.renderer import Renderer

        screen = None
        renderer = None
        if render:
            pygame.init()
            screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            pygame.display.set_caption("Vampire Survivors AI — Step-Lock Mode")
            renderer = Renderer(screen)

        tick_count = 0
        while not self.game.is_over():
            if max_ticks and tick_count >= max_ticks:
                break

            if render:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return self.metrics.save()
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        return self.metrics.save()

            result = self.step()
            tick_count += 1

            if render and renderer:
                renderer.render(self.game.player, self.game.arena)

            # Print progress every 10 ticks
            if tick_count % 10 == 0:
                print(f"Tick {tick_count} | HP: {result['player_hp']} | "
                      f"Enemies: {result['enemies_alive']} | "
                      f"Action: {result['action_chosen']} | "
                      f"Inference: {result['inference_time_ms']:.0f}ms")

        filepath = self.metrics.save()
        summary = self.metrics.get_summary()
        print(f"\n--- Run Complete ---")
        print(f"Survived: {summary.get('total_ticks', 0)} ticks")
        print(f"Avg inference: {summary.get('avg_inference_ms', 0):.0f}ms")
        print(f"P95 inference: {summary.get('p95_inference_ms', 0):.0f}ms")
        print(f"Parse failures: {summary.get('parse_failure_rate', 0):.1%}")
        print(f"Metrics saved to: {filepath}")

        if render:
            # Show game over screen briefly
            import time as t
            t.sleep(3)
            pygame.quit()

        return filepath
```

- [ ] **Step 6: Create run_ai.py entry point**

```python
# scripts/run_ai.py
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.game.main import Game
from src.agent.controller import StepLockController
from src.agent.llm_client import OllamaClient

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run AI-controlled Vampire Survivors")
    parser.add_argument("--no-render", action="store_true", help="Run without rendering (faster)")
    parser.add_argument("--max-ticks", type=int, default=None, help="Max ticks before stopping")
    parser.add_argument("--model", type=str, default=None, help="Ollama model override")
    args = parser.parse_args()

    game = Game()
    client = OllamaClient()
    if args.model:
        client.model = args.model

    controller = StepLockController(game=game, client=client)
    print(f"Starting AI run with model: {client.model}")
    print(f"Render: {not args.no_render}")
    print("Press ESC to stop early.\n")

    controller.run(max_ticks=args.max_ticks, render=not args.no_render)
```

- [ ] **Step 7: Run tests to verify they pass**

Run: `cd "c:/Jake Old PC Docs/Resumes/vampire-survivors-ai" && python -m pytest tests/metrics/test_collector.py tests/agent/test_controller.py -v`
Expected: All tests PASS

- [ ] **Step 8: Run full test suite**

Run: `cd "c:/Jake Old PC Docs/Resumes/vampire-survivors-ai" && python -m pytest tests/ -v`
Expected: All tests PASS

- [ ] **Step 9: Integration test — run AI mode (requires Ollama running)**

Prereq: `ollama pull llama3.1:8b` and Ollama server running.

Run: `cd "c:/Jake Old PC Docs/Resumes/vampire-survivors-ai" && python scripts/run_ai.py --max-ticks 20`

Verify:
- Game window opens
- LLM makes decisions each tick (printed to console)
- Game advances after each LLM response
- Metrics CSV created in `data/runs/`
- Summary printed on completion

- [ ] **Step 10: Commit**

```bash
cd "c:/Jake Old PC Docs/Resumes/vampire-survivors-ai"
git add src/agent/controller.py src/metrics/__init__.py src/metrics/collector.py scripts/run_ai.py tests/metrics/__init__.py tests/metrics/test_collector.py tests/agent/test_controller.py
git commit -m "feat(m2): add step-lock controller, metrics collector, and AI play mode

Milestone 2 complete — LLM plays the game via step-lock loop with
per-decision metrics logging to CSV."
```

- [ ] **Step 11: Push all work to GitHub**

```bash
cd "c:/Jake Old PC Docs/Resumes/vampire-survivors-ai"
git push origin main
```
