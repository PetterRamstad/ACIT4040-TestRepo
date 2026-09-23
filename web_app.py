import json
import os
import subprocess
import sys
import tempfile
import shutil
import threading
import uuid
from threading import Lock
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, render_template, request, send_from_directory

from main import build_profile
from main import load_config, load_json, make_variants, prompt_for
from preference_agent import AgentError, analyze_rated_images
from swarm_client import SwarmClient, SwarmError


ROOT = Path(os.getenv("PROJECT_ROOT", Path(__file__).resolve().parent)).resolve()
SESSION_PATH = ROOT / "data" / "dataset_session.json"
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
VALID_CHOICES = {"like", "dislike", "skip", None}
app = Flask(__name__)
round_lock = Lock()
agent_lock = Lock()
session_reset_lock = Lock()
pipeline_lock = Lock()
pipeline_jobs: dict[str, dict[str, Any]] = {}
DEFAULT_SESSION_PATH = ROOT / "data" / "session.json"


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


def rated_images(session: dict[str, Any]) -> list[dict[str, Any]]:
    items = []
    for round_data in session.get("rounds", []):
        for candidate in round_data.get("candidates", []):
            if not candidate.get("choice") and candidate.get("rating") is None:
                continue
            image_path = image_for_candidate(round_data, candidate["candidate_id"])
            if image_path is None:
                continue
            items.append({
                **candidate,
                "local_file": str(image_path.relative_to(ROOT)),
            })
    return items


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
    if rating is not None and (not isinstance(rating, int) or not 1 <= rating <= 5):
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


@app.post("/api/reset-choices")
def reset_choices():
    try:
        session = load_session()
        round_data = latest_round(session)
    except (FileNotFoundError, KeyError, ValueError) as exc:
        return jsonify({"error": str(exc)}), 404

    for candidate in round_data.get("candidates", []):
        candidate["choice"] = None
        candidate["rating"] = None
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


