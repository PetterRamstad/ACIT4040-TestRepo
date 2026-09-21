import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from dotenv import load_dotenv


def _bool_value(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).strip().lower() in {"1", "true", "yes", "y", "on"}


def _int_value(value: Any, fallback: int) -> int:
    if value in (None, ""):
        return fallback
    return int(value)


def _float_value(value: Any, fallback: float) -> float:
    if value in (None, ""):
        return fallback
    return float(value)


@dataclass(frozen=True)
class Settings:
    swarm_url: str
    swarm_api_key: str
    mock_swarm: bool
    model: str
    images_per_round: int
    width: int
    height: int
    steps: int
    cfgscale: float
    negativeprompt: str
    seed: int

    @classmethod
    def from_json(cls, config_path: Path, config: dict[str, Any]) -> "Settings":
        load_dotenv(config_path.parent / ".env")

        return cls(
            swarm_url=str(os.getenv("SWARM_URL", config.get("swarm_url", "http://localhost:7801"))),
            swarm_api_key=str(os.getenv("SWARM_API_KEY", "")),
            mock_swarm=_bool_value(os.getenv("MOCK_SWARM", config.get("mock_swarm", False))),
            model=str(os.getenv("SWARM_MODEL", config.get("model", ""))),
            images_per_round=_int_value(
                os.getenv("IMAGES_PER_ROUND", config.get("images_per_round")),
                5,
            ),
            width=_int_value(os.getenv("IMAGE_WIDTH", config.get("width")), 1024),
            height=_int_value(os.getenv("IMAGE_HEIGHT", config.get("height")), 1024),
            steps=_int_value(os.getenv("GENERATION_STEPS", config.get("steps")), 24),
            cfgscale=_float_value(os.getenv("CFG_SCALE", config.get("cfgscale")), 6.5),
            negativeprompt=str(os.getenv("NEGATIVE_PROMPT", config.get("negativeprompt", ""))),
            seed=_int_value(os.getenv("GENERATION_SEED", config.get("seed")), -1),
        )

    def safe_dict(self) -> dict[str, Any]:
        return {
            "swarm_url": self.swarm_url,
            "swarm_api_key": "set" if self.swarm_api_key else "",
            "mock_swarm": self.mock_swarm,
            "model": self.model,
            "images_per_round": self.images_per_round,
            "width": self.width,
            "height": self.height,
            "steps": self.steps,
            "cfgscale": self.cfgscale,
            "negativeprompt": self.negativeprompt,
            "seed": self.seed,
        }
