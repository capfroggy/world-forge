"""Regenerate the checked-in Atlasmancer example exports."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from atlasmancer.cli import main as atlasmancer_main

SAMPLE_SEED = "atlasmancer-sample"
SAMPLE_WIDTH = 72
SAMPLE_HEIGHT = 28
SAMPLE_LANDMARKS = 9

EXAMPLE_OUTPUTS = (
    ("example-en-gm.html", "html", "en", "gm"),
    ("example-en-player.html", "html", "en", "player"),
    ("example-es-gm.html", "html", "es", "gm"),
    ("example-es-player.html", "html", "es", "player"),
    ("example-campaign.json", "campaign", "en", "gm"),
)


def build_examples(output_dir: Path = ROOT / "examples") -> list[Path]:
    """Build all sample exports and return their output paths."""

    output_dir.mkdir(parents=True, exist_ok=True)
    generated: list[Path] = []

    for filename, export_format, locale, audience in EXAMPLE_OUTPUTS:
        output_path = output_dir / filename
        result = atlasmancer_main(
            [
                "--seed",
                SAMPLE_SEED,
                "--width",
                str(SAMPLE_WIDTH),
                "--height",
                str(SAMPLE_HEIGHT),
                "--landmarks",
                str(SAMPLE_LANDMARKS),
                "--locale",
                locale,
                "--audience",
                audience,
                "--format",
                export_format,
                "--output",
                str(output_path),
            ]
        )
        if result != 0:
            raise RuntimeError(f"atlasmancer failed while building {output_path}")
        generated.append(output_path)

    return generated


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Regenerate Atlasmancer example exports.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "examples",
        help="Directory to write examples into.",
    )
    args = parser.parse_args(argv)

    for path in build_examples(args.output_dir):
        print(path)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
