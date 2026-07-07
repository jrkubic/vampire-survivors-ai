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
