from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / ".pipeline" / "state.json"
LOG_PATH = ROOT / ".pipeline" / "pipeline.log"


def log(message: str) -> None:
    LOG_PATH.parent.mkdir(exist_ok=True)
    line = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}"
    print(line)
    with LOG_PATH.open("a", encoding="utf-8") as stream:
        stream.write(line + "\n")


def load_state() -> dict[str, str]:
    if not STATE_PATH.exists():
        return {}
    return json.loads(STATE_PATH.read_text(encoding="utf-8"))


def save_state(state: dict[str, str]) -> None:
    STATE_PATH.parent.mkdir(exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def run(command: list[str], *, dry_run: bool = False) -> None:
    if sys.platform == "win32" and command[0] == "npm":
        command = ["npm.cmd", *command[1:]]
    log("$ " + " ".join(command))
    if dry_run:
        return
    subprocess.run(command, cwd=ROOT, check=True)


def python_script(path: str, *args: str, dry_run: bool = False) -> None:
    run([sys.executable, path, *args], dry_run=dry_run)


def environment(profile: str, *, dry_run: bool) -> None:
    log("Environment and dependency checks")
    for executable in ("git", "node", "npm"):
        if shutil.which(executable) is None:
            raise RuntimeError(f"Required executable not found: {executable}")
        log(f"{executable}: available")
    if profile == "production":
        python_script("scripts/env/check.py", dry_run=dry_run)


def data(*, dry_run: bool) -> None:
    python_script("scripts/data/registry.py", "ensure", "furniture-fixture", dry_run=dry_run)
    python_script("scripts/data/verify.py", dry_run=dry_run)


def test(*, dry_run: bool) -> None:
    python_script("-m", "pytest", "-q", dry_run=dry_run)
    python_script("-m", "ruff", "check", ".", dry_run=dry_run)
    python_script(
        "-m",
        "mypy",
        "apps/api",
        "packages",
        "--ignore-missing-imports",
        dry_run=dry_run,
    )
    run(["npm", "--prefix", "apps/frontend", "run", "typecheck"], dry_run=dry_run)
    run(["npm", "--prefix", "apps/frontend", "test", "--", "--run"], dry_run=dry_run)
    run(["npm", "--prefix", "apps/frontend", "run", "build"], dry_run=dry_run)


def api_health(*, dry_run: bool) -> None:
    if dry_run:
        log("Would verify http://127.0.0.1:8000/health and /ready")
        return
    for endpoint in ("health", "ready"):
        try:
            with urlopen(f"http://127.0.0.1:8000/{endpoint}", timeout=5) as response:
                if response.status != 200:
                    raise RuntimeError(f"/{endpoint} returned HTTP {response.status}")
                log(f"/{endpoint}: HTTP {response.status}")
        except URLError as error:
            raise RuntimeError(
                "API is not running. Start it with "
                "'python -m uvicorn apps.api.app.main:app --reload'."
            ) from error


def api_health_with_local_server(*, dry_run: bool) -> None:
    if dry_run:
        api_health(dry_run=True)
        return
    try:
        api_health(dry_run=False)
        return
    except RuntimeError:
        log("API is not running; starting a temporary local server for verification.")

    server = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "apps.api.app.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8000",
        ],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        for _ in range(20):
            try:
                api_health(dry_run=False)
                return
            except RuntimeError:
                time.sleep(0.25)
        raise RuntimeError("Temporary API server did not become healthy.")
    finally:
        server.terminate()
        server.wait(timeout=10)


def production_check(*, dry_run: bool) -> None:
    api_health_with_local_server(dry_run=dry_run)
    test(dry_run=dry_run)


def clean() -> None:
    if STATE_PATH.exists():
        STATE_PATH.unlink()
    if LOG_PATH.exists():
        LOG_PATH.unlink()
    log("Removed pipeline state and logs only; data and models were preserved.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="ACIT4040 safe, resumable local pipeline")
    parser.add_argument(
        "command",
        nargs="?",
        default="full",
        choices=(
            "setup",
            "data",
            "models",
            "embeddings",
            "index",
            "test",
            "dev",
            "production-check",
            "deploy",
            "full",
            "clean",
        ),
    )
    parser.add_argument("--profile", choices=("dev", "research", "production"), default="dev")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.command == "clean":
        clean()
        return 0

    state = load_state()
    steps = {
        "setup": lambda: environment(args.profile, dry_run=args.dry_run),
        "data": lambda: data(dry_run=args.dry_run),
        "models": lambda: log("Models: fixture profile; no heavyweight download requested."),
        "embeddings": lambda: log("Embeddings: deterministic fixture provider; reused."),
        "index": lambda: log("Index: deterministic fixture index; reused."),
        "test": lambda: test(dry_run=args.dry_run),
        "production-check": lambda: production_check(dry_run=args.dry_run),
        "dev": lambda: log("Start API separately with the documented uvicorn command."),
        "deploy": lambda: log("Deployment is intentionally not automated in the local profile."),
    }
    selected = (
        ["setup", "data", "models", "embeddings", "index", "test", "production-check"]
        if args.command == "full"
        else [args.command]
    )
    for step in selected:
        if args.resume and not args.force and state.get(step) == "passed":
            log(f"{step}: reused from pipeline state")
            continue
        log(f"== {step} ==")
        steps[step]()
        if not args.dry_run:
            state[step] = "passed"
            save_state(state)
    log("Pipeline completed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
