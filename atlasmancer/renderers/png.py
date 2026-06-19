"""Printable PNG renderer."""

from __future__ import annotations

from pathlib import Path
import textwrap

from atlasmancer.generator import World, landmark_legend, terrain_legend
from atlasmancer.i18n import load_locale


PALETTE = {
    "~": (66, 119, 153),
    ",": (112, 174, 174),
    ".": (211, 187, 126),
    ";": (139, 171, 98),
    ":": (190, 138, 85),
    "^": (66, 117, 71),
    "A": (136, 132, 118),
    "*": (235, 232, 218),
    "|": (64, 153, 190),
    "C": (215, 167, 46),
    "v": (217, 137, 61),
    "X": (181, 80, 67),
    "T": (142, 106, 184),
    "?": (189, 115, 178),
}

MARKER_FILL = {
    "capital": (171, 67, 48),
    "village": (189, 104, 42),
    "ruin": (115, 55, 48),
    "tower": (98, 78, 145),
    "oddity": (147, 72, 139),
}


def render_png(world: World, output: str | Path, tile_size: int = 12) -> None:
    """Render a parchment-style printable PNG map."""

    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError as exc:  # pragma: no cover - depends on optional extra
        raise RuntimeError(
            "PNG export requires Pillow. Install it with: python -m pip install -e .[image]"
        ) from exc

    tile_size = max(6, min(28, tile_size))
    catalog = load_locale(world.locale)
    margin = 46
    header = 86
    footer = 38
    sidebar = 430
    gap = 26
    map_width = world.width * tile_size
    map_height = world.height * tile_size
    image_width = margin * 2 + map_width + gap + sidebar
    terrain_labels = terrain_legend(catalog)
    landmark_labels = landmark_legend(catalog)
    legend_rows = (len(terrain_labels) + len(landmark_labels) + 1) // 2
    sidebar_entries = min(len(world.landmarks), 8)
    sidebar_height = margin + header + legend_rows * 24 + 88 + sidebar_entries * 86 + footer
    image_height = max(margin + header + map_height + footer, sidebar_height, 760)

    image = Image.new("RGB", (image_width, image_height), (238, 218, 176))
    draw = ImageDraw.Draw(image)

    title_font = _font(ImageFont, 34, bold=True)
    subtitle_font = _font(ImageFont, 15)
    label_font = _font(ImageFont, max(10, tile_size), bold=True)
    small_font = _font(ImageFont, 13)
    body_font = _font(ImageFont, 15)
    heading_font = _font(ImageFont, 21, bold=True)

    _paper_texture(draw, image_width, image_height)

    draw.text((margin, 28), world.title, fill=(54, 38, 21), font=title_font)
    draw.text(
        (margin, 66),
        f"{catalog.t('export.seed_label')}: {world.seed} | {world.width} x {world.height} | {catalog.t('export.printable_gm_map')}",
        fill=(91, 69, 43),
        font=subtitle_font,
    )

    map_x = margin
    map_y = margin + header
    _draw_panel(draw, (map_x - 12, map_y - 12, map_x + map_width + 12, map_y + map_height + 12))
    _draw_tiles(draw, world, map_x, map_y, tile_size)
    _draw_grid(draw, world, map_x, map_y, tile_size)
    _draw_landmarks(draw, world, map_x, map_y, tile_size, label_font, small_font)
    _draw_compass(draw, map_x + map_width - 62, map_y + 18)
    notes_top = map_y + map_height + 30
    notes_bottom = image_height - margin - 24
    if notes_bottom - notes_top > 90:
        _draw_notes_area(
            draw,
            map_x,
            notes_top,
            map_width,
            notes_bottom - notes_top,
            heading_font,
            catalog.t("export.gm_notes_label"),
        )

    side_x = map_x + map_width + gap
    side_y = map_y - 12
    _draw_panel(draw, (side_x, side_y, side_x + sidebar, image_height - margin))
    _draw_sidebar(
        draw,
        world,
        side_x + 20,
        side_y + 18,
        sidebar - 40,
        image_height - margin - 20,
        catalog,
        heading_font,
        body_font,
        small_font,
    )
    _draw_border(draw, image_width, image_height)

    Path(output).parent.mkdir(parents=True, exist_ok=True)
    image.save(output)


