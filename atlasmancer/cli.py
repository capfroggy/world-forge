"""Command-line interface for Atlasmancer."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .generator import generate_world
from .i18n import DEFAULT_LOCALE, UnsupportedLocaleError, available_locales, load_locale
from .renderers.html import render_html


def build_parser(locale: str = DEFAULT_LOCALE) -> argparse.ArgumentParser:
    catalog = load_locale(locale)
    parser = argparse.ArgumentParser(
        prog="atlasmancer",
        description=catalog.t("cli.description"),
    )
    parser.add_argument("--seed", help=catalog.t("cli.flags.seed"))
    parser.add_argument("--width", type=int, default=72, help=catalog.t("cli.flags.width"))
    parser.add_argument("--height", type=int, default=28, help=catalog.t("cli.flags.height"))
    parser.add_argument(
        "--landmarks",
        type=int,
        default=9,
        help=catalog.t("cli.flags.landmarks"),
    )
    parser.add_argument(
        "--format",
        choices=("plain", "ansi", "markdown", "json", "html", "png"),
        default="plain",
        help=catalog.t("cli.flags.format"),
    )
    parser.add_argument(
        "--locale",
        default=DEFAULT_LOCALE,
        help=catalog.t("cli.flags.locale"),
    )
    parser.add_argument(
        "--tile-size",
        type=int,
        default=12,
        help=catalog.t("cli.flags.tile_size"),
    )
    parser.add_argument("--output", type=Path, help=catalog.t("cli.flags.output"))
    return parser


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    requested_locale = _requested_locale(argv)
    parser_locale = requested_locale if requested_locale in available_locales() else DEFAULT_LOCALE
    parser = build_parser(parser_locale)
    args = parser.parse_args(argv)
    catalog = load_locale(parser_locale)

    try:
        load_locale(args.locale)
    except UnsupportedLocaleError:
        parser.error(
            catalog.t(
                "cli.errors.unsupported_locale",
                locale=args.locale,
                available=", ".join(available_locales()),
            )
        )

    world = generate_world(
        seed=args.seed,
        width=args.width,
        height=args.height,
        landmark_count=args.landmarks,
        locale=args.locale,
    )

    if args.format == "png":
        if not args.output:
            parser.error(catalog.t("cli.errors.png_requires_output"))
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


def _requested_locale(argv: list[str]) -> str:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--locale", default=DEFAULT_LOCALE)
    args, _ = parser.parse_known_args(argv)
    return args.locale
