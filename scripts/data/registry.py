from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REGISTRY_PATH = ROOT / "data" / "manifests" / "dataset_registry.json"


@dataclass(frozen=True)
class DatasetSpec:
    name: str
    display_name: str
    purpose: str
    required: bool
    profile: str
    acquisition: str
    status: str
    license_status: str
    source: str
    version: str
    preprocessing_version: str
    path: str | None = None
    source_url: str | None = None
    notes: tuple[str, ...] = ()
    open_questions: tuple[str, ...] = ()

    @property
    def can_download_automatically(self) -> bool:
        return self.acquisition in {"local_fixture", "safe_public_download"}

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> DatasetSpec:
        return cls(
            name=data["name"],
            display_name=data.get("display_name", data["name"]),
            purpose=data["purpose"],
            required=bool(data.get("required", False)),
            profile=data.get("profile", "dev"),
            acquisition=data["acquisition"],
            status=data["status"],
            license_status=data["license_status"],
            source=data["source"],
            version=data.get("version", "unknown"),
            preprocessing_version=data.get("preprocessing_version", "v1"),
            path=data.get("path"),
            source_url=data.get("source_url"),
            notes=tuple(data.get("notes", [])),
            open_questions=tuple(data.get("open_questions", [])),
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "display_name": self.display_name,
            "purpose": self.purpose,
            "required": self.required,
            "profile": self.profile,
            "acquisition": self.acquisition,
            "status": self.status,
            "license_status": self.license_status,
            "source": self.source,
            "version": self.version,
            "preprocessing_version": self.preprocessing_version,
            "path": self.path,
            "source_url": self.source_url,
            "can_download_automatically": self.can_download_automatically,
            "notes": list(self.notes),
            "open_questions": list(self.open_questions),
        }


class DatasetRegistry:
    def __init__(self, specs: list[DatasetSpec]):
        self._specs = {spec.name: spec for spec in specs}

    @classmethod
    def from_default(cls) -> DatasetRegistry:
        return cls.from_path(DEFAULT_REGISTRY_PATH)

    @classmethod
    def from_path(cls, path: Path) -> DatasetRegistry:
        data = json.loads(path.read_text(encoding="utf-8"))
        return cls([DatasetSpec.from_mapping(item) for item in data["datasets"]])

    def get(self, name: str) -> DatasetSpec:
        try:
            return self._specs[name]
        except KeyError as exc:
            raise KeyError(f"Unknown dataset: {name}") from exc

    def list(self) -> list[DatasetSpec]:
        return sorted(self._specs.values(), key=lambda spec: spec.name)


class DatasetManager:
    def __init__(self, registry: DatasetRegistry | None = None, root: Path = ROOT):
        self.registry = registry or DatasetRegistry.from_default()
        self.root = root

    def status(self, name: str) -> dict[str, Any]:
        spec = self.registry.get(name)
        payload = spec.as_dict()

        if spec.path:
            artifact_path = self.root / spec.path
            payload["artifact_path"] = str(artifact_path)
            payload["artifact_exists"] = artifact_path.exists()
        else:
            payload["artifact_path"] = None
            payload["artifact_exists"] = False

        return payload

    def ensure(self, name: str) -> dict[str, Any]:
        spec = self.registry.get(name)
        status = self.status(name)

        if spec.acquisition == "local_fixture":
            if status["artifact_exists"]:
                return {
                    **status,
                    "status": "reused",
                    "message": "Compatible local fixture artifact is present.",
                }
            return {
                **status,
                "status": "missing",
                "message": "Local fixture artifact is missing.",
            }

        if spec.acquisition == "confirm_source_url":
            return {
                **status,
                "status": "needs_user_confirmation",
                "message": "The exact source URL and license must be confirmed before automation.",
            }

        if spec.acquisition in {"manual_archive", "manual_registration", "explicit_download"}:
            return {
                **status,
                "status": "human_required",
                "message": (
                    "Manual license/access approval is required before this dataset can be "
                    "downloaded, unpacked, or indexed."
                ),
            }

        return {
            **status,
            "status": spec.status,
            "message": "No automated action is configured for this dataset.",
        }


def main() -> int:
    parser = argparse.ArgumentParser(description="Dataset registry and safe acquisition status")
    parser.add_argument("command", choices=("list", "status", "ensure"), nargs="?", default="list")
    parser.add_argument("name", nargs="?")
    args = parser.parse_args()

    manager = DatasetManager()
    if args.command == "list":
        print(json.dumps([spec.as_dict() for spec in manager.registry.list()], indent=2))
        return 0

    if not args.name:
        parser.error("status/ensure require a dataset name")

    result = manager.status(args.name) if args.command == "status" else manager.ensure(args.name)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
