from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any


def build_manifest(path: Path) -> dict[str, Any]:
    if path.is_file():
        file_digest = hashlib.sha256(path.read_bytes()).hexdigest()
        return {
            "path": str(path),
            "file_count": 1,
            "byte_size": path.stat().st_size,
            "sha256": file_digest,
        }

    if path.is_dir():
        tree_digest = hashlib.sha256()
        file_count = 0
        byte_size = 0
        for file_path in sorted(item for item in path.rglob("*") if item.is_file()):
            relative = file_path.relative_to(path).as_posix().encode("utf-8")
            content = file_path.read_bytes()
            tree_digest.update(relative)
            tree_digest.update(content)
            file_count += 1
            byte_size += len(content)
        return {
            "path": str(path),
            "file_count": file_count,
            "byte_size": byte_size,
            "sha256": tree_digest.hexdigest(),
        }

    return {
        "path": str(path),
        "file_count": 0,
        "byte_size": 0,
        "sha256": None,
    }
