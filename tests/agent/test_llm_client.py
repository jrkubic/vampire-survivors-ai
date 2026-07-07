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
