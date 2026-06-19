"""Deterministic ASCII world generation."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import math
import random
from typing import Iterable


TERRAIN_LEGEND = {
    "~": "deep water",
    ",": "shoals",
    ".": "coast",
    ";": "grassland",
    ":": "drylands",
    "^": "forest",
    "A": "mountains",
    "*": "snow",
    "|": "river",
}

LANDMARK_LEGEND = {
    "C": "capital",
    "v": "village",
    "X": "ruin",
    "T": "tower",
    "?": "oddity",
}

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

ODD_RUMORS = [
    "The wells hum after midnight.",
    "Nobody agrees where the oldest road begins.",
    "A bell rings under the hills when fog arrives.",
    "Cartographers keep losing the same peninsula.",
    "The birds here migrate in perfect squares.",
    "Every seventh bridge is older than the river.",
]

NPCS = [
    "a tired caravan master with a perfect memory for roads",
    "a river priest who collects forbidden maps",
    "a masked captain looking for a missing heir",
    "a cheerful innkeeper who hears too much",
    "a disgraced knight guarding an unpaid debt",
    "a young astronomer tracking an impossible star",
    "a scarred hunter who knows the old paths",
    "a quiet scribe carrying a sealed royal order",
]

HOOKS = [
    "A patron offers coin for proof that the old stories are true.",
    "Travelers vanished after following lights beyond the road.",
    "A local leader needs neutral outsiders before a feud turns violent.",
    "A sealed door has opened for the first time in a century.",
    "Someone is buying maps of this place and burning every copy.",
    "The next full moon will reveal a path that normally is not there.",
    "A caravan arrived with no drivers and cargo from a ruined age.",
    "The place is peaceful, but every child has drawn the same monster.",
]

SECRETS = [
    "The ruler here is protecting an enemy spy.",
    "The landmark is built on older stone from a lost empire.",
    "A nearby spring is slowly changing anyone who drinks from it.",
    "The local legend is false, but the cover-up is worse.",
    "A hidden tunnel connects this place to another marked location.",
    "The treasure everyone seeks is actually a prison key.",
    "One landmark on the map does not exist unless it is being watched.",
    "The oldest family in town serves something under the hills.",
]

DANGERS = [
    "bandits with military discipline",
    "restless dead that follow spoken names",
    "a territorial beast drawn to metal",
    "sinkholes hidden beneath moss and flowers",
    "raiders using old border tunnels",
    "a curse that makes compasses lie",
    "poisonous fog rolling in from low ground",
    "a noble house willing to start a war quietly",
]

REWARDS = [
    "a safe route through hostile terrain",
    "a minor magic item with a useful flaw",
    "an alliance with a local faction",
    "a chest of old coins and newer blackmail",
    "the true name of a dangerous spirit",
    "maps to another forgotten site",
    "a loyal guide who knows the wilderness",
    "a legal claim to land nobody wants yet",
]


@dataclass(frozen=True)
class Landmark:
    """A named point of interest placed on the map."""

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
    title: str
    width: int
    height: int
    tiles: tuple[str, ...]
    landmarks: tuple[Landmark, ...]

    def render_plain(self) -> str:
        lines = [self.title, ""]
        lines.extend(self.tiles)
        lines.append("")
        lines.append(legend_text())
        if self.landmarks:
            lines.append("")
            lines.append("Landmarks:")
            for landmark in self.landmarks:
                lines.append(
                    f"- {landmark.symbol} {landmark.name} ({landmark.kind}) "
                    f"at {landmark.x},{landmark.y}: {landmark.hook}"
                )
                lines.append(f"  NPC: {landmark.npc}")
                lines.append(f"  Rumor: {landmark.rumor}")
                lines.append(f"  Danger: {landmark.danger}")
                lines.append(f"  Reward: {landmark.reward}")
        return "\n".join(lines)

    def render_ansi(self) -> str:
        lines = [self.title, ""]
        for row in self.tiles:
            lines.append("".join(_paint(char) for char in row))
        lines.append("")
        lines.append(legend_text())
        if self.landmarks:
            lines.append("")
            lines.append("Landmarks:")
            for landmark in self.landmarks:
                lines.append(
                    f"- {_paint(landmark.symbol)} {landmark.name} ({landmark.kind}) "
                    f"at {landmark.x},{landmark.y}: {landmark.hook}"
                )
                lines.append(f"  NPC: {landmark.npc}")
                lines.append(f"  Rumor: {landmark.rumor}")
                lines.append(f"  Danger: {landmark.danger}")
                lines.append(f"  Reward: {landmark.reward}")
        return "\n".join(lines)

    def to_markdown(self) -> str:
        landmark_lines = "\n".join(
            (
                f"- `{landmark.symbol}` **{landmark.name}** ({landmark.kind}) "
                f"at `{landmark.x},{landmark.y}`\n"
                f"  - Hook: {landmark.hook}\n"
                f"  - NPC: {landmark.npc}\n"
                f"  - Rumor: {landmark.rumor}\n"
                f"  - Secret: {landmark.secret}\n"
                f"  - Danger: {landmark.danger}\n"
                f"  - Reward: {landmark.reward}"
            )
            for landmark in self.landmarks
        )
        if not landmark_lines:
            landmark_lines = "- No landmarks survived the cartographer."

        return "\n".join(
            [
                f"# {self.title}",
                "",
                f"Seed: `{self.seed}`",
                "",
                "```text",
                *self.tiles,
                "```",
                "",
                legend_text(),
                "",
                "## Landmarks",
                "",
                landmark_lines,
                "",
            ]
        )

    def to_json(self) -> str:
        data = asdict(self)
        data["landmarks"] = [asdict(landmark) for landmark in self.landmarks]
        return json.dumps(data, indent=2, sort_keys=True)


def generate_world(
    seed: str | None = None,
    width: int = 72,
    height: int = 28,
    landmark_count: int = 9,
) -> World:
    """Generate a deterministic ASCII world."""

    seed = seed or _random_seed()
    width = _clamp(width, 24, 140)
    height = _clamp(height, 12, 60)
    landmark_count = _clamp(landmark_count, 0, 30)

    rng = random.Random(_seed_int(seed, "world"))
    elevation = _field(seed, width, height, "elevation")
    moisture = _field(seed, width, height, "moisture")
    tiles = _terrain(seed, width, height, elevation, moisture)
    river_points = _river_points(seed, width, height, elevation, tiles)
    tiles = _overlay(tiles, river_points, "|")
    landmarks = _landmarks(seed, rng, width, height, tiles, landmark_count)
    tiles = _place_landmarks(tiles, landmarks)

    title = _title(seed, rng)
    return World(
        seed=seed,
        title=title,
        width=width,
        height=height,
        tiles=tuple("".join(row) for row in tiles),
        landmarks=tuple(landmarks),
    )


def legend_text() -> str:
    terrain = ", ".join(f"{symbol} {name}" for symbol, name in TERRAIN_LEGEND.items())
    landmarks = ", ".join(f"{symbol} {name}" for symbol, name in LANDMARK_LEGEND.items())
    return f"Legend: {terrain}, {landmarks}"


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


def _river_points(
    seed: str,
    width: int,
    height: int,
    elevation: list[list[float]],
    tiles: list[list[str]],
) -> set[tuple[int, int]]:
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
        x, y = source
        seen: set[tuple[int, int]] = set()
        for _ in range(width + height):
            if not (0 <= x < width and 0 <= y < height) or (x, y) in seen:
                break
            seen.add((x, y))
            if tiles[y][x] in {"~", ","}:
                break
            if tiles[y][x] not in {"A", "*"}:
                rivers.add((x, y))

            neighbors = _neighbors(x, y, width, height)
            water = [(nx, ny) for nx, ny in neighbors if tiles[ny][nx] in {"~", ","}]
            if water:
                x, y = rng.choice(water)
                continue

            x, y = min(
                neighbors,
                key=lambda point: elevation[point[1]][point[0]]
                + rng.random() * 0.06
                + (0.03 if point in seen else 0),
            )

    return rivers


def _landmarks(
    seed: str,
    rng: random.Random,
    width: int,
    height: int,
    tiles: list[list[str]],
    landmark_count: int,
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
                symbol=symbol,
                name=name,
                kind=kind,
                x=x,
                y=y,
                rumor=rng.choice(ODD_RUMORS),
                npc=rng.choice(NPCS),
                hook=rng.choice(HOOKS),
                secret=rng.choice(SECRETS),
                danger=rng.choice(DANGERS),
                reward=rng.choice(REWARDS),
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
        if copied[y][x] not in {"~", ",", "A", "*"}:
            copied[y][x] = symbol
    return copied


def _neighbors(x: int, y: int, width: int, height: int) -> list[tuple[int, int]]:
    options = [
        (x - 1, y),
        (x + 1, y),
        (x, y - 1),
        (x, y + 1),
        (x - 1, y + 1),
        (x + 1, y + 1),
    ]
    return [(nx, ny) for nx, ny in options if 0 <= nx < width and 0 <= ny < height]


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
