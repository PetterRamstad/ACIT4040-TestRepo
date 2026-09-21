import argparse
import copy
import json
import shutil
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.table import Table

from settings import Settings
from swarm_client import MockSwarmClient, SwarmClient, SwarmError


ROOT = Path(__file__).resolve().parent
DEFAULT_CONFIG = ROOT / "config.json"
DEFAULT_SESSION = ROOT / "data" / "session.json"
OUTPUTS = ROOT / "outputs"
DATASET_MANIFEST = ROOT / "data" / "processed" / "interior_styles_manifest.json"
DATASET_SESSION = ROOT / "data" / "dataset_session.json"
console = Console()

# A deliberately transparent vocabulary for the MVP.
TAG_TO_TEXT = {
    "warm": "warm visual atmosphere",
    "cool": "cool visual atmosphere",
    "natural_wood": "natural oak and warm timber",
    "soft_neutral": "soft neutral palette",
    "bold_colour": "controlled bold accent colours",
    "minimal": "clean minimal styling",
    "scandinavian": "Scandinavian interior styling",
    "industrial": "industrial styling",
    "dark_metal": "dark metal details",
    "metal": "metal details",
    "comfortable": "comfortable inviting furniture",
    "warm_lighting": "warm layered lighting",
    "airy": "airy open feeling",
    "cluttered": "visually busy and cluttered styling",
    "maximalist": "maximalist styling",
    "dark": "dark moody styling",
    "cold_grey": "cold grey palette",
    "cold": "cool desaturated palette",
    "concrete": "concrete-heavy materials",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def load_config(path: Path) -> Settings:
    return Settings.from_json(path, load_json(path))


def build_profile(session: dict[str, Any]) -> dict[str, Any]:
    liked = Counter()
    disliked = Counter()
    for swipe in session.get("swipes", []):
        choice = swipe.get("choice")
        for tag in swipe.get("tags", []):
            if choice == "like":
                liked[tag] += 1
            elif choice == "dislike":
                disliked[tag] += 1

    for round_data in session.get("rounds", []):
        for candidate in round_data.get("candidates", []):
            choice = candidate.get("choice")
            style = candidate.get("dataset_style")
            if style and choice == "like":
                liked[style] += 1
            elif style and choice == "dislike":
                disliked[style] += 1

    scores = {}
    for tag in sorted(set(liked) | set(disliked)):
        scores[tag] = liked[tag] - disliked[tag]

    positives = [t for t, score in scores.items() if score > 0]
    negatives = [t for t, score in scores.items() if score < 0]

    return {
        "liked_counts": dict(liked),
        "disliked_counts": dict(disliked),
        "scores": scores,
        "positive_tags": positives,
        "negative_tags": negatives,
        "explanation": (
            "MVP taste vector = like-count minus dislike-count for each tagged concept. "
            "This is intentionally interpretable and is not a learned buyer embedding."
        ),
    }


def tag_text(tag: str) -> str:
    return TAG_TO_TEXT.get(tag, tag.replace("_", " "))


def make_variants(profile: dict[str, Any]) -> list[dict[str, Any]]:
    pos = profile.get("positive_tags", [])
    neg = profile.get("negative_tags", [])

    # Five candidates are designed to probe different style dimensions.
    variant_specs = [
        ("warmth", ["warm", "warm_lighting", "natural_wood"], ["cold", "cold_grey"]),
        ("materials", ["natural_wood", "comfortable"], ["concrete", "dark_metal"]),
        ("palette", ["soft_neutral", "airy"], ["cold_grey", "dark"]),
        ("style", ["scandinavian", "minimal"], ["industrial", "maximalist"]),
        ("comfort", ["comfortable", "warm_lighting", "airy"], ["cluttered", "dark"]),
    ]

    variants = []
    for index, (axis, preferred, avoided) in enumerate(variant_specs, start=1):
        selected = [tag for tag in preferred if tag in pos]
        if not selected:
            # If the buyer has not expressed this exact tag, still create a
            # controlled probe around the axis.
            selected = preferred[:2]

        avoid = [tag for tag in avoided if tag in neg]
        if not avoid:
            avoid = avoided[:1]

        variants.append({
            "candidate_id": f"c{index}",
            "probe_axis": axis,
            "positive_tags": selected,
            "negative_tags": avoid,
        })
    return variants


def prompt_for(room: dict[str, Any], profile: dict[str, Any], variant: dict[str, Any]) -> str:
    positive = ", ".join(tag_text(t) for t in variant["positive_tags"])
    negative = ", ".join(tag_text(t) for t in variant["negative_tags"])
    global_positive = ", ".join(tag_text(t) for t in profile["positive_tags"][:5])

    return (
        "Photorealistic high-end apartment interior visualization. "
        f"Room: {room['description']} "
        f"Buyer preferences: {global_positive or 'balanced modern interior'}. "
        f"Current probe axis: {variant['probe_axis']}. "
        f"Emphasize: {positive}. "
        f"Avoid: {negative}. "
        "Keep the architecture coherent, realistic furniture scale, natural materials, "
        "professional real-estate visualization, daylight, clean composition."
    )


GenerationClient = SwarmClient | MockSwarmClient


def wants_mock(args: argparse.Namespace, settings: Settings) -> bool:
    return bool(getattr(args, "mock", False) or settings.mock_swarm)


def make_client(args: argparse.Namespace, settings: Settings) -> GenerationClient:
    url = getattr(args, "url", None) or settings.swarm_url
    if wants_mock(args, settings):
        return MockSwarmClient(url)
    return SwarmClient(url, api_key=settings.swarm_api_key)


def choose_model(client: GenerationClient, configured: str) -> str:
    if configured:
        return configured
    models = client.models()
    if not models:
        raise SwarmError(
            "No model was detected. Open SwarmUI and make sure a text-to-image model "
            "is installed/available, then set 'model' in config.json if needed."
        )
    return models[0]


def command_check(args: argparse.Namespace) -> None:
    settings = load_config(Path(args.config))
    client = make_client(args, settings)
    client.new_session()
    status = client.status()
    console.print("[bold]SwarmUI:[/]", client.base_url)
    if client.is_mock:
        console.print("[yellow]Mode:[/] offline mock")
    console.print("[bold]Session:[/]", client.session_id)
    console.print("[bold]Backend status:[/]", status.get("backend_status", {}))

    models = client.models()
    table = Table(title="Detected Models")
    table.add_column("Model")
    for model in models[:20]:
        table.add_row(model)
    console.print(table)
    if len(models) > 20:
        console.print(f"... and {len(models)-20} more")


def command_config(args: argparse.Namespace) -> None:
    settings = load_config(Path(args.config))
    console.print_json(data=settings.safe_dict())


def command_profile(args: argparse.Namespace) -> None:
    session_path = Path(args.input)
    if session_path.resolve() == DEFAULT_SESSION.resolve() and DATASET_SESSION.exists():
        session_path = DATASET_SESSION
    session = load_json(session_path)
    profile = build_profile(session)
    out = session_path.parent / "profile.json"
    save_json(out, profile)
    console.print_json(data=profile)
    console.print(f"\n[green]Saved:[/] {out}")


def command_show(args: argparse.Namespace) -> None:
    session = load_json(Path(args.input))
    console.print_json(data=session)


def generate_round(args: argparse.Namespace) -> None:
    settings = load_config(Path(args.config))
    session_path = Path(args.input)
    session = load_json(session_path)

    client = make_client(args, settings)
    client.new_session()
    model = choose_model(client, args.model or settings.model)

    profile = build_profile(session)
    variants = make_variants(profile)
    image_count = args.images if args.images is not None else settings.images_per_round
    round_no = len(session.get("rounds", [])) + 1
    round_dir = OUTPUTS / f"round_{round_no:02d}"
    round_dir.mkdir(parents=True, exist_ok=True)

    prompts = []
    results = []

    if client.is_mock:
        console.print("[yellow]Mock mode:[/] no SwarmUI request will be sent.")
    console.print(f"[bold]Generating round {round_no}[/] with {image_count} image(s) per candidate...")
    for variant in variants[:image_count]:
        prompt = prompt_for(session["room"], profile, variant)
        prompts.append({
            **variant,
            "prompt": prompt,
        })

        console.print(f"  [cyan]{variant['candidate_id']}[/] | probe={variant['probe_axis']}")
        generated = client.generate(
            prompt=prompt,
            model=model,
            images=1,
            width=settings.width,
            height=settings.height,
            steps=settings.steps,
            cfgscale=settings.cfgscale,
            negativeprompt=settings.negativeprompt,
            seed=settings.seed,
            extra_metadata={
                "project_round": str(round_no),
                "project_candidate": variant["candidate_id"],
                "project_probe_axis": variant["probe_axis"],
            },
        )

        candidate_results = []
        for idx, item in enumerate(generated, start=1):
            path = item.get("path")
            local = None
            if path and path.startswith("View/"):
                local_path = round_dir / f"{variant['candidate_id']}_{idx}.png"
                try:
                    client.download_view(path, local_path)
                    local = str(local_path.relative_to(ROOT))
                except SwarmError as exc:
                    console.print("[yellow]    Warning:[/]", exc)
            candidate_results.append({
                "swarm": item,
                "local_file": local,
                "choice": None,
            })

        results.append({
            **variant,
            "results": candidate_results,
        })

    save_json(round_dir / "prompts.json", {
        "round": round_no,
        "model": model,
        "profile": profile,
        "prompts": prompts,
    })
    save_json(round_dir / "generation_results.json", results)
    save_json(round_dir / "profile.json", profile)

    session.setdefault("rounds", []).append({
        "round": round_no,
        "model": model,
        "output_dir": str(round_dir.relative_to(ROOT)),
        "candidates": [
            {
                "candidate_id": r["candidate_id"],
                "probe_axis": r["probe_axis"],
                "positive_tags": r["positive_tags"],
                "negative_tags": r["negative_tags"],
                "choice": None,
            }
            for r in results
        ],
    })
    save_json(session_path, session)

    console.print("\n[green]Done.[/]")
    console.print("[bold]Output:[/]", round_dir)
    console.print(f"Open the images, then add like/dislike/skip choices to {session_path}.")
    console.print("Then run the next round.")


def command_demo(args: argparse.Namespace) -> None:
    session_path = ROOT / "data" / "demo_session.json"
    session = load_json(session_path)
    # Reset demo rounds so repeated runs are easy.
    session["rounds"] = []
    save_json(session_path, session)
    local_args = argparse.Namespace(
        config=args.config,
        input=str(session_path),
        url=args.url,
        model=args.model,
        images=args.images,
        mock=args.mock,
    )
    generate_round(local_args)


def command_dataset(args: argparse.Namespace) -> None:
    if not DATASET_MANIFEST.exists():
        raise SwarmError(
            "The dataset manifest is missing. Run setup_windows.ps1 first, "
            "or run prepare_dataset.py after configuring Kaggle authentication."
        )

    manifest = load_json(DATASET_MANIFEST)
    records = [record for record in manifest.get("images", []) if Path(
        manifest["dataset_root"]
    ).joinpath(record["path"]).exists()]
    if not records:
        raise SwarmError("The dataset manifest contains no available images.")

    session_path = Path(args.input)
    if session_path.resolve() == DEFAULT_SESSION.resolve() and DATASET_SESSION.exists():
        session_path = DATASET_SESSION
    session = load_json(session_path)
    profile = build_profile(session)
    variants = make_variants(profile)
    image_count = min(args.images or 5, len(variants))
    positive_tags = set(profile.get("positive_tags", []))
    used_paths = {
        candidate.get("source_image")
        for previous_round in session.get("rounds", [])
        for candidate in previous_round.get("candidates", [])
        if candidate.get("source_image")
    }

    negative_tags = set(profile.get("negative_tags", []))
    records.sort(key=lambda record: (
        0 if record.get("style", "") in positive_tags else (
            2 if record.get("style", "") in negative_tags else 1
        ),
        record.get("style", ""),
        record.get("path", ""),
    ))
    unused_records = [record for record in records if record["path"] not in used_paths]
    if len(unused_records) >= image_count:
        records = unused_records

    selected = []
    selected_styles = set()
    for record in records:
        style = record.get("style", "unknown")
        if style not in selected_styles:
            selected.append(record)
            selected_styles.add(style)
        if len(selected) == image_count:
            break
    if len(selected) < image_count:
        selected_paths = {record["path"] for record in selected}
        for record in records:
            if record["path"] not in selected_paths:
                selected.append(record)
                selected_paths.add(record["path"])
            if len(selected) == image_count:
                break

    round_no = 1
    while (OUTPUTS / f"dataset_round_{round_no:02d}").exists():
        round_no += 1
    round_dir = OUTPUTS / f"dataset_round_{round_no:02d}"
    round_dir.mkdir(parents=True, exist_ok=True)
    dataset_root = Path(manifest["dataset_root"])
    prompts = []
    results = []

    console.print("[bold]Using existing dataset images; no image generation will run.[/]")
    console.print(f"[bold]Preparing dataset round {round_no}[/] with {image_count} image(s)...")
    for variant, record in zip(variants[:image_count], selected):
        source = dataset_root / record["path"]
        destination = round_dir / f"{variant['candidate_id']}{source.suffix.lower()}"
        shutil.copy2(source, destination)
        prompt = prompt_for(session["room"], profile, variant)
        prompts.append({
            **variant,
            "prompt": prompt,
            "dataset_style": record.get("style", "unknown"),
            "source_image": record["path"],
        })
        results.append({
            **variant,
            "dataset_style": record.get("style", "unknown"),
            "source_image": record["path"],
            "local_file": str(destination.relative_to(ROOT)),
            "choice": None,
        })
        console.print(
            f"  [cyan]{variant['candidate_id']}[/] | "
            f"style={record.get('style', 'unknown')} | source={record['path']}"
        )

    save_json(round_dir / "prompts.json", {
        "round": round_no,
        "mode": "dataset_reference",
        "profile": profile,
        "prompts": prompts,
    })
    save_json(round_dir / "generation_results.json", {
        "mode": "dataset_reference",
        "results": results,
    })
    save_json(round_dir / "profile.json", profile)

    dataset_session = copy.deepcopy(session)
    dataset_session.setdefault("rounds", []).append({
        "round": round_no,
        "mode": "dataset_reference",
        "output_dir": str(round_dir.relative_to(ROOT)),
        "candidates": [
            {
                "candidate_id": result["candidate_id"],
                "dataset_style": result["dataset_style"],
                "source_image": result["source_image"],
                "choice": None,
            }
            for result in results
        ],
    })
    save_json(DATASET_SESSION, dataset_session)

    console.print("\n[green]Dataset pipeline complete.[/]")
    console.print("[bold]Results:[/]", round_dir)
    console.print("[bold]Record choices in:[/]", DATASET_SESSION)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Apartment buyer-clone MVP client for SwarmUI"
    )
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("check", help="Check SwarmUI connection and models")
    p.add_argument("--url", default=None)
    p.add_argument("--mock", action="store_true", help="Use the offline mock client")
    p.set_defaults(func=command_check)

    p = sub.add_parser("config", help="Show resolved config with .env overrides")
    p.set_defaults(func=command_config)

    p = sub.add_parser("profile", help="Build the transparent taste vector")
    p.add_argument("--input", default=str(DEFAULT_SESSION))
    p.set_defaults(func=command_profile)

    p = sub.add_parser("show", help="Print the session JSON")
    p.add_argument("--input", default=str(DEFAULT_SESSION))
    p.set_defaults(func=command_show)

    p = sub.add_parser("round", help="Generate one candidate round")
    p.add_argument("--input", default=str(DEFAULT_SESSION))
    p.add_argument("--url", default=None)
    p.add_argument("--model", default=None)
    p.add_argument("--images", type=int, default=None, help="Number of candidates, max 5")
    p.add_argument("--mock", action="store_true", help="Use the offline mock client")
    p.set_defaults(func=generate_round)

    p = sub.add_parser("demo", help="Run the included demo session")
    p.add_argument("--url", default=None)
    p.add_argument("--model", default=None)
    p.add_argument("--images", type=int, default=None)
    p.add_argument("--mock", action="store_true", help="Use the offline mock client")
    p.set_defaults(func=command_demo)

    p = sub.add_parser(
        "dataset",
        help="Use existing downloaded dataset images without generating new images",
    )
    p.add_argument("--input", default=str(DEFAULT_SESSION))
    p.add_argument("--images", type=int, default=5)
    p.set_defaults(func=command_dataset)

    return parser


if __name__ == "__main__":
    if len(sys.argv) == 1:
        args = argparse.Namespace(
            config=str(DEFAULT_CONFIG),
            images=5,
            input=str(DEFAULT_SESSION),
        )
        try:
            if DATASET_MANIFEST.exists():
                console.print("Running the dataset pipeline because no command was provided.")
                command_dataset(args)
            else:
                console.print("Dataset manifest not found; running the offline demo instead.")
                command_demo(argparse.Namespace(
                    config=str(DEFAULT_CONFIG),
                    url=None,
                    model=None,
                    images=2,
                    mock=True,
                ))
        except SwarmError as exc:
            print(f"\nERROR: {exc}")
            raise SystemExit(1)
        raise SystemExit(0)

    args = build_parser().parse_args()
    try:
        args.func(args)
    except SwarmError as exc:
        print(f"\nERROR: {exc}")
        raise SystemExit(1)
