import os
import asyncio
from typing import List

import requests


class OpenAIEmbedder:
    """Embedder that calls OpenAI's embeddings API.

    Requires `OPENAI_API_KEY` in env.
    """

    def __init__(self, model: str = "text-embedding-3-small"):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = model
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY not set in environment")

    async def embed(self, texts: List[str]) -> List[List[float]]:
        # run blocking requests in a thread
        return await asyncio.get_running_loop().run_in_executor(None, self._embed_sync, texts)

    def _embed_sync(self, texts: List[str]) -> List[List[float]]:
        url = "https://api.openai.com/v1/embeddings"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {"model": self.model, "input": texts}
        resp = requests.post(url, json=payload, headers=headers, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        return [item["embedding"] for item in data.get("data", [])]


class OllamaEmbedder:
    """Simple Ollama adapter using local Ollama HTTP API (if available).

    Expects `OLLAMA_URL` env var (e.g., http://localhost:11434).
    """

    def __init__(self, model: str = "llama2"):
        self.base = os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.model = model

    async def embed(self, texts: List[str]) -> List[List[float]]:
        # Ollama embedding API varies; here we call a hypothetical endpoint
        return await asyncio.get_running_loop().run_in_executor(None, self._embed_sync, texts)

    def _embed_sync(self, texts: List[str]) -> List[List[float]]:
        url = f"{self.base}/embed"
        resp = requests.post(url, json={"model": self.model, "input": texts}, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        return data.get("embeddings", [])
