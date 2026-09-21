import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any

from PIL import Image, UnidentifiedImageError

DATASET_ID = "stepanyarullin/interior-design-styles"
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
ROOT = Path(__file__).resolve().parent
DEFAULT_MANIFEST = ROOT / "data" / "processed" / "interior_styles_manifest.json"


def find_dataset_root(dataset_path: Path) -> Path:
    candidates = [dataset_path]
    candidates.extend(path for path in dataset_path.rglob("*") if path.is_dir())
    for candidate in candidates:
        if any((candidate / name).exists() for name in ("dataset_train", "dataset_test")):
            return candidate
    return dataset_path


def load_test_labels(dataset_root: Path) -> dict[str, str]:
    labels_path = next(dataset_root.rglob("test_labels.csv"), None)
    if labels_path is None:
        return {}

    with labels_path.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        return {}

    fieldnames = rows[0].keys()
    image_field = next((name for name in fieldnames if "file" in name.lower() or "image" in name.lower()), None)
    label_field = next((name for name in fieldnames if "label" in name.lower() or "style" in name.lower()), None)
    if not image_field or not label_field:
        return {}
    return {str(row[image_field]): str(row[label_field]) for row in rows}


def image_label(path: Path, dataset_root: Path, test_labels: dict[str, str]) -> tuple[str, str]:
    relative_parts = path.relative_to(dataset_root).parts
    split = "unknown"
    for index, part in enumerate(relative_parts):
        lowered = part.lower()
        if lowered in {"dataset_train", "train", "training"}:
            split = "train"
            if index + 1 < len(relative_parts) and not relative_parts[index + 1].lower().endswith(tuple(IMAGE_EXTENSIONS)):
                return split, relative_parts[index + 1]
        if lowered in {"dataset_test", "test", "testing"}:
            split = "test"

    label = test_labels.get(path.name, "")
    if not label:
        label = path.parent.name
    return split, label.replace(" ", "_").lower()


def build_manifest(dataset_root: Path, manifest_path: Path) -> dict[str, Any]:
    test_labels = load_test_labels(dataset_root)
    records = []
    invalid = []

    for path in sorted(dataset_root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in IMAGE_EXTENSIONS:
            continue
        split, label = image_label(path, dataset_root, test_labels)
        try:
            with Image.open(path) as image:
                image.verify()
            with Image.open(path) as image:
                width, height = image.size
                mode = image.mode
        except (OSError, UnidentifiedImageError) as exc:
            invalid.append({"path": str(path.relative_to(dataset_root)), "error": str(exc)})
            continue

        records.append({
            "path": str(path.relative_to(dataset_root)),
            "split": split,
            "style": label,
            "width": width,
            "height": height,
            "mode": mode,
        })

    manifest = {
        "dataset_id": DATASET_ID,
        "dataset_root": str(dataset_root),
        "image_count": len(records),
        "invalid_count": len(invalid),
        "styles": dict(sorted(Counter(record["style"] for record in records).items())),
        "splits": dict(sorted(Counter(record["split"] for record in records).items())),
        "images": records,
        "invalid_images": invalid,
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Download and validate the Kaggle interior styles dataset")
    parser.add_argument("--dataset-dir", type=Path, help="Use an already downloaded dataset directory")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    args = parser.parse_args()

    if args.dataset_dir:
        dataset_root = find_dataset_root(args.dataset_dir.resolve())
    else:
        try:
            from kagglehub import dataset_download
            downloaded = Path(dataset_download(DATASET_ID))
        except Exception as exc:
            raise SystemExit(
                "Could not download the Kaggle dataset. Configure Kaggle authentication first "
                f"and rerun setup. Details: {exc}"
            ) from exc
        dataset_root = find_dataset_root(downloaded)

    manifest = build_manifest(dataset_root, args.manifest)
    print(f"Dataset ready: {manifest['image_count']} valid images")
    print(f"Styles: {len(manifest['styles'])}; invalid images: {manifest['invalid_count']}")
    print(f"Manifest: {args.manifest}")


if __name__ == "__main__":
    main()
