import json
import hashlib
import struct
import zlib
from pathlib import Path
from typing import Any

import requests


class SwarmError(RuntimeError):
    pass


class SwarmClient:
    is_mock = False

    def __init__(self, base_url: str, timeout: int = 600, api_key: str = ""):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.api_key = api_key
        self.session_id = ""
        self.http = requests.Session()
        self.http.headers.update({"Content-Type": "application/json"})
        if api_key:
            self.http.headers.update({"Authorization": f"Bearer {api_key}"})

    def post(self, route: str, payload: dict[str, Any]) -> dict[str, Any]:
        url = f"{self.base_url}/API/{route}"
        try:
            response = self.http.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()
        except requests.Timeout as exc:
            raise SwarmError(f"SwarmUI request timed out: {url}") from exc
        except requests.RequestException as exc:
            raise SwarmError(
                f"Could not reach SwarmUI at {self.base_url}. "
                f"Start SwarmUI first. Details: {exc}"
            ) from exc

        try:
            data = response.json()
        except ValueError as exc:
            raise SwarmError(
                f"SwarmUI returned invalid JSON from {route}: {response.text[:500]}"
            ) from exc

        if isinstance(data, dict) and data.get("error"):
            raise SwarmError(str(data["error"]))
        return data

    def new_session(self) -> str:
        data = self.post("GetNewSession", {})
        session_id = data.get("session_id")
        if not session_id:
            raise SwarmError(f"SwarmUI did not return a session_id: {data}")
        self.session_id = session_id
        return session_id

    def status(self) -> dict[str, Any]:
        if not self.session_id:
            self.new_session()
        return self.post("GetCurrentStatus", {"session_id": self.session_id})

    def params(self) -> dict[str, Any]:
        if not self.session_id:
            self.new_session()
        return self.post("ListT2IParams", {"session_id": self.session_id})

    def models(self) -> list[str]:
        data = self.params()
        values: list[str] = []
        for item in data.get("list", []):
            if item.get("id") == "model":
                raw = item.get("values") or []
                values.extend(str(v) for v in raw)
        # Some versions may expose models separately.
        for model in data.get("models", []) or []:
            if isinstance(model, str):
                values.append(model)
            elif isinstance(model, dict) and model.get("name"):
                values.append(str(model["name"]))
        return list(dict.fromkeys(values))

    def generate(
        self,
        prompt: str,
        model: str,
        images: int = 1,
        width: int = 1024,
        height: int = 1024,
        steps: int = 24,
        cfgscale: float = 6.5,
        negativeprompt: str = "",
        seed: int = -1,
        extra_metadata: dict[str, str] | None = None,
    ) -> list[dict[str, Any]]:
        if not self.session_id:
            self.new_session()

        payload: dict[str, Any] = {
            "session_id": self.session_id,
            "images": images,
            "prompt": prompt,
            "negativeprompt": negativeprompt,
            "model": model,
            "width": width,
            "height": height,
            "steps": steps,
            "cfgscale": cfgscale,
            "seed": seed,
        }
        if extra_metadata:
            payload["extra_metadata"] = json.dumps(extra_metadata)

        data = self.post("GenerateText2Image", payload)
        results = data.get("images", [])
        normalized = []
        for item in results:
            if isinstance(item, str):
                normalized.append({"path": item})
            elif isinstance(item, dict):
                normalized.append(item)
        return normalized

    def download_view(self, view_path: str, destination: Path) -> Path:
        # SwarmUI normally returns paths beginning with View/.
        url = f"{self.base_url}/{view_path.lstrip('/')}"
        destination.parent.mkdir(parents=True, exist_ok=True)
        try:
            response = self.http.get(url, timeout=self.timeout)
            response.raise_for_status()
            destination.write_bytes(response.content)
        except requests.RequestException as exc:
            raise SwarmError(f"Could not download generated image {url}: {exc}") from exc
        return destination


class MockSwarmClient:
    is_mock = True

    def __init__(self, base_url: str = "mock://swarmui", timeout: int = 600):
        self.base_url = base_url.rstrip("/") or "mock://swarmui"
        self.timeout = timeout
        self.session_id = ""
        self._images: dict[str, dict[str, Any]] = {}

    def new_session(self) -> str:
        self.session_id = "mock-session"
        return self.session_id

    def status(self) -> dict[str, Any]:
        if not self.session_id:
            self.new_session()
        return {
            "backend_status": {
                "mode": "mock",
                "message": "Offline mock client is active. No SwarmUI requests are sent.",
            }
        }

    def params(self) -> dict[str, Any]:
        if not self.session_id:
            self.new_session()
        return {
            "list": [
                {
                    "id": "model",
                    "values": ["mock-offline-model"],
                }
            ]
        }

    def models(self) -> list[str]:
        return ["mock-offline-model"]

    def generate(
        self,
        prompt: str,
        model: str,
        images: int = 1,
        width: int = 1024,
        height: int = 1024,
        steps: int = 24,
        cfgscale: float = 6.5,
        negativeprompt: str = "",
        seed: int = -1,
        extra_metadata: dict[str, str] | None = None,
    ) -> list[dict[str, Any]]:
        if not self.session_id:
            self.new_session()

        results = []
        for index in range(1, images + 1):
            key = json.dumps(
                {
                    "prompt": prompt,
                    "model": model or "mock-offline-model",
                    "index": index,
                    "width": width,
                    "height": height,
                    "steps": steps,
                    "cfgscale": cfgscale,
                    "negativeprompt": negativeprompt,
                    "seed": seed,
                    "extra_metadata": extra_metadata or {},
                },
                sort_keys=True,
            )
            digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
            view_path = f"View/mock/{digest[:16]}.png"
            self._images[view_path] = {
                "digest": digest,
                "prompt": prompt,
                "model": model or "mock-offline-model",
                "width": width,
                "height": height,
                "seed": seed,
                "extra_metadata": extra_metadata or {},
            }
            results.append({
                "path": view_path,
                "mock": True,
                "model": model or "mock-offline-model",
                "seed": seed,
            })
        return results

    def download_view(self, view_path: str, destination: Path) -> Path:
        metadata = self._images.get(view_path, {"digest": view_path})
        width = int(metadata.get("width", 512))
        height = int(metadata.get("height", 512))
        _write_mock_png(destination, width, height, str(metadata.get("digest", view_path)))
        return destination


def _write_mock_png(destination: Path, requested_width: int, requested_height: int, key: str) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    width = max(64, min(requested_width, 512))
    height = max(64, min(requested_height, 512))
    digest = hashlib.sha256(key.encode("utf-8")).digest()
    base = digest[:3]
    accent = digest[3:6]

    rows = []
    for y in range(height):
        row = bytearray()
        for x in range(width):
            checker = ((x // 32) + (y // 32)) % 2
            source = accent if checker else base
            fade = 0.72 + (0.28 * y / max(height - 1, 1))
            row.extend(min(255, int(channel * fade) + 32) for channel in source)
        rows.append(b"\x00" + bytes(row))

    raw = b"".join(rows)
    png = (
        b"\x89PNG\r\n\x1a\n"
        + _png_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + _png_chunk(b"tEXt", b"Software\x00Apartment project offline SwarmUI mock")
        + _png_chunk(b"IDAT", zlib.compress(raw, level=9))
        + _png_chunk(b"IEND", b"")
    )
    destination.write_bytes(png)


def _png_chunk(chunk_type: bytes, data: bytes) -> bytes:
    checksum = zlib.crc32(chunk_type + data) & 0xFFFFFFFF
    return struct.pack(">I", len(data)) + chunk_type + data + struct.pack(">I", checksum)
