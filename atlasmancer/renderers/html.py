"""Printable HTML renderer."""

from __future__ import annotations

from html import escape

from atlasmancer.generator import World, landmark_kind_label, landmark_legend, terrain_legend
from atlasmancer.i18n import load_locale


CLASS_BY_SYMBOL = {
    "~": "water",
    ",": "shoal",
    ".": "coast",
    ";": "grass",
    ":": "dry",
    "^": "forest",
    "A": "mountain",
    "*": "snow",
    "|": "river",
    "C": "capital",
    "v": "village",
    "X": "ruin",
    "T": "tower",
    "?": "oddity",
}


def render_html(world: World, audience: str = "gm") -> str:
    """Render a self-contained printable HTML atlas page."""

    catalog = load_locale(world.locale)
    landmark_labels = landmark_legend(catalog)
    cells = []
    for row in world.tiles:
        for char in row:
            css_class = CLASS_BY_SYMBOL.get(char, "grass")
            label = char if char in landmark_labels else ""
            cells.append(f'<span class="tile {css_class}">{escape(label)}</span>')

    legend_items = []
    for symbol, name in {**terrain_legend(catalog), **landmark_labels}.items():
        css_class = CLASS_BY_SYMBOL.get(symbol, "grass")
        legend_items.append(
            f'<span class="legend-item"><span class="swatch {css_class}">{escape(symbol)}</span>{escape(name)}</span>'
        )

    landmark_cards = []
    for landmark in world.landmarks:
        card_lines = [
            '<article class="landmark">',
            f"<h3>{escape(landmark.symbol)} {escape(landmark.name)}</h3>",
            f"<p><strong>{escape(landmark_kind_label(landmark.kind, catalog).title())}</strong> at {landmark.x}, {landmark.y}</p>",
            f"<p><b>{escape(catalog.t('export.hook_label'))}:</b> {escape(landmark.hook)}</p>",
            f"<p><b>{escape(catalog.t('export.npc_label'))}:</b> {escape(landmark.npc)}</p>",
            f"<p><b>{escape(catalog.t('export.rumor_label'))}:</b> {escape(landmark.rumor)}</p>",
        ]
        if audience != "player":
            card_lines.extend(
                [
                    f"<p><b>{escape(catalog.t('export.danger_label'))}:</b> {escape(landmark.danger)}</p>",
                    f"<p><b>{escape(catalog.t('export.reward_label'))}:</b> {escape(landmark.reward)}</p>",
                    f'<p class="dm"><b>{escape(catalog.t("export.secret_label"))}:</b> {escape(landmark.secret)}</p>',
                ]
            )
        card_lines.append("</article>")
        landmark_cards.append("\n".join(card_lines))

    region_cards = []
    for region in world.regions:
        kind = catalog.t(f"terrain.{region.kind}")
        region_cards.append(
            "\n".join(
                [
                    '<article class="region">',
                    f"<h3>{escape(region.name)}</h3>",
                    f"<p><strong>{escape(kind.title())}</strong> | {region.tile_count} tiles</p>",
                    f"<p>{escape(region.description)}</p>",
                    "</article>",
                ]
            )
        )

    atlas_label = catalog.t("export.printable_player_atlas") if audience == "player" else catalog.t("export.printable_gm_atlas")
    header_lines = [
        f"<h1>{escape(world.title)}</h1>",
        f"<p>{escape(catalog.t('export.seed_label'))} <code>{escape(world.seed)}</code> | {world.width} x {world.height} | {escape(atlas_label)}</p>",
    ]
    if audience == "player":
        header_lines.append(f'<p class="player-note">{escape(catalog.t("export.audience_player_note"))}</p>')

    return "\n".join(
        [
            "<!doctype html>",
            f'<html lang="{escape(catalog.locale)}">',
            "<head>",
            '<meta charset="utf-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1">',
            f"<title>{escape(world.title)}</title>",
            "<style>",
            _css(world.width),
            "</style>",
            "</head>",
            "<body>",
            '<main class="page">',
            "<header>",
            *header_lines,
            "</header>",
            '<section class="layout">',
            '<section class="map-panel" aria-label="World map">',
            '<div class="map">',
            "".join(cells),
            "</div>",
            f'<h2 class="legend-title">{escape(catalog.t("export.legend_label"))}</h2>',
            '<div class="legend">',
            "".join(legend_items),
            "</div>",
            "</section>",
            '<aside class="notes">',
            f"<h2>{escape(catalog.t('export.regions_label'))}</h2>",
            "".join(region_cards),
            f"<h2>{escape(catalog.t('export.landmarks_label'))}</h2>",
            "".join(landmark_cards),
            "</aside>",
            "</section>",
            "</main>",
            "</body>",
            "</html>",
        ]
    )