@app.post("/api/new-session")
def new_session():
    if not session_reset_lock.acquire(blocking=False):
        return jsonify({"error": "A new session is already being prepared."}), 409

    try:
        session = json.loads(DEFAULT_SESSION_PATH.read_text(encoding="utf-8"))
        session["rounds"] = []
        save_session(session)
        for round_path in ROOT.joinpath("outputs").glob("dataset_round_*"):
            if round_path.is_dir():
                shutil.rmtree(round_path)
        result = subprocess.run(
            [sys.executable, "main.py", "dataset", "--images", "5"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=300,
            check=False,
        )
        if result.returncode != 0:
            details = (result.stderr or result.stdout).strip()
            return jsonify({"error": details or "The new session failed."}), 500
        return jsonify(review_payload())
    except (FileNotFoundError, KeyError, ValueError) as exc:
        return jsonify({"error": str(exc)}), 500
    except subprocess.TimeoutExpired:
        return jsonify({"error": "The new session took too long to complete."}), 504
    finally:
        session_reset_lock.release()


def run_agent_pipeline(job_id: str) -> None:
    try:
        session = load_session()
        profile = build_profile(session)
        items = rated_images(session)
        if not items:
            raise ValueError("Rate at least one image before starting agent analysis.")

        def update_progress(index: int, total: int, record: dict[str, Any]) -> None:
            pipeline_jobs[job_id].update({
                "status": "analyzing",
                "current": index,
                "total": total,
                "message": f"Analyzing rated image {index} of {total}: {record['local_file']}",
            })

        analysis = analyze_rated_images(items, profile, ROOT, update_progress)
        pipeline_jobs[job_id].update({"status": "generating", "message": "Generating five images with SwarmUI..."})
        settings = load_config(ROOT / "config.json")
        client = SwarmClient(settings.swarm_url, api_key=settings.swarm_api_key)
        client.new_session()
        models = client.models()
        if settings.model and settings.model not in models:
            raise SwarmError(
                f"Invalid SwarmUI model '{settings.model}'. Valid models: "
                + ", ".join(models)
            )
        model = settings.model or (models[0] if models else "")
        if not model:
            raise SwarmError("SwarmUI did not report an available image model.")

        variants = make_variants(profile)
        round_no = 1
        while (ROOT / "outputs" / f"agent_round_{round_no:02d}").exists():
            round_no += 1
        round_dir = ROOT / "outputs" / f"agent_round_{round_no:02d}"
        round_dir.mkdir(parents=True, exist_ok=True)
        generated = []
        for index, variant in enumerate(variants[:5], start=1):
            prompt = prompt_for(session["room"], profile, variant)
            items = client.generate(
                prompt=prompt, model=model, images=1, width=settings.width,
                height=settings.height, steps=settings.steps, cfgscale=settings.cfgscale,
                negativeprompt=settings.negativeprompt, seed=settings.seed,
                extra_metadata={"agent_pipeline": "true", "candidate": variant["candidate_id"]},
            )
            files = []
            for file_index, item in enumerate(items, start=1):
                if item.get("path", "").startswith("View/"):
                    destination = round_dir / f"{variant['candidate_id']}_{file_index}.png"
                    client.download_view(item["path"], destination)
                    files.append(str(destination.relative_to(ROOT)))
            generated.append({**variant, "prompt": prompt, "local_files": files})
            pipeline_jobs[job_id].update({"current": index, "total": 5, "message": f"Generated image {index} of 5"})

        (round_dir / "agent_analysis.json").write_text(json.dumps(analysis, indent=2) + "\n", encoding="utf-8")
        (round_dir / "generation_results.json").write_text(json.dumps({"mode": "agent_swarm", "results": generated}, indent=2) + "\n", encoding="utf-8")
        (round_dir / "profile.json").write_text(json.dumps(profile, indent=2) + "\n", encoding="utf-8")
        pipeline_jobs[job_id].update({"status": "complete", "round": round_no, "output_dir": str(round_dir.relative_to(ROOT))})
        session.setdefault("rounds", []).append({
            "round": round_no,
            "mode": "agent_swarm",
            "output_dir": str(round_dir.relative_to(ROOT)),
            "candidates": [
                {"candidate_id": item["candidate_id"], "choice": None}
                for item in generated
            ],
        })
        save_session(session)
        pipeline_jobs[job_id].update({"status": "complete", "round": round_no, "output_dir": str(round_dir.relative_to(ROOT))})
    except (AgentError, FileNotFoundError, KeyError, ValueError, SwarmError) as exc:
        pipeline_jobs[job_id].update({"status": "error", "message": str(exc)})
    finally:
        pipeline_lock.release()


@app.post("/api/agent-pipeline")
def start_agent_pipeline():
    if not pipeline_lock.acquire(blocking=False):
        return jsonify({"error": "The agent pipeline is already running."}), 409
    job_id = uuid.uuid4().hex
    pipeline_jobs[job_id] = {"status": "starting", "current": 0, "total": 0, "message": "Starting agent pipeline..."}
    worker = threading.Thread(target=run_agent_pipeline, args=(job_id,), daemon=True)
    worker.start()
    return jsonify({"job_id": job_id}), 202


@app.get("/api/agent-pipeline/<job_id>")
def agent_pipeline_status(job_id: str):
    job = pipeline_jobs.get(job_id)
    if not job:
        return jsonify({"error": "Unknown agent pipeline job."}), 404
    return jsonify(job)


@app.get("/generated")
def generated_page():
    return render_template("generated.html")


@app.get("/api/generated")
def generated_results():
    session = load_session()
    agent_rounds = [
        item for item in session.get("rounds", [])
        if item.get("mode") == "agent_swarm"
    ]
    if not agent_rounds:
        return jsonify({"error": "No agent-generated SwarmUI round exists yet."}), 404
    round_data = max(agent_rounds, key=lambda item: item.get("round", 0))
    output_dir = ROOT / round_data["output_dir"]
    results_path = output_dir / "generation_results.json"
    analysis_path = output_dir / "agent_analysis.json"
    results = json.loads(results_path.read_text(encoding="utf-8"))
    files = []
    for result in results.get("results", []):
        files.extend(
            {
                "candidate_id": result["candidate_id"],
                "image_url": "/media/" + file.replace("\\", "/"),
            }
            for file in result.get("local_files", [])
            if (ROOT / file).is_file()
        )
    analysis = json.loads(analysis_path.read_text(encoding="utf-8")) if analysis_path.exists() else None
    return jsonify({"round": round_data.get("round"), "output_dir": round_data["output_dir"], "images": files, "analysis": analysis})


@app.get("/media/<path:filename>")
def media(filename: str):
    requested = (ROOT / filename).resolve()
    if ROOT not in requested.parents or not requested.is_file():
        return jsonify({"error": "Image not found"}), 404
    return send_from_directory(ROOT, requested.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=False)