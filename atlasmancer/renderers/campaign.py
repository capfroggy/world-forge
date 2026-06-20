"""Canonical, versioned campaign.json exporter."""

from __future__ import annotations

from datetime import datetime, timezone
import json

from atlasmancer import __version__ as GENERATOR_VERSION
from atlasmancer.generator import LANDMARK_KEYS, TERRAIN_KEYS, World

SCHEMA_VERSION = "0.4.0"
GENERATOR_NAME = "atlasmancer"

RESERVED_FOR = {
    "countries": "v0.5 Civilizations",
    "factions": "v0.6 Playable Content",
    "quests": "v0.6 Playable Content",
    "dungeons": "v0.8 Dungeons & Tactical Maps",
}


def build_campaign(world: World, audience: str = "gm") -> dict:
    """Build the campaign.json payload as a plain dict."""

    legend = {**TERRAIN_KEYS, **LANDMARK_KEYS}

    landmarks = []
    for landmark in world.landmarks:
        entry = {
            "id": landmark.id,
            "symbol": landmark.symbol,
            "kind": landmark.kind,
            "name": landmark.name,
            "x": landmark.x,
            "y": landmark.y,
            "public": {
                "hook": landmark.hook,
                "rumor": landmark.rumor,
                "npc": landmark.npc,
            },
        }
        if audience != "player":
            entry["gm"] = {
                "secret": landmark.secret,
                "danger": landmark.danger,
                "reward": landmark.reward,
            }
        landmarks.append(entry)

    regions = [
        {
            "id": region.id,
            "name": region.name,
            "kind": region.kind,
            "tile_count": region.tile_count,
            "is_island": region.is_island,
            "description": region.description,
        }
        for region in world.regions
    ]

    return {
        "meta": {
            "schema_version": SCHEMA_VERSION,
            "generator": GENERATOR_NAME,
            "generator_version": GENERATOR_VERSION,
            "world_id": world.world_id,
            "seed": world.seed,
            "locale": world.locale,
            "audience": audience,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "params": {
                "width": world.width,
                "height": world.height,
                "landmark_count": len(world.landmarks),
            },
        },
        "title": world.title,
        "map": {
            "width": world.width,
            "height": world.height,
            "legend": legend,
            "ascii": list(world.tiles),
        },
        "landmarks": landmarks,
        "regions": regions,
        "countries": [],
        "factions": [],
        "quests": [],
        "dungeons": [],
        "reserved_for": RESERVED_FOR,
    }


def render_campaign(world: World, audience: str = "gm") -> str:
    """Render the canonical campaign.json export."""

    return json.dumps(build_campaign(world, audience=audience), indent=2)
