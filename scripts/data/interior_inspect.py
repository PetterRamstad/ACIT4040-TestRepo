from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

EXPECTED_ROOM_FOLDERS = {
    "bathroom",
    "bedroom",
    "childrens_room",
    "dining_room",
    "hallway_entrance",
    "home_office",
    "kitchen",
    "living_room",
    "mixed",
    "other_interior",
}

FILENAME_PATTERN = re.compile(
    r"^(?P<split>train|test)-(?P<style>[A-Za-z0-9_]+)-(?P<class_token>[A-Za-z0-9_]+)_(?P<index>\d+)\.[^.]+$"
)


def inspect_interior_dataset(root: Path) -> dict[str, Any]:
    root = root.resolve()
    files = sorted(path for path in root.rglob("*") if path.is_file())
    room_counts: dict[str, dict[str, Any]] = {}
    extensions: Counter[str] = Counter()
    splits: Counter[str] = Counter()
    styles: Counter[str] = Counter()
    non_matching: list[str] = []
    hash_to_files: dict[str, list[str]] = defaultdict(list)
    image_dimensions: dict[str, dict[str, int]] = {}
    corrupt_files: list[str] = []

    for file_path in files:
        relative = file_path.relative_to(root).as_posix()
        room = relative.split("/", 1)[0]
        room_counts.setdefault(room, {"file_count": 0})
        room_counts[room]["file_count"] += 1
        extensions[file_path.suffix.lower()] += 1

        digest = hashlib.sha256(file_path.read_bytes()).hexdigest()
        hash_to_files[digest].append(relative)

        match = FILENAME_PATTERN.match(file_path.name)
        if match:
            splits[match.group("split")] += 1
            styles[match.group("style")] += 1
        else:
            non_matching.append(relative)

        if file_path.suffix.lower() in {".jpg", ".jpeg", ".png"}:
            dimensions = _probe_image_dimensions(file_path)
            if dimensions is None:
                corrupt_files.append(relative)
            else:
                image_dimensions[relative] = dimensions

    duplicate_hashes = [
        {"sha256": digest, "files": sorted(paths)}
        for digest, paths in sorted(hash_to_files.items())
        if len(paths) > 1
    ]

    observed_rooms = set(room_counts)
    return {
        "root": str(root),
        "total_files": len(files),
        "rooms": dict(sorted(room_counts.items())),
        "missing_expected_rooms": sorted(EXPECTED_ROOM_FOLDERS - observed_rooms),
        "unexpected_rooms": sorted(observed_rooms - EXPECTED_ROOM_FOLDERS),
        "extensions": dict(sorted(extensions.items())),
        "duplicate_hashes": duplicate_hashes,
        "image_dimensions": dict(sorted(image_dimensions.items())),
        "corrupt_files": sorted(corrupt_files),
        "filename_metadata": {
            "pattern": FILENAME_PATTERN.pattern,
            "matched_files": sum(splits.values()),
            "non_matching_files": sorted(non_matching),
            "splits": dict(sorted(splits.items())),
            "styles": dict(sorted(styles.items())),
        },
    }


def _probe_image_dimensions(path: Path) -> dict[str, int] | None:
    data = path.read_bytes()
    if path.suffix.lower() == ".png":
        return _probe_png_dimensions(data)
    if path.suffix.lower() in {".jpg", ".jpeg"}:
        return _probe_jpeg_dimensions(data)
    return None


def _probe_png_dimensions(data: bytes) -> dict[str, int] | None:
    if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        return None
    return {
        "width": int.from_bytes(data[16:20], "big"),
        "height": int.from_bytes(data[20:24], "big"),
    }


def _probe_jpeg_dimensions(data: bytes) -> dict[str, int] | None:
    if len(data) < 4 or data[:2] != b"\xff\xd8":
        return None

    index = 2
    while index + 9 < len(data):
        if data[index] != 0xFF:
            return None
        marker = data[index + 1]
        index += 2
        if marker in {0xD8, 0xD9}:
            continue
        if index + 2 > len(data):
            return None
        segment_length = int.from_bytes(data[index : index + 2], "big")
        if segment_length < 2 or index + segment_length > len(data):
            return None
        if marker in {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}:
            return {
                "height": int.from_bytes(data[index + 3 : index + 5], "big"),
                "width": int.from_bytes(data[index + 5 : index + 7], "big"),
            }
        index += segment_length
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect an interior room image dataset")
    parser.add_argument("path", type=Path)
    args = parser.parse_args()

    report = inspect_interior_dataset(args.path)
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
