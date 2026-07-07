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
