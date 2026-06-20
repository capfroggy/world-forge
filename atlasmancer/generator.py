"""Deterministic ASCII world generation."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import math
import random
from typing import Iterable, Sequence

from .i18n import DEFAULT_LOCALE, LocaleCatalog, load_locale

TERRAIN_KEYS = {
    "~": "terrain.deep_water",
    ",": "terrain.shoals",
    ".": "terrain.coast",
    ";": "terrain.grassland",
    ":": "terrain.drylands",
    "^": "terrain.forest",
    "A": "terrain.mountains",
    "*": "terrain.snow",
    "|": "terrain.river",
}

LAND_REGION_KINDS = {
    ";": "grassland",
    ":": "drylands",
    "^": "forest",
    "A": "mountains",
    "*": "snow",
}
COAST_TILE = "."
LAND_REGION_TILES = set(LAND_REGION_KINDS) | {COAST_TILE}
WATER_TILES = {"~", ","}
MIN_REGION_SIZE = 6
OCEAN_SIZE_THRESHOLD = 80
REGION_KIND_ORDER = ("grassland", "drylands", "forest", "mountains", "snow")
REGION_DESCRIPTION_INDEX = {
    "forest": 0,
    "drylands": 1,
    "grassland": 2,
    "mountains": 3,
    "snow": 4,
}

LANDMARK_KEYS = {
    "C": "landmark.capital",
    "v": "landmark.village",
    "X": "landmark.ruin",
    "T": "landmark.tower",
    "?": "landmark.oddity",
}

TERRAIN_LEGEND = {symbol: load_locale(DEFAULT_LOCALE).t(key) for symbol, key in TERRAIN_KEYS.items()}
LANDMARK_LEGEND = {symbol: load_locale(DEFAULT_LOCALE).t(key) for symbol, key in LANDMARK_KEYS.items()}

ANSI_COLORS = {
    "~": "\033[38;5;25m",
    ",": "\033[38;5;32m",
    ".": "\033[38;5;179m",
    ";": "\033[38;5;106m",
    ":": "\033[38;5;173m",
    "^": "\033[38;5;34m",
    "A": "\033[38;5;244m",
    "*": "\033[38;5;231m",
    "|": "\033[38;5;45m",
    "C": "\033[38;5;220m",
    "v": "\033[38;5;214m",
    "X": "\033[38;5;196m",
    "T": "\033[38;5;141m",
    "?": "\033[38;5;201m",
}

RESET = "\033[0m"

PREFIXES = [
    "Ael",
    "Ash",
    "Bel",
    "Cor",
    "Dun",
    "Eld",
    "Fen",
    "Hal",
    "Iri",
    "Jun",
    "Kai",
    "Lor",
    "Mor",
    "Nor",
    "Ora",
    "Pyr",
    "Rin",
    "Sol",
    "Tor",
    "Vey",
]

SUFFIXES = [
    "barrow",
    "bay",
    "brook",
    "cross",
    "fall",
    "gate",
    "hollow",
    "mere",
    "reach",
    "rest",
    "ridge",
    "run",
    "spire",
    "stone",
    "watch",
    "wick",
]

TITLE_ADJECTIVES = [
    "Amber",
    "Broken",
    "Hidden",
    "Lantern",
    "Moonlit",
    "Salt",
    "Shimmering",
    "Silver",
    "Thorn",
    "Verdant",
]

TITLE_NOUNS = [
    "Archipelago",
    "Crownlands",
    "Expanse",
    "Marches",
    "Reach",
    "Realm",
    "Rim",
    "Wilds",
]

DEFAULT_AUDIENCE = "gm"
AUDIENCES = ("gm", "player")


@dataclass(frozen=True)
class Region:
    """A named natural region detected from contiguous terrain."""

    id: str
    name: str
    kind: str
    tile_count: int
    is_island: bool
    description: str


@dataclass
class _LandComponent:
    kind: str
    tiles: set[tuple[int, int]]
    min_coord: tuple[int, int]


@dataclass
class _RegionDraft:
    tiles: set[tuple[int, int]]
    kind_counts: dict[str, int]
    min_coord: tuple[int, int]
    land_mass_id: int


@dataclass(frozen=True)
class _WaterBody:
    kind: str
    tiles: frozenset[tuple[int, int]]
    tile_count: int
    touches_edge: bool


@dataclass(frozen=True)
class Landmark:
    """A named point of interest placed on the map."""

    id: str
    symbol: str
    name: str
    kind: str
    x: int
    y: int
    rumor: str
    npc: str
    hook: str
    secret: str
    danger: str
    reward: str


@dataclass(frozen=True)
class World:
    """Generated world data plus rendering helpers."""

    seed: str
    world_id: str
    title: str
    width: int
    height: int
    tiles: tuple[str, ...]
    landmarks: tuple[Landmark, ...]
    regions: tuple[Region, ...] = ()
    locale: str = DEFAULT_LOCALE

    def render_plain(self, audience: str = DEFAULT_AUDIENCE) -> str:
        catalog = load_locale(self.locale)
        lines = [self.title, ""]
        lines.extend(self.tiles)
        lines.append("")
        lines.append(legend_text(catalog))
        if self.landmarks:
            lines.append("")
            lines.append(f"{catalog.t('export.landmarks_label')}:")
            for landmark in self.landmarks:
                lines.append(
                    f"- {landmark.symbol} {landmark.name} ({landmark_kind_label(landmark.kind, catalog)}) "
                    f"at {landmark.x},{landmark.y}: {landmark.hook}"
                )
                lines.append(f"  {catalog.t('export.npc_label')}: {landmark.npc}")
                lines.append(f"  {catalog.t('export.rumor_label')}: {landmark.rumor}")
                if audience != "player":
                    lines.append(f"  {catalog.t('export.danger_label')}: {landmark.danger}")
                    lines.append(f"  {catalog.t('export.reward_label')}: {landmark.reward}")
        return "\n".join(lines)

    def render_ansi(self, audience: str = DEFAULT_AUDIENCE) -> str:
        catalog = load_locale(self.locale)
        lines = [self.title, ""]
        for row in self.tiles:
            lines.append("".join(_paint(char) for char in row))
        lines.append("")
        lines.append(legend_text(catalog))
        if self.landmarks:
            lines.append("")
            lines.append(f"{catalog.t('export.landmarks_label')}:")
            for landmark in self.landmarks:
                lines.append(
                    f"- {_paint(landmark.symbol)} {landmark.name} ({landmark_kind_label(landmark.kind, catalog)}) "
                    f"at {landmark.x},{landmark.y}: {landmark.hook}"
                )
                lines.append(f"  {catalog.t('export.npc_label')}: {landmark.npc}")
                lines.append(f"  {catalog.t('export.rumor_label')}: {landmark.rumor}")
                if audience != "player":
                    lines.append(f"  {catalog.t('export.danger_label')}: {landmark.danger}")
                    lines.append(f"  {catalog.t('export.reward_label')}: {landmark.reward}")
        return "\n".join(lines)

    def to_markdown(self, audience: str = DEFAULT_AUDIENCE) -> str:
        catalog = load_locale(self.locale)

        def landmark_block(landmark: Landmark) -> str:
            lines = [
                f"- `{landmark.symbol}` **{landmark.name}** ({landmark_kind_label(landmark.kind, catalog)}) "
                f"at `{landmark.x},{landmark.y}`",
                f"  - {catalog.t('export.hook_label')}: {landmark.hook}",
                f"  - {catalog.t('export.npc_label')}: {landmark.npc}",
                f"  - {catalog.t('export.rumor_label')}: {landmark.rumor}",
            ]
            if audience != "player":
                lines.append(f"  - {catalog.t('export.secret_label')}: {landmark.secret}")
                lines.append(f"  - {catalog.t('export.danger_label')}: {landmark.danger}")
                lines.append(f"  - {catalog.t('export.reward_label')}: {landmark.reward}")
            return "\n".join(lines)

        landmark_lines = "\n".join(landmark_block(landmark) for landmark in self.landmarks)
        if not landmark_lines:
            landmark_lines = "- No landmarks survived the cartographer."

        return "\n".join(
            [
                f"# {self.title}",
                "",
                f"{catalog.t('export.seed_label')}: `{self.seed}`",
                "",
                "```text",
                *self.tiles,
                "```",
                "",
                legend_text(catalog),
                "",
                f"## {catalog.t('export.landmarks_label')}",
                "",
                landmark_lines,
                "",
            ]
        )

    def to_json(self) -> str:
        data = asdict(self)
        data["landmarks"] = [asdict(landmark) for landmark in self.landmarks]
        data["regions"] = [asdict(region) for region in self.regions]
        return json.dumps(data, indent=2, sort_keys=True)


def generate_world(
    seed: str | None = None,
    width: int = 72,
    height: int = 28,
    landmark_count: int = 9,
    locale: str = DEFAULT_LOCALE,
) -> World:
    """Generate a deterministic ASCII world."""

    seed = seed or _random_seed()
    catalog = load_locale(locale)
    width = _clamp(width, 24, 140)
    height = _clamp(height, 12, 60)
    landmark_count = _clamp(landmark_count, 0, 30)

    rng = random.Random(_seed_int(seed, "world"))
    elevation = _field(seed, width, height, "elevation")
    moisture = _field(seed, width, height, "moisture")
    tiles = _terrain(seed, width, height, elevation, moisture)
    regions = _detect_regions(seed, tiles, catalog)
    river_points = _river_points(seed, width, height, elevation, tiles)
    tiles = _overlay(tiles, river_points, "|")
    landmarks = _landmarks(seed, rng, width, height, tiles, landmark_count, catalog)
    tiles = _place_landmarks(tiles, landmarks)

    title = _title(seed, rng)
    return World(
        seed=seed,
        world_id=_world_id(seed),
        title=title,
        width=width,
        height=height,
        tiles=tuple("".join(row) for row in tiles),
        landmarks=tuple(landmarks),
        regions=regions,
        locale=locale,
    )


def _world_id(seed: str) -> str:
    return hashlib.sha1(seed.encode("utf-8")).hexdigest()[:8]


def terrain_legend(catalog: LocaleCatalog | None = None) -> dict[str, str]:
    catalog = catalog or load_locale(DEFAULT_LOCALE)
    return {symbol: catalog.t(key) for symbol, key in TERRAIN_KEYS.items()}


def landmark_legend(catalog: LocaleCatalog | None = None) -> dict[str, str]:
    catalog = catalog or load_locale(DEFAULT_LOCALE)
    return {symbol: catalog.t(key) for symbol, key in LANDMARK_KEYS.items()}


def legend_text(catalog: LocaleCatalog | None = None) -> str:
    catalog = catalog or load_locale(DEFAULT_LOCALE)
    terrain = ", ".join(f"{symbol} {name}" for symbol, name in terrain_legend(catalog).items())
    landmarks = ", ".join(f"{symbol} {name}" for symbol, name in landmark_legend(catalog).items())
    return f"{catalog.t('export.legend_label')}: {terrain}, {landmarks}"


def landmark_kind_label(kind: str, catalog: LocaleCatalog | None = None) -> str:
    catalog = catalog or load_locale(DEFAULT_LOCALE)
    return catalog.t(f"landmark.{kind}")


def _terrain(
    seed: str,
    width: int,
    height: int,
    elevation: list[list[float]],
    moisture: list[list[float]],
) -> list[list[str]]:
    grid: list[list[str]] = []
    aspect = width / max(height, 1)

    for y in range(height):
        row: list[str] = []
        for x in range(width):
            nx = (x / max(width - 1, 1)) * 2 - 1
            ny = (y / max(height - 1, 1)) * 2 - 1
            vertical_weight = min(max(aspect * 0.58, 1.0), 1.85)
            distance = math.sqrt(nx * nx + (ny * vertical_weight) ** 2)
            edge_falloff = distance**1.6
            ridges = _value_noise(seed, x, y, 8.0, "ridges")
            height_value = elevation[y][x] - (edge_falloff * 0.56) + (ridges * 0.13) + 0.03
            wet = moisture[y][x]
            temp = 1.0 - (abs(ny) * 0.42) - (height_value * 0.28)

            if height_value < 0.30:
                char = "~"
            elif height_value < 0.36:
                char = ","
            elif height_value < 0.42:
                char = "."
            elif height_value > 0.78 and temp < 0.48:
                char = "*"
            elif height_value > 0.70:
                char = "A"
            elif wet > 0.62:
                char = "^"
            elif wet < 0.28:
                char = ":"
            else:
                char = ";"
            row.append(char)
        grid.append(row)

    return grid


def _field(seed: str, width: int, height: int, salt: str) -> list[list[float]]:
    rows: list[list[float]] = []
    for y in range(height):
        row = []
        for x in range(width):
            value = (
                _value_noise(seed, x, y, 26.0, salt) * 0.52
                + _value_noise(seed, x, y, 13.0, f"{salt}-middle") * 0.31
                + _value_noise(seed, x, y, 6.0, f"{salt}-detail") * 0.17
            )
            row.append(value)
        rows.append(row)
    return rows


def _detect_regions(seed: str, tiles: Sequence[Sequence[str]], catalog: LocaleCatalog) -> tuple[Region, ...]:
    components, component_by_tile = _land_components(tiles)
    if not components:
        return ()

    mass_by_tile, main_mass_id = _land_mass_ids(tiles)
    drafts: list[_RegionDraft] = []
    component_to_region: dict[int, int] = {}

    for index, component in enumerate(components):
        if len(component.tiles) < MIN_REGION_SIZE:
            continue
        tile = next(iter(component.tiles))
        component_to_region[index] = len(drafts)
        drafts.append(
            _RegionDraft(
                tiles=set(component.tiles),
                kind_counts={component.kind: len(component.tiles)},
                min_coord=component.min_coord,
                land_mass_id=mass_by_tile.get(tile, -1),
            )
        )

    pending = [index for index, component in enumerate(components) if len(component.tiles) < MIN_REGION_SIZE]
    while pending:
        merged = False
        for index in pending[:]:
            candidates = _neighbor_region_indices(components[index].tiles, component_by_tile, component_to_region, tiles)
            if not candidates:
                continue
            region_index = _largest_region(candidates, drafts)
            _merge_component(drafts[region_index], components[index])
            component_to_region[index] = region_index
            pending.remove(index)
            merged = True
        if not merged:
            index = min(pending, key=lambda item: (-len(components[item].tiles), components[item].min_coord))
            component = components[index]
            if drafts:
                region_index = _nearest_region_to_component(component, drafts)
                _merge_component(drafts[region_index], component)
                component_to_region[index] = region_index
            else:
                tile = next(iter(component.tiles))
                component_to_region[index] = len(drafts)
                drafts.append(
                    _RegionDraft(
                        tiles=set(component.tiles),
                        kind_counts={component.kind: len(component.tiles)},
                        min_coord=component.min_coord,
                        land_mass_id=mass_by_tile.get(tile, -1),
                    )
                )
            pending.remove(index)

    _assign_coasts(drafts, tiles)

    regions: list[Region] = []
    used_names: set[str] = set()
    for index, draft in enumerate(sorted(drafts, key=lambda item: item.min_coord), start=1):
        kind = _dominant_region_kind(draft.kind_counts)
        regions.append(
            Region(
                id=f"rg-{index:02d}",
                name=_region_name(seed, index, used_names),
                kind=kind,
                tile_count=len(draft.tiles),
                is_island=draft.land_mass_id != main_mass_id,
                description=catalog.content("regions")[REGION_DESCRIPTION_INDEX[kind]],
            )
        )
    return tuple(regions)


def _land_components(tiles: Sequence[Sequence[str]]) -> tuple[list[_LandComponent], dict[tuple[int, int], int]]:
    height = len(tiles)
    width = len(tiles[0]) if height else 0
    visited: set[tuple[int, int]] = set()
    components: list[_LandComponent] = []
    component_by_tile: dict[tuple[int, int], int] = {}

    for y in range(height):
        for x in range(width):
            if (x, y) in visited or tiles[y][x] not in LAND_REGION_KINDS:
                continue
            symbol = tiles[y][x]
            kind = LAND_REGION_KINDS[symbol]
            stack = [(x, y)]
            visited.add((x, y))
            component_tiles: set[tuple[int, int]] = set()

            while stack:
                cx, cy = stack.pop()
                component_tiles.add((cx, cy))
                for nx, ny in _neighbors(cx, cy, width, height):
                    if (nx, ny) in visited or tiles[ny][nx] != symbol:
                        continue
                    visited.add((nx, ny))
                    stack.append((nx, ny))

            component_index = len(components)
            for tile in component_tiles:
                component_by_tile[tile] = component_index
            components.append(
                _LandComponent(
                    kind=kind,
                    tiles=component_tiles,
                    min_coord=_min_coord(component_tiles),
                )
            )

    return components, component_by_tile


def _land_mass_ids(tiles: Sequence[Sequence[str]]) -> tuple[dict[tuple[int, int], int], int]:
    height = len(tiles)
    width = len(tiles[0]) if height else 0
    visited: set[tuple[int, int]] = set()
    mass_by_tile: dict[tuple[int, int], int] = {}
    mass_sizes: list[int] = []

    for y in range(height):
        for x in range(width):
            if (x, y) in visited or tiles[y][x] not in LAND_REGION_TILES:
                continue
            mass_id = len(mass_sizes)
            stack = [(x, y)]
            visited.add((x, y))
            count = 0
            while stack:
                cx, cy = stack.pop()
                mass_by_tile[(cx, cy)] = mass_id
                count += 1
                for nx, ny in _neighbors(cx, cy, width, height):
                    if (nx, ny) in visited or tiles[ny][nx] not in LAND_REGION_TILES:
                        continue
                    visited.add((nx, ny))
                    stack.append((nx, ny))
            mass_sizes.append(count)

    if not mass_sizes:
        return mass_by_tile, -1
    main_mass_id = max(range(len(mass_sizes)), key=lambda index: (mass_sizes[index], -index))
    return mass_by_tile, main_mass_id


def _classify_water_bodies(tiles: Sequence[Sequence[str]]) -> tuple[_WaterBody, ...]:
    height = len(tiles)
    width = len(tiles[0]) if height else 0
    visited: set[tuple[int, int]] = set()
    bodies: list[_WaterBody] = []

    for y in range(height):
        for x in range(width):
            if (x, y) in visited or tiles[y][x] not in WATER_TILES:
                continue
            stack = [(x, y)]
            visited.add((x, y))
            body_tiles: set[tuple[int, int]] = set()
            touches_edge = False

            while stack:
                cx, cy = stack.pop()
                body_tiles.add((cx, cy))
                touches_edge = touches_edge or _is_edge(cx, cy, width, height)
                for nx, ny in _neighbors(cx, cy, width, height):
                    if (nx, ny) in visited or tiles[ny][nx] not in WATER_TILES:
                        continue
                    visited.add((nx, ny))
                    stack.append((nx, ny))

            kind = "ocean" if touches_edge or len(body_tiles) >= OCEAN_SIZE_THRESHOLD else "lake"
            bodies.append(
                _WaterBody(
                    kind=kind,
                    tiles=frozenset(body_tiles),
                    tile_count=len(body_tiles),
                    touches_edge=touches_edge,
                )
            )

    return tuple(sorted(bodies, key=lambda body: _min_coord(body.tiles)))


def _neighbor_region_indices(
    tiles_to_check: set[tuple[int, int]],
    component_by_tile: dict[tuple[int, int], int],
    component_to_region: dict[int, int],
    tiles: Sequence[Sequence[str]],
) -> set[int]:
    height = len(tiles)
    width = len(tiles[0]) if height else 0
    candidates: set[int] = set()
    for x, y in tiles_to_check:
        for neighbor in _neighbors(x, y, width, height):
            component_index = component_by_tile.get(neighbor)
            if component_index is not None and component_index in component_to_region:
                candidates.add(component_to_region[component_index])
    return candidates


def _largest_region(candidates: set[int], drafts: list[_RegionDraft]) -> int:
    return min(candidates, key=lambda index: (-len(drafts[index].tiles), drafts[index].min_coord))


def _merge_component(draft: _RegionDraft, component: _LandComponent) -> None:
    draft.tiles.update(component.tiles)
    draft.kind_counts[component.kind] = draft.kind_counts.get(component.kind, 0) + len(component.tiles)
    draft.min_coord = min(draft.min_coord, component.min_coord)


def _assign_coasts(drafts: list[_RegionDraft], tiles: Sequence[Sequence[str]]) -> None:
    if not drafts:
        return

    height = len(tiles)
    width = len(tiles[0]) if height else 0
    region_by_tile = {tile: index for index, draft in enumerate(drafts) for tile in draft.tiles}
    pending = [(x, y) for y in range(height) for x in range(width) if tiles[y][x] == COAST_TILE]

    while pending:
        assigned_this_pass = False
        for tile in pending[:]:
            candidates = {
                region_by_tile[neighbor]
                for neighbor in _neighbors(tile[0], tile[1], width, height)
                if neighbor in region_by_tile
            }
            if not candidates:
                continue
            region_index = _largest_region(candidates, drafts)
            _add_coast_tile(drafts[region_index], tile)
            region_by_tile[tile] = region_index
            pending.remove(tile)
            assigned_this_pass = True
        if not assigned_this_pass:
            for tile in pending:
                region_index = _nearest_region(tile, drafts)
                _add_coast_tile(drafts[region_index], tile)
                region_by_tile[tile] = region_index
            pending.clear()


def _add_coast_tile(draft: _RegionDraft, tile: tuple[int, int]) -> None:
    draft.tiles.add(tile)
    draft.min_coord = min(draft.min_coord, (tile[1], tile[0]))


def _nearest_region(tile: tuple[int, int], drafts: list[_RegionDraft]) -> int:
    x, y = tile
    return min(
        range(len(drafts)),
        key=lambda index: (
            min(abs(x - rx) + abs(y - ry) for rx, ry in drafts[index].tiles),
            drafts[index].min_coord,
        ),
    )


def _nearest_region_to_component(component: _LandComponent, drafts: list[_RegionDraft]) -> int:
    return min(
        range(len(drafts)),
        key=lambda index: (
            min(
                abs(cx - rx) + abs(cy - ry)
                for cx, cy in component.tiles
                for rx, ry in drafts[index].tiles
            ),
            -len(drafts[index].tiles),
            drafts[index].min_coord,
        ),
    )


def _dominant_region_kind(kind_counts: dict[str, int]) -> str:
    return min(
        kind_counts,
        key=lambda kind: (-kind_counts[kind], REGION_KIND_ORDER.index(kind)),
    )


def _region_name(seed: str, index: int, used_names: set[str]) -> str:
    rng = random.Random(_seed_int(seed, f"region-name-{index}"))
    for _ in range(len(TITLE_ADJECTIVES) * len(TITLE_NOUNS)):
        name = f"The {rng.choice(TITLE_ADJECTIVES)} {rng.choice(TITLE_NOUNS)}"
        if name not in used_names:
            used_names.add(name)
            return name

    name = f"The {rng.choice(TITLE_ADJECTIVES)} {rng.choice(TITLE_NOUNS)} {index}"
    used_names.add(name)
    return name


def _min_coord(points: Iterable[tuple[int, int]]) -> tuple[int, int]:
    return min((y, x) for x, y in points)


def _river_points(
    seed: str,
    width: int,
    height: int,
    elevation: list[list[float]],
    tiles: list[list[str]],
) -> set[tuple[int, int]]:
    water_tiles = {tile for body in _classify_water_bodies(tiles) for tile in body.tiles}
    candidates = [
        (elevation[y][x], x, y)
        for y in range(2, height - 2)
        for x in range(2, width - 2)
        if tiles[y][x] in {"A", "*", "^", ";"}
    ]
    if not candidates:
        return set()

    candidates.sort(reverse=True)
    rng = random.Random(_seed_int(seed, "rivers"))
    source_count = min(3, max(1, (width * height) // 950))
    selected = _spread_points([(x, y) for _, x, y in candidates[: max(20, source_count * 12)]], source_count, rng)
    rivers: set[tuple[int, int]] = set()

    for source in selected:
        rivers.update(_river_path(source, width, height, elevation, tiles, water_tiles, rng))

    return rivers


def _river_path(
    source: tuple[int, int],
    width: int,
    height: int,
    elevation: list[list[float]],
    tiles: Sequence[Sequence[str]],
    water_tiles: set[tuple[int, int]],
    rng: random.Random,
) -> set[tuple[int, int]]:
    x, y = source
    seen: set[tuple[int, int]] = set()
    path: list[tuple[int, int]] = []

    for _ in range(width + height):
        if (x, y) in water_tiles:
            return set(path)
        if _is_edge(x, y, width, height):
            return set(_append_river_point(path, (x, y), tiles))
        if (x, y) in seen:
            return set(_finish_river_path(path, (x, y), width, height, tiles, water_tiles))

        seen.add((x, y))
        _append_river_point(path, (x, y), tiles)

        neighbors = _neighbors(x, y, width, height)
        if any(neighbor in water_tiles for neighbor in neighbors):
            return set(path)

        unvisited = [point for point in neighbors if point not in seen and point not in water_tiles]
        if not unvisited:
            return set(_finish_river_path(path, (x, y), width, height, tiles, water_tiles))

        x, y = min(
            unvisited,
            key=lambda point: elevation[point[1]][point[0]] + rng.random() * 0.06,
        )

    return set(_finish_river_path(path, (x, y), width, height, tiles, water_tiles))


def _append_river_point(
    path: list[tuple[int, int]],
    point: tuple[int, int],
    tiles: Sequence[Sequence[str]],
) -> list[tuple[int, int]]:
    x, y = point
    if tiles[y][x] not in WATER_TILES and (not path or path[-1] != point):
        path.append(point)
    return path


def _finish_river_path(
    path: list[tuple[int, int]],
    start: tuple[int, int],
    width: int,
    height: int,
    tiles: Sequence[Sequence[str]],
    water_tiles: set[tuple[int, int]],
) -> list[tuple[int, int]]:
    for point in _route_to_water_or_edge(start, width, height, tiles, water_tiles):
        _append_river_point(path, point, tiles)
    return path


def _route_to_water_or_edge(
    start: tuple[int, int],
    width: int,
    height: int,
    tiles: Sequence[Sequence[str]],
    water_tiles: set[tuple[int, int]],
) -> list[tuple[int, int]]:
    queue = [start]
    parents: dict[tuple[int, int], tuple[int, int] | None] = {start: None}

    for point in queue:
        x, y = point
        if _is_edge(x, y, width, height) or any(neighbor in water_tiles for neighbor in _neighbors(x, y, width, height)):
            route: list[tuple[int, int]] = []
            current: tuple[int, int] | None = point
            while current is not None:
                route.append(current)
                current = parents[current]
            return list(reversed(route))

        for neighbor in _neighbors(x, y, width, height):
            if neighbor in parents or neighbor in water_tiles:
                continue
            parents[neighbor] = point
            queue.append(neighbor)

    return [start]


def _landmarks(
    seed: str,
    rng: random.Random,
    width: int,
    height: int,
    tiles: list[list[str]],
    landmark_count: int,
    catalog: LocaleCatalog,
) -> list[Landmark]:
    land = [
        (x, y)
        for y in range(1, height - 1)
        for x in range(1, width - 1)
        if tiles[y][x] in {";", ":", "^", ".", "|"}
    ]
    if not land or landmark_count <= 0:
        return []

    min_distance = max(4, min(width, height) // 5)
    points = _spread_points(land, landmark_count, rng, min_distance=min_distance)
    kinds = [("C", "capital"), ("v", "village"), ("v", "village"), ("X", "ruin"), ("T", "tower"), ("?", "oddity")]
    landmarks: list[Landmark] = []
    used_names: set[str] = set()

    for index, (x, y) in enumerate(points):
        if index == 0:
            symbol, kind = "C", "capital"
        else:
            symbol, kind = rng.choice(kinds[1:])
        name = _unique_place_name(rng, used_names)
        landmarks.append(
            Landmark(
                id=f"lm-{index + 1:02d}",
                symbol=symbol,
                name=name,
                kind=kind,
                x=x,
                y=y,
                rumor=rng.choice(catalog.content("rumors")),
                npc=rng.choice(catalog.content("npcs")),
                hook=rng.choice(catalog.content("hooks")),
                secret=rng.choice(catalog.content("secrets")),
                danger=rng.choice(catalog.content("dangers")),
                reward=rng.choice(catalog.content("rewards")),
            )
        )

    return landmarks


def _spread_points(
    points: list[tuple[int, int]],
    count: int,
    rng: random.Random,
    min_distance: int = 6,
) -> list[tuple[int, int]]:
    shuffled = points[:]
    rng.shuffle(shuffled)
    selected: list[tuple[int, int]] = []

    for point in shuffled:
        if all(_distance(point, existing) >= min_distance for existing in selected):
            selected.append(point)
            if len(selected) >= count:
                return selected

    for point in shuffled:
        if point not in selected:
            selected.append(point)
            if len(selected) >= count:
                break

    return selected


def _place_landmarks(tiles: list[list[str]], landmarks: Iterable[Landmark]) -> list[list[str]]:
    copied = [row[:] for row in tiles]
    for landmark in landmarks:
        copied[landmark.y][landmark.x] = landmark.symbol
    return copied


def _overlay(tiles: list[list[str]], points: set[tuple[int, int]], symbol: str) -> list[list[str]]:
    copied = [row[:] for row in tiles]
    for x, y in points:
        if copied[y][x] not in WATER_TILES:
            copied[y][x] = symbol
    return copied


def _neighbors(x: int, y: int, width: int, height: int) -> list[tuple[int, int]]:
    options = [
        (x - 1, y),
        (x + 1, y),
        (x, y - 1),
        (x, y + 1),
        (x - 1, y - 1),
        (x + 1, y - 1),
        (x - 1, y + 1),
        (x + 1, y + 1),
    ]
    return [(nx, ny) for nx, ny in options if 0 <= nx < width and 0 <= ny < height]


def _is_edge(x: int, y: int, width: int, height: int) -> bool:
    return x == 0 or y == 0 or x == width - 1 or y == height - 1


def _value_noise(seed: str, x: int, y: int, scale: float, salt: str) -> float:
    x0 = math.floor(x / scale)
    y0 = math.floor(y / scale)
    sx = _smooth((x / scale) - x0)
    sy = _smooth((y / scale) - y0)

    n00 = _unit(seed, x0, y0, salt)
    n10 = _unit(seed, x0 + 1, y0, salt)
    n01 = _unit(seed, x0, y0 + 1, salt)
    n11 = _unit(seed, x0 + 1, y0 + 1, salt)

    ix0 = _lerp(n00, n10, sx)
    ix1 = _lerp(n01, n11, sx)
    return _lerp(ix0, ix1, sy)


def _unit(seed: str, x: int, y: int, salt: str) -> float:
    digest = hashlib.blake2b(f"{seed}:{salt}:{x}:{y}".encode(), digest_size=8).digest()
    return int.from_bytes(digest, "big") / ((1 << 64) - 1)


def _seed_int(seed: str, salt: str) -> int:
    digest = hashlib.blake2b(f"{seed}:{salt}".encode(), digest_size=8).digest()
    return int.from_bytes(digest, "big")


def _smooth(value: float) -> float:
    return value * value * (3 - 2 * value)


def _lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def _distance(a: tuple[int, int], b: tuple[int, int]) -> float:
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)


def _title(seed: str, rng: random.Random) -> str:
    adjective = rng.choice(TITLE_ADJECTIVES)
    noun = rng.choice(TITLE_NOUNS)
    name = _place_name(random.Random(_seed_int(seed, "title-name"))).split()[0]
    return f"The {adjective} {noun} of {name}"


def _place_name(rng: random.Random) -> str:
    prefix = rng.choice(PREFIXES)
    suffix = rng.choice(SUFFIXES)
    if rng.random() < 0.32:
        return f"{prefix}{suffix.title()}"
    return f"{prefix} {suffix.title()}"


def _unique_place_name(rng: random.Random, used_names: set[str]) -> str:
    for _ in range(16):
        name = _place_name(rng)
        if name not in used_names:
            used_names.add(name)
            return name

    name = f"{_place_name(rng)} {len(used_names) + 1}"
    used_names.add(name)
    return name


def _random_seed() -> str:
    words = [
        "amber",
        "brine",
        "cinder",
        "drift",
        "ember",
        "fog",
        "lantern",
        "moss",
        "rune",
        "salt",
        "thunder",
        "velvet",
    ]
    rng = random.SystemRandom()
    return f"{rng.choice(words)}-{rng.choice(words)}-{rng.randrange(1000, 9999)}"


def _clamp(value: int, low: int, high: int) -> int:
    return max(low, min(high, value))


def _paint(char: str) -> str:
    return f"{ANSI_COLORS.get(char, '')}{char}{RESET if char in ANSI_COLORS else ''}"
