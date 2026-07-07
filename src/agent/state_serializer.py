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
