from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from scripts.data.manifest import build_manifest
from scripts.data.registry import DatasetManager


def validate_dataset(name: str, manager: DatasetManager | None = None) -> dict[str, Any]:
    manager = manager or DatasetManager()
    ensure_result = manager.ensure(name)
    spec = manager.registry.get(name)

    report: dict[str, Any] = {
        "name": name,
        "display_name": spec.display_name,
        "required": spec.required,
        "status": ensure_result["status"],
        "message": ensure_result["message"],
        "manifest": None,
        "errors": [],
        "warnings": [],
    }

    if ensure_result["status"] != "reused":
        return report

    path = Path(ensure_result["artifact_path"])
    report["manifest"] = build_manifest(path)

    if spec.acquisition == "local_fixture" and path.suffix == ".json":
        report["errors"].extend(_validate_furniture_fixture(path))

    report["status"] = "invalid" if report["errors"] else "ok"
    report["message"] = (
        "Dataset artifact validated."
        if report["status"] == "ok"
        else "Dataset artifact is invalid."
    )
    return report


def validate_registry(manager: DatasetManager | None = None) -> list[dict[str, Any]]:
    manager = manager or DatasetManager()
    return [validate_dataset(spec.name, manager=manager) for spec in manager.registry.list()]


def _validate_furniture_fixture(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        records = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"invalid JSON: {exc.msg}"]

    if not isinstance(records, list):
        return ["fixture must be a JSON array"]

    seen_ids: set[str] = set()
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            errors.append(f"record {index} must be an object")
            continue

        item_id = record.get("id")
        if not isinstance(item_id, str) or not item_id:
            errors.append(f"record {index} has missing furniture id")
        elif item_id in seen_ids:
            errors.append(f"duplicate furniture id: {item_id}")
        else:
            seen_ids.add(item_id)

        dimensions = record.get("dimensions")
        if dimensions is not None and (
            not isinstance(dimensions, list)
            or len(dimensions) != 3
            or any(not isinstance(value, (int, float)) or value <= 0 for value in dimensions)
        ):
            errors.append(f"record {index} has invalid dimensions")

    return errors
