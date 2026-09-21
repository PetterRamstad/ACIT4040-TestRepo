import json
import os
import subprocess
import sys
import tempfile
from threading import Lock
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, render_template, request, send_from_directory


ROOT = Path(os.getenv("PROJECT_ROOT", Path(__file__).resolve().parent)).resolve()
SESSION_PATH = ROOT / "data" / "dataset_session.json"
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
VALID_CHOICES = {"like", "dislike", "skip", None}
app = Flask(__name__)
round_lock = Lock()


def load_session() -> dict[str, Any]:
    if not SESSION_PATH.exists():
        raise FileNotFoundError(
            "data/dataset_session.json is missing. Run python3 main.py first."
        )
    return json.loads(SESSION_PATH.read_text(encoding="utf-8"))


def save_session(session: dict[str, Any]) -> None:
    SESSION_PATH.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=SESSION_PATH.parent, delete=False
    ) as handle:
        json.dump(session, handle, indent=2)
        handle.write("\n")
        temporary_path = Path(handle.name)
    temporary_path.replace(SESSION_PATH)


def latest_round(session: dict[str, Any]) -> dict[str, Any]:
    rounds = session.get("rounds", [])
    if not rounds:
        raise ValueError("No dataset round exists yet. Run python3 main.py first.")
    return max(rounds, key=lambda item: item.get("round", 0))


def image_for_candidate(round_data: dict[str, Any], candidate_id: str) -> Path | None:
    output_dir = ROOT / round_data["output_dir"]
    for path in output_dir.glob(f"{candidate_id}.*"):
        if path.suffix.lower() in IMAGE_EXTENSIONS and path.is_file():
            return path
    return None


def review_payload() -> dict[str, Any]:
    session = load_session()
    round_data = latest_round(session)
    candidates = []
    for candidate in round_data.get("candidates", []):
        image_path = image_for_candidate(round_data, candidate["candidate_id"])
        if image_path is None:
            continue
        candidates.append({
            **candidate,
            "image_url": "/media/" + image_path.relative_to(ROOT).as_posix(),
        })
    counts = {"like": 0, "dislike": 0, "skip": 0, "unrated": 0}
    for candidate in round_data.get("candidates", []):
        choice = candidate.get("choice")
        counts[choice if choice in counts else "unrated"] += 1
    return {
        "round": round_data.get("round"),
        "mode": round_data.get("mode", "dataset_reference"),
        "output_dir": round_data.get("output_dir"),
        "candidates": candidates,
        "counts": counts,
    }


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/review")
def review():
    try:
        return jsonify(review_payload())
    except (FileNotFoundError, KeyError, ValueError) as exc:
        return jsonify({"error": str(exc)}), 404


@app.post("/api/candidates/<candidate_id>/feedback")
def feedback(candidate_id: str):
    payload = request.get_json(silent=True) or {}
    choice = payload.get("choice")
    rating = payload.get("rating")
    if choice not in VALID_CHOICES:
        return jsonify({"error": "choice must be like, dislike, skip, or null"}), 400
    if rating is not None or "rating" in payload:
        if not isinstance(rating, int) or not 1 <= rating <= 5:
            return jsonify({"error": "rating must be an integer from 1 to 5 or null"}), 400

    try:
        session = load_session()
        round_data = latest_round(session)
    except (FileNotFoundError, KeyError, ValueError) as exc:
        return jsonify({"error": str(exc)}), 404

    candidate = next(
        (item for item in round_data.get("candidates", []) if item.get("candidate_id") == candidate_id),
        None,
    )
    if candidate is None:
        return jsonify({"error": f"Unknown candidate: {candidate_id}"}), 404
    candidate["choice"] = choice
    candidate["rating"] = rating
    save_session(session)
    return jsonify(review_payload())


@app.post("/api/next-round")
def next_round():
    if not round_lock.acquire(blocking=False):
        return jsonify({"error": "A new round is already being prepared."}), 409

    try:
        result = subprocess.run(
            [sys.executable, "main.py", "dataset", "--images", "5"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=300,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return jsonify({"error": "The next round took too long to complete."}), 504
    finally:
        round_lock.release()

    if result.returncode != 0:
        details = (result.stderr or result.stdout).strip()
        return jsonify({"error": details or "The next round failed."}), 500

    try:
        return jsonify(review_payload())
    except (FileNotFoundError, KeyError, ValueError) as exc:
        return jsonify({"error": str(exc)}), 500


@app.get("/media/<path:filename>")
def media(filename: str):
    requested = (ROOT / filename).resolve()
    if ROOT not in requested.parents or not requested.is_file():
        return jsonify({"error": "Image not found"}), 404
    return send_from_directory(ROOT, requested.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=False)