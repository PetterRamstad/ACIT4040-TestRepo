from pathlib import Path

from scripts.data.interior_inspect import inspect_interior_dataset


def test_interior_inspection_counts_room_folders_and_filename_metadata(tmp_path):
    _write(tmp_path / "living_room" / "train-asian-asian_0.jpg", b"same")
    _write(tmp_path / "living_room" / "test-victorian-victorian_1.jpg", b"other")
    _write(tmp_path / "kitchen" / "bad-name.jpg", b"same")

    report = inspect_interior_dataset(tmp_path)

    assert report["total_files"] == 3
    assert report["rooms"]["living_room"]["file_count"] == 2
    assert report["rooms"]["kitchen"]["file_count"] == 1
    assert report["extensions"] == {".jpg": 3}
    assert report["filename_metadata"]["splits"] == {"test": 1, "train": 1}
    assert report["filename_metadata"]["styles"] == {"asian": 1, "victorian": 1}
    assert report["filename_metadata"]["non_matching_files"] == ["kitchen/bad-name.jpg"]
    assert report["duplicate_hashes"][0]["files"] == [
        "kitchen/bad-name.jpg",
        "living_room/train-asian-asian_0.jpg",
    ]


def test_interior_inspection_reports_missing_expected_room_folders(tmp_path):
    _write(tmp_path / "living_room" / "train-modern-modern_0.jpg", b"image")

    report = inspect_interior_dataset(tmp_path)

    assert "bathroom" in report["missing_expected_rooms"]
    assert "living_room" not in report["missing_expected_rooms"]


def test_interior_inspection_reports_dimensions_and_corrupt_images(tmp_path):
    _write(tmp_path / "bedroom" / "train-modern-modern_0.png", _png_header(width=640, height=480))
    _write(tmp_path / "bedroom" / "train-modern-modern_1.jpg", b"not an image")

    report = inspect_interior_dataset(tmp_path)

    assert report["image_dimensions"]["bedroom/train-modern-modern_0.png"] == {
        "width": 640,
        "height": 480,
    }
    assert report["corrupt_files"] == ["bedroom/train-modern-modern_1.jpg"]


def _write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


def _png_header(width: int, height: int) -> bytes:
    return (
        b"\x89PNG\r\n\x1a\n"
        + b"\x00\x00\x00\rIHDR"
        + width.to_bytes(4, "big")
        + height.to_bytes(4, "big")
        + b"\x08\x02\x00\x00\x00"
    )
