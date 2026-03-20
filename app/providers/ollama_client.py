"""
Low-Level Ollama API Client.

HTTP-Client für die lokale Ollama-Instanz (Tags, Chat, Pull, etc.).
"""

import json
from typing import Any, AsyncGenerator, Dict, List, Optional

import aiohttp

OLLAMA_URL = "http://localhost:11434"


class OllamaClient:
    def __init__(self, session: aiohttp.ClientSession = None, base_url: str = OLLAMA_URL):
        self._session = session
        self._own_session = False
        self.base_url = base_url.rstrip("/")

    async def get_session(self) -> aiohttp.ClientSession:
        if self._session is None:
            timeout = aiohttp.ClientTimeout(total=300, connect=10)
            self._session = aiohttp.ClientSession(timeout=timeout)
            self._own_session = True
        return self._session

    async def close(self):
        if self._own_session and self._session:
            await self._session.close()

    async def get_models(self) -> List[Dict[str, Any]]:
        try:
            session = await self.get_session()
            async with session.get(f"{self.base_url}/api/tags") as r:
                if r.status != 200:
                    print(f"DEBUG: get_models returned HTTP {r.status}")
                    return []
                data = await r.json()
                return data.get("models", [])
        except Exception as e:
            print(f"Ollama API unreachable (get_models): {e}")
            return []

    async def get_version(self) -> Optional[str]:
        try:
            session = await self.get_session()
            async with session.get(f"{self.base_url}/api/version") as r:
                if r.status != 200:
                    print(f"DEBUG: get_version returned HTTP {r.status}")
                    return None
                data = await r.json()
                return data.get("version") or data.get("ollama_version") or json.dumps(data)
        except Exception as e:
            print(f"Ollama API unreachable (get_version): {e}")
            return None

    async def get_processes(self) -> List[Dict[str, Any]]:
        try:
            session = await self.get_session()
            async with session.get(f"{self.base_url}/api/ps") as r:
                if r.status != 200:
                    print(f"DEBUG: get_processes returned HTTP {r.status}")
                    return []
                data = await r.json()
                return data.get("models", [])
        except Exception as e:
            print(f"Ollama API unreachable (get_processes): {e}")
            return []

    async def get_debug_info(self) -> Dict[str, Any]:
        info: Dict[str, Any] = {
            "online": False,
            "base_url": self.base_url,
            "version": None,
            "models": [],
            "model_count": 0,
            "processes": [],
            "vram_used_mib": None,
        }
        models = await self.get_models()
        info["models"] = [m.get("name") for m in models]
        info["model_count"] = len(models)
        info["online"] = len(models) > 0
        version = await self.get_version()
        if version:
            info["version"] = version
            info["online"] = True
        processes = await self.get_processes()
        info["processes"] = processes
        total_vram_mib = 0.0
        for p in processes:
            vram_mib = None
            if "size_vram_mib" in p:
                vram_mib = p.get("size_vram_mib")
            elif "size_vram" in p:
                try:
                    vram_bytes = float(p.get("size_vram") or 0)
                    vram_mib = vram_bytes / (1024 * 1024)
                except Exception:
                    vram_mib = None
            if isinstance(vram_mib, (int, float)):
                total_vram_mib += float(vram_mib)
        if total_vram_mib > 0:
            info["vram_used_mib"] = round(total_vram_mib, 1)
        return info

    async def pull_model(self, model: str) -> AsyncGenerator[Dict[str, Any], None]:
        session = await self.get_session()
        async with session.post(f"{self.base_url}/api/pull", json={"name": model}) as r:
            r.raise_for_status()
            async for line in r.content:
                chunk = line.decode("utf-8").strip()
                if chunk:
                    yield json.loads(chunk)

    def _build_chat_payload(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
        stream: bool,
        think: Any = None,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "model": model,
            "messages": messages,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
            "stream": stream,
        }
        model_lower = (model or "").lower()
        if think is not None:
            payload["think"] = think
        elif "gpt-oss" in model_lower:
            payload["think"] = "low"
        return payload

    async def chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 512,
        stream: bool = True,
        think: Any = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        session = await self.get_session()
        if not messages:
            messages = [{"role": "user", "content": "Hallo"}]
        payload = self._build_chat_payload(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream,
            think=think,
        )
        async with session.post(f"{self.base_url}/api/chat", json=payload) as r:
            if r.status != 200:
                error_text = await r.text()
                print(f"DEBUG: Ollama API returned error {r.status}: {error_text}")
                yield {"error": f"API Fehler {r.status}: {error_text}"}
                return
            if stream:
                async for line in r.content:
                    chunk = line.decode("utf-8").strip()
                    if not chunk:
                        continue
                    try:
                        data = json.loads(chunk)
                        yield data
                    except json.JSONDecodeError as exc:
                        print(f"DEBUG: JSON decode failed for chunk: {chunk!r} -> {exc}")
                        continue
            else:
                data = await r.json()
                yield data
