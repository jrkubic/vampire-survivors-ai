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
