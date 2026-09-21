import argparse
import json
import tempfile
from pathlib import Path

import main


root = Path(__file__).parent
session = json.loads((root / "data" / "demo_session.json").read_text(encoding="utf-8"))
session["rounds"] = []

profile = main.build_profile(session)
variants = main.make_variants(profile)

assert len(variants) == 5
assert profile["positive_tags"]
assert profile["negative_tags"]

for variant in variants:
    prompt = main.prompt_for(session["room"], profile, variant)
    assert "Photorealistic" in prompt

smoke_output_parent = root / "outputs"
smoke_output_parent.mkdir(parents=True, exist_ok=True)

with tempfile.TemporaryDirectory(dir=smoke_output_parent) as temp_dir:
    temp_root = Path(temp_dir)
    session_path = temp_root / "session.json"
    session_path.write_text(json.dumps(session), encoding="utf-8")

    old_outputs = main.OUTPUTS
    main.OUTPUTS = temp_root / "outputs"
    try:
        args = argparse.Namespace(
            config=str(root / "config.json"),
            input=str(session_path),
            url=None,
            model=None,
            images=2,
            mock=True,
        )
        main.generate_round(args)
        round_dir = main.OUTPUTS / "round_01"
        assert (round_dir / "prompts.json").exists()
        assert (round_dir / "generation_results.json").exists()
        assert len(list(round_dir.glob("*.png"))) == 2

        demo_root = temp_root / "demo_root"
        (demo_root / "data").mkdir(parents=True)
        (demo_root / "data" / "demo_session.json").write_text(
            json.dumps(session),
            encoding="utf-8",
        )
        captured = {}
        old_root = main.ROOT
        real_generate_round = main.generate_round

        def fake_generate_round(generated_args: argparse.Namespace) -> None:
            captured["mock"] = generated_args.mock
            captured["input"] = generated_args.input

        try:
            main.ROOT = demo_root
            main.generate_round = fake_generate_round
            main.command_demo(argparse.Namespace(
                config=str(root / "config.json"),
                url=None,
                model=None,
                images=1,
                mock=True,
            ))
        finally:
            main.ROOT = old_root
            main.generate_round = real_generate_round

        assert captured["mock"] is True
        assert captured["input"] == str(demo_root / "data" / "demo_session.json")
    finally:
        main.OUTPUTS = old_outputs

print("Smoke test passed: profile, prompts, mock generation, demo mock mode and artifacts are valid.")
