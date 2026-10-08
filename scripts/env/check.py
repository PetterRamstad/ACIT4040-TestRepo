from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class VariableStatus:
    name: str
    configured: bool
    required: bool


REQUIRED_FOR_LOCAL = ("APP_ENV", "DATA_ROOT", "MODEL_CACHE_DIR")
OPTIONAL = (
    "DATABASE_URL",
    "QDRANT_URL",
    "QDRANT_API_KEY",
    "OBJECT_STORAGE_ENDPOINT",
    "AI_GATEWAY_API_KEY",
    "AUTH_SECRET",
)


def inspect_environment() -> list[VariableStatus]:
    return [
        VariableStatus(name, bool(os.getenv(name)), name in REQUIRED_FOR_LOCAL)
        for name in (*REQUIRED_FOR_LOCAL, *OPTIONAL)
    ]


def validate_environment(*, production: bool = False) -> list[str]:
    statuses = inspect_environment()
    missing = [status.name for status in statuses if status.required and not status.configured]
    if production:
        missing.extend(
            status.name
            for status in statuses
            if status.name in ("DATABASE_URL", "QDRANT_URL", "AUTH_SECRET")
            and not status.configured
        )
    return sorted(set(missing))


def main() -> int:
    missing = validate_environment(production=os.getenv("APP_ENV") == "production")
    for status in inspect_environment():
        label = "configured" if status.configured else "missing"
        requirement = "required" if status.required else "optional"
        print(f"{status.name}: {label} ({requirement})")
    if missing:
        print("Missing required variables: " + ", ".join(missing))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
