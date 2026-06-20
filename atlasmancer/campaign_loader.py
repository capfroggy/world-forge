"""Load saved campaign.json files back into World objects."""

from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path
from typing import Any

from .generator import Landmark, Region, World
from .i18n import DEFAULT_LOCALE, load_locale

SUPPORTED_SCHEMA_VERSIONS = ("0.2.0", "0.3.0", "0.4.0")

_CONTENT_FIELDS = {
    "hook": "hooks",
    "npc": "npcs",
    "rumor": "rumors",
    "secret": "secrets",
    "danger": "dangers",
    "reward": "rewards",
}


class CampaignLoadError(ValueError):
    """Raised when a saved campaign cannot be reopened safely."""


def load_campaign(path: str | Path, locale: str = DEFAULT_LOCALE) -> World:
    """Load a campaign.json file and reconstruct its World exactly."""

    catalog = load_locale(locale)
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    meta = _mapping(payload["meta"])
    schema_version = str(meta.get("schema_version", ""))

    if schema_version not in SUPPORTED_SCHEMA_VERSIONS:
        raise CampaignLoadError(
            catalog.t(
                "cli.errors.unsupported_schema_version",
                version=schema_version,
                supported=", ".join(SUPPORTED_SCHEMA_VERSIONS),
            )
        )

    map_data = _mapping(payload["map"])
    landmarks = tuple(_landmark_from_payload(entry, catalog) for entry in payload["landmarks"])
    regions = tuple(_region_from_payload(entry) for entry in payload.get("regions", []))

    return World(
        seed=str(meta["seed"]),
        world_id=str(meta["world_id"]),
        title=str(payload["title"]),
        width=int(map_data["width"]),
        height=int(map_data["height"]),
        tiles=tuple(str(row) for row in map_data["ascii"]),
        landmarks=landmarks,
        regions=regions,
        locale=str(meta.get("locale", DEFAULT_LOCALE)),
    )


def localize_world(world: World, locale: str) -> World:
    """Return a copy of a saved World with stock content translated by locale."""

    if locale == world.locale:
        return world

    source_catalog = load_locale(world.locale)
    target_catalog = load_locale(locale)
    translated_landmarks = []

    for landmark in world.landmarks:
        updates = {
            field: _translate_content(
                getattr(landmark, field),
                source_catalog.content(pool),
                target_catalog.content(pool),
            )
            for field, pool in _CONTENT_FIELDS.items()
        }
        translated_landmarks.append(replace(landmark, **updates))

    translated_regions = tuple(
        replace(
            region,
            description=_translate_content(
                region.description,
                source_catalog.content("regions"),
                target_catalog.content("regions"),
            ),
        )
        for region in world.regions
    )

    return replace(world, locale=locale, landmarks=tuple(translated_landmarks), regions=translated_regions)


def _landmark_from_payload(entry: Any, catalog) -> Landmark:
    data = _mapping(entry)
    public = _mapping(data["public"])
    gm = data.get("gm")

    if not isinstance(gm, dict) or any(key not in gm for key in ("secret", "danger", "reward")):
        raise CampaignLoadError(catalog.t("cli.errors.campaign_missing_gm_data"))

    return Landmark(
        id=str(data["id"]),
        symbol=str(data["symbol"]),
        name=str(data["name"]),
        kind=str(data["kind"]),
        x=int(data["x"]),
        y=int(data["y"]),
        hook=str(public["hook"]),
        rumor=str(public["rumor"]),
        npc=str(public["npc"]),
        secret=str(gm["secret"]),
        danger=str(gm["danger"]),
        reward=str(gm["reward"]),
    )


def _region_from_payload(entry: Any) -> Region:
    data = _mapping(entry)
    return Region(
        id=str(data["id"]),
        name=str(data["name"]),
        kind=str(data["kind"]),
        tile_count=int(data["tile_count"]),
        is_island=bool(data["is_island"]),
        description=str(data["description"]),
    )


def _translate_content(value: str, source_values: list[str], target_values: list[str]) -> str:
    try:
        index = source_values.index(value)
    except ValueError:
        return value
    return target_values[index]


def _mapping(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise TypeError("Expected a JSON object")
    return value