def _css(width: int) -> str:
    return f"""
@page {{ size: landscape; margin: 10mm; }}
* {{ box-sizing: border-box; }}
body {{
  margin: 0;
  color: #2f2619;
  background: #ead7ad;
  font-family: Georgia, 'Times New Roman', serif;
}}
.page {{
  max-width: 1500px;
  margin: 0 auto;
  padding: 24px;
}}
header {{
  border-bottom: 2px solid #7f5f34;
  margin-bottom: 18px;
}}
h1 {{
  margin: 0;
  font-size: 38px;
  letter-spacing: 0;
}}
header p {{
  margin: 8px 0 14px;
  color: #5b472d;
}}
.player-note {{
  font-style: italic;
}}
.layout {{
  display: grid;
  grid-template-columns: minmax(520px, 1fr) 420px;
  gap: 22px;
  align-items: start;
}}
.map-panel {{
  background: #f3e4c1;
  border: 3px double #7f5f34;
  padding: 14px;
}}
.map {{
  display: grid;
  grid-template-columns: repeat({width}, minmax(4px, 1fr));
  width: 100%;
  border: 1px solid rgba(64, 45, 22, 0.45);
  background: #d7bf86;
}}
.tile {{
  display: block;
  min-width: 0;
  min-height: 7px;
  aspect-ratio: 1 / 1;
  text-align: center;
  font: 700 8px/1 monospace;
  color: #1e160d;
}}
.water {{ background: #4b83a6; }}
.shoal {{ background: #79b7b9; }}
.coast {{ background: #d7c083; }}
.grass {{ background: #8fac62; }}
.dry {{ background: #c38b55; }}
.forest {{ background: #437545; }}
.mountain {{ background: #8d8878; }}
.snow {{ background: #ece7d8; }}
.river {{ background: #4aa6c8; }}
.capital {{ background: #d7a72e; }}
.village {{ background: #d9893d; }}
.ruin {{ background: #b55043; }}
.tower {{ background: #8e6ab8; }}
.oddity {{ background: #bd73b2; }}
.legend {{
  display: flex;
  flex-wrap: wrap;
  gap: 8px 12px;
  margin-top: 12px;
  font-size: 13px;
}}
.legend-title {{
  margin: 12px 0 0;
  font-size: 16px;
}}
.legend-item {{
  display: inline-flex;
  align-items: center;
  gap: 5px;
}}
.swatch {{
  display: inline-grid;
  place-items: center;
  width: 20px;
  height: 20px;
  border: 1px solid rgba(64, 45, 22, 0.55);
  font: 700 11px/1 monospace;
}}
.notes {{
  display: grid;
  gap: 10px;
}}
.notes h2 {{
  margin: 0 0 4px;
  font-size: 24px;
}}
.landmark,
.region {{
  break-inside: avoid;
  border: 1px solid #a78350;
  background: rgba(255, 248, 225, 0.72);
  padding: 10px 12px;
}}
.landmark h3,
.region h3 {{
  margin: 0 0 5px;
  font-size: 17px;
}}
.landmark p,
.region p {{
  margin: 4px 0;
  font-size: 13px;
  line-height: 1.32;
}}
.dm {{
  color: #6d2d28;
}}
@media print {{
  body {{ background: white; }}
  .page {{ padding: 0; max-width: none; }}
  .layout {{ grid-template-columns: 1fr 390px; gap: 12px; }}
}}
"""
