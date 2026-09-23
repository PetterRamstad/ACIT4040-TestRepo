import base64
import json
import os
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434").rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llava")


class AgentError(RuntimeError):
    pass


def _image_data(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode("ascii")


def _parse_response(content: str) -> dict[str, Any]:
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError as exc:
        raise AgentError(f"Ollama returned non-JSON analysis: {content[:300]}") from exc
    if not isinstance(parsed, dict):
        raise AgentError("Ollama returned an invalid analysis object.")
    return parsed


def analyze_image(
    image_path: Path,
    candidate: dict[str, Any],
    buyer_profile: dict[str, Any],
) -> dict[str, Any]:
    positive = ", ".join(buyer_profile.get("positive_tags", [])) or "balanced modern interiors"
    negative = ", ".join(buyer_profile.get("negative_tags", [])) or "none specified"
    prompt = f"""
You are a careful interior-design preference analyst.
Analyze the attached apartment interior image for this buyer.
Buyer positive preferences: {positive}.
Buyer negative preferences: {negative}.
Candidate style label: {candidate.get('dataset_style', 'unknown')}.

Return only valid JSON with exactly these fields:
{{
  "score": integer from 1 to 10,
  "strengths": array of short strings,
  "concerns": array of short strings,
  "summary": short string
}}
Score how well the visible image matches the buyer preferences. Do not infer
personal information or identify people. Base the analysis only on visible
interior design characteristics.
""".strip()
    payload = {
        "model": OLLAMA_MODEL,
        "stream": False,
        "format": "json",
        "messages": [{
            "role": "user",
            "content": prompt,
            "images": [_image_data(image_path)],
        }],
    }
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/chat",
            json=payload,
            timeout=180,
        )
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as exc:
        details = ""
        if exc.response is not None:
            details = exc.response.text[:300]
        raise AgentError(
            f"Ollama could not analyze the image with model '{OLLAMA_MODEL}'. "
            f"Run 'ollama run {OLLAMA_MODEL}' first. Details: {details or exc}"
        ) from exc
    except ValueError as exc:
        raise AgentError("Ollama returned invalid JSON.") from exc

    message = data.get("message", {})
    return _parse_response(message.get("content", ""))


def analyze_round(
    round_data: dict[str, Any],
    buyer_profile: dict[str, Any],
    root: Path = ROOT,
) -> dict[str, Any]:
    analyses = []
    output_dir = root / round_data["output_dir"]
    for candidate in round_data.get("candidates", []):
        image_paths = list(output_dir.glob(f"{candidate['candidate_id']}.*"))
        image_path = next((path for path in image_paths if path.is_file()), None)
        if image_path is None:
            continue
        analysis = analyze_image(image_path, candidate, buyer_profile)
        analyses.append({
            "candidate_id": candidate["candidate_id"],
            "dataset_style": candidate.get("dataset_style", "unknown"),
            "source_image": candidate.get("source_image"),
            "local_file": str(image_path.relative_to(root)),
            "analysis": analysis,
        })

    if not analyses:
        raise AgentError("No candidate images were found for the current round.")
    analyses.sort(key=lambda item: item["analysis"].get("score", 0), reverse=True)
    return {
        "round": round_data.get("round"),
        "model": OLLAMA_MODEL,
        "agent": "ollama_preference_analyst",
        "ranking": analyses,
    }


def analyze_dataset(
    records: list[dict[str, Any]],
    buyer_profile: dict[str, Any],
    dataset_root: Path,
    progress: Any = None,
) -> dict[str, Any]:
    """Analyze every valid dataset image and return a descending ranking."""
    ranking = []
    total = len(records)
    for index, record in enumerate(records, start=1):
        image_path = dataset_root / record["path"]
        analysis = analyze_image(image_path, record, buyer_profile)
        ranking.append({
            "dataset_style": record.get("style", "unknown"),
            "source_image": record["path"],
            "analysis": analysis,
        })
        if progress:
            progress(index, total, record)

    ranking.sort(key=lambda item: item["analysis"].get("score", 0), reverse=True)
    return {
        "model": OLLAMA_MODEL,
        "agent": "ollama_preference_analyst",
        "image_count": total,
        "ranking": ranking,
    }


def analyze_rated_images(
    items: list[dict[str, Any]],
    buyer_profile: dict[str, Any],
    root: Path = ROOT,
    progress: Any = None,
) -> dict[str, Any]:
    """Analyze only images the user rated or explicitly liked/disliked."""
    ranking = []
    total = len(items)
    for index, item in enumerate(items, start=1):
        image_path = root / item["local_file"]
        analysis = analyze_image(image_path, item, buyer_profile)
        ranking.append({
            "candidate_id": item["candidate_id"],
            "choice": item.get("choice"),
            "rating": item.get("rating"),
            "dataset_style": item.get("dataset_style", "unknown"),
            "source_image": item.get("source_image"),
            "local_file": item["local_file"],
            "analysis": analysis,
        })
        if progress:
            progress(index, total, item)

    ranking.sort(key=lambda item: item["analysis"].get("score", 0), reverse=True)
    return {
        "model": OLLAMA_MODEL,
        "agent": "ollama_preference_analyst",
        "image_count": total,
        "scope": "user_rated_round_images",
        "ranking": ranking,
    }
