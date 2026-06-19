"""Command-line interface for Atlasmancer."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .generator import generate_world
from .renderers.html import render_html


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="atlasmancer",
        description="Generate tiny deterministic fantasy worlds for tabletop campaigns.",
    )
    parser.add_argument("--seed", help="Seed text for deterministic worlds.")
    parser.add_argument("--width", type=int, default=72, help="Map width, from 24 to 140.")
    parser.add_argument("--height", type=int, default=28, help="Map height, from 12 to 60.")
    parser.add_argument(
        "--landmarks",
        type=int,
        default=9,
        help="Number of named places to add, from 0 to 30.",
    )
    parser.add_argument(
        "--format",
        choices=("plain", "ansi", "markdown", "json", "html", "png"),
        default="plain",
        help="Output format.",
    )
    parser.add_argument(
        "--tile-size",
        type=int,
        default=12,
        help="Pixel size for PNG tiles, from 6 to 28.",
    )
    parser.add_argument("--output", type=Path, help="Write output to a file.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    world = generate_world(
        seed=args.seed,
        width=args.width,
        height=args.height,
        landmark_count=args.landmarks,
    )

    if args.format == "png":
        if not args.output:
            parser.error("--format png requires --output")
        from .renderers.png import render_png

        try:
            render_png(world, args.output, tile_size=args.tile_size)
        except RuntimeError as error:
            parser.error(str(error))
        return 0

    if args.format == "json":
        output = world.to_json()
    elif args.format == "markdown":
        output = world.to_markdown()
    elif args.format == "html":
        output = render_html(world)
    elif args.format == "ansi":
        output = world.render_ansi()
    else:
        output = world.render_plain()

    if args.output:
        args.output.write_text(output + "\n", encoding="utf-8")
    else:
        sys.stdout.write(output + "\n")

    return 0