def _draw_tiles(draw, world: World, map_x: int, map_y: int, tile_size: int) -> None:
    for y, row in enumerate(world.tiles):
        for x, char in enumerate(row):
            fill = PALETTE.get(char, PALETTE[";"])
            left = map_x + x * tile_size
            top = map_y + y * tile_size
            draw.rectangle((left, top, left + tile_size, top + tile_size), fill=fill)
            _draw_terrain_mark(draw, char, left, top, tile_size)


def _draw_terrain_mark(draw, char: str, left: int, top: int, tile_size: int) -> None:
    if tile_size < 10:
        return
    center_x = left + tile_size // 2
    bottom = top + tile_size - 2
    if char == "A":
        draw.polygon(
            [(left + 2, bottom), (center_x, top + 2), (left + tile_size - 2, bottom)],
            outline=(82, 77, 67),
        )
    elif char == "^":
        draw.polygon(
            [(left + 2, bottom), (center_x, top + 2), (left + tile_size - 2, bottom)],
            fill=(45, 95, 50),
        )
    elif char == "|":
        draw.line((center_x, top, center_x, top + tile_size), fill=(31, 101, 145), width=max(2, tile_size // 4))
    elif char == "~":
        draw.arc((left + 1, top + 2, left + tile_size - 1, top + tile_size - 2), 190, 350, fill=(41, 92, 125))


def _draw_grid(draw, world: World, map_x: int, map_y: int, tile_size: int) -> None:
    if tile_size < 10:
        return
    color = (84, 63, 38)
    for x in range(0, world.width + 1):
        if x % 5 == 0:
            left = map_x + x * tile_size
            draw.line((left, map_y, left, map_y + world.height * tile_size), fill=color, width=1)
    for y in range(0, world.height + 1):
        if y % 5 == 0:
            top = map_y + y * tile_size
            draw.line((map_x, top, map_x + world.width * tile_size, top), fill=color, width=1)


def _draw_landmarks(draw, world: World, map_x: int, map_y: int, tile_size: int, label_font, small_font) -> None:
    for index, landmark in enumerate(world.landmarks):
        center_x = map_x + landmark.x * tile_size + tile_size // 2
        center_y = map_y + landmark.y * tile_size + tile_size // 2
        radius = max(7, tile_size // 2 + 2)
        fill = MARKER_FILL.get(landmark.kind, (150, 84, 138))
        draw.ellipse(
            (center_x - radius, center_y - radius, center_x + radius, center_y + radius),
            fill=fill,
            outline=(35, 25, 17),
            width=2,
        )
        _center_text(draw, landmark.symbol, center_x, center_y - 1, label_font, fill=(255, 242, 200))

        label = landmark.name
        label_x = center_x + radius + 4
        label_y = center_y - 9 + ((index % 3) - 1) * 7
        bbox = draw.textbbox((label_x, label_y), label, font=small_font)
        pad = 3
        draw.rectangle(
            (bbox[0] - pad, bbox[1] - pad, bbox[2] + pad, bbox[3] + pad),
            fill=(246, 226, 177),
            outline=(103, 78, 47),
        )
        draw.text((label_x, label_y), label, font=small_font, fill=(48, 34, 20))


def _draw_sidebar(
    draw,
    world: World,
    x: int,
    y: int,
    width: int,
    max_y: int,
    catalog,
    heading_font,
    body_font,
    small_font,
) -> None:
    draw.text((x, y), catalog.t("export.legend_label"), fill=(54, 38, 21), font=heading_font)
    cursor_y = y + 34
    landmark_labels = landmark_legend(catalog)
    legend = {**terrain_legend(catalog), **landmark_labels}
    for index, (symbol, name) in enumerate(legend.items()):
        col = index % 2
        row = index // 2
        item_x = x + col * (width // 2)
        item_y = cursor_y + row * 24
        draw.rectangle((item_x, item_y, item_x + 17, item_y + 17), fill=PALETTE.get(symbol, PALETTE[";"]), outline=(78, 56, 32))
        _center_text(draw, symbol if symbol in landmark_labels else "", item_x + 8, item_y + 8, small_font, fill=(30, 22, 14))
        draw.text((item_x + 24, item_y), name, fill=(54, 38, 21), font=small_font)

    cursor_y += ((len(legend) + 1) // 2) * 24 + 22
    draw.text((x, cursor_y), catalog.t("export.landmarks_label"), fill=(54, 38, 21), font=heading_font)
    cursor_y += 34

    for landmark in world.landmarks[:8]:
        heading = f"{landmark.symbol} {landmark.name} ({landmark.kind})"
        draw.text((x, cursor_y), heading, fill=(69, 39, 28), font=body_font)
        cursor_y += 20
        for line in _wrap(f"{catalog.t('export.hook_label')}: {landmark.hook}", 48)[:2]:
            draw.text((x + 8, cursor_y), line, fill=(54, 38, 21), font=small_font)
            cursor_y += 16
        for line in _wrap(f"{catalog.t('export.danger_label')}: {landmark.danger}", 48)[:1]:
            draw.text((x + 8, cursor_y), line, fill=(95, 41, 32), font=small_font)
            cursor_y += 16
        cursor_y += 8
        if cursor_y > max_y:
            break


def _draw_panel(draw, box: tuple[int, int, int, int]) -> None:
    draw.rectangle(box, fill=(245, 226, 183), outline=(115, 84, 48), width=2)
    inset = 5
    draw.rectangle(
        (box[0] + inset, box[1] + inset, box[2] - inset, box[3] - inset),
        outline=(174, 135, 80),
        width=1,
    )


def _draw_compass(draw, x: int, y: int) -> None:
    draw.ellipse((x, y, x + 44, y + 44), outline=(58, 41, 24), width=2)
    draw.polygon([(x + 22, y + 4), (x + 17, y + 22), (x + 22, y + 18), (x + 27, y + 22)], fill=(58, 41, 24))
    draw.text((x + 17, y - 11), "N", fill=(58, 41, 24))


def _draw_notes_area(draw, x: int, y: int, width: int, height: int, heading_font, label: str) -> None:
    draw.text((x, y), label, fill=(54, 38, 21), font=heading_font)
    line_y = y + 42
    while line_y < y + height - 8:
        draw.line((x, line_y, x + width, line_y), fill=(174, 135, 80), width=1)
        line_y += 30


def _paper_texture(draw, width: int, height: int) -> None:
    for offset in range(0, width + height, 34):
        draw.line((offset, 0, 0, offset), fill=(232, 207, 158), width=1)


def _draw_border(draw, width: int, height: int) -> None:
    draw.rectangle((14, 14, width - 14, height - 14), outline=(91, 65, 37), width=3)
    draw.rectangle((22, 22, width - 22, height - 22), outline=(170, 125, 69), width=1)


def _center_text(draw, text: str, center_x: int, center_y: int, font, fill: tuple[int, int, int]) -> None:
    if not text:
        return
    bbox = draw.textbbox((0, 0), text, font=font)
    draw.text(
        (center_x - (bbox[2] - bbox[0]) / 2, center_y - (bbox[3] - bbox[1]) / 2),
        text,
        fill=fill,
        font=font,
    )


def _font(image_font, size: int, bold: bool = False):
    names = [
        "C:/Windows/Fonts/georgiab.ttf" if bold else "C:/Windows/Fonts/georgia.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf",
    ]
    for name in names:
        try:
            return image_font.truetype(name, size)
        except OSError:
            continue
    return image_font.load_default()


def _wrap(text: str, width: int) -> list[str]:
    return textwrap.wrap(text, width=width, break_long_words=False) or [text]
