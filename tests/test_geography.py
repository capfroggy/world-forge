import unittest

from atlasmancer import generate_world
from atlasmancer.generator import (
    LAND_REGION_TILES,
    MIN_REGION_SIZE,
    WATER_TILES,
    _classify_water_bodies,
    _detect_regions,
    _field,
    _is_edge,
    _neighbors,
    _river_points,
    _terrain,
)
from atlasmancer.i18n import load_locale


class GeographyTests(unittest.TestCase):
    def test_regions_are_deterministic_for_same_seed(self):
        first = generate_world(seed="geography-determinism", width=72, height=28)
        second = generate_world(seed="geography-determinism", width=72, height=28)

        self.assertTrue(first.regions)
        self.assertEqual(first.regions, second.regions)
        self.assertEqual([region.id for region in first.regions], [f"rg-{index + 1:02d}" for index in range(len(first.regions))])

    def test_small_components_and_coast_are_merged_into_neighbor_region(self):
        tiles = [
            "~~~~~~~~~",
            "~;;;::..~",
            "~;;;::..~",
            "~;;;....~",
            "~~~~~~~~~",
        ]

        regions = _detect_regions("merge-small", tiles, load_locale("en"))
        land_tile_count = sum(1 for row in tiles for tile in row if tile in LAND_REGION_TILES)

        self.assertEqual(sum(region.tile_count for region in regions), land_tile_count)
        self.assertEqual(len(regions), 1)
        self.assertEqual(regions[0].kind, "grassland")
        self.assertGreaterEqual(regions[0].tile_count, MIN_REGION_SIZE)

    def test_water_bodies_classify_ocean_and_lake(self):
        tiles = [
            "~~~~~~~~~",
            "~;;;;;;;~",
            "~;~~;;;;~",
            "~;~~;;;;~",
            "~;;;;;;;~",
            "~~~~~~~~~",
        ]

        bodies = _classify_water_bodies(tiles)
        lakes = [body for body in bodies if body.kind == "lake"]
        oceans = [body for body in bodies if body.kind == "ocean"]

        self.assertTrue(oceans)
        self.assertEqual(len(lakes), 1)
        self.assertEqual(lakes[0].tile_count, 4)
        self.assertFalse(lakes[0].touches_edge)

    def test_separate_land_mass_is_marked_as_island(self):
        tiles = [
            "~~~~~~~~~~~",
            "~;;;;~~~~~~",
            "~;;;;~~^^^~",
            "~;;;;~~^^^~",
            "~~~~~~~~~~~",
        ]

        regions = _detect_regions("island", tiles, load_locale("en"))
        by_kind = {region.kind: region for region in regions}

        self.assertFalse(by_kind["grassland"].is_island)
        self.assertTrue(by_kind["forest"].is_island)

    def test_region_descriptions_respect_locale(self):
        world = generate_world(seed="region-locale", width=72, height=28, locale="es")
        spanish_descriptions = set(load_locale("es").content("regions"))
        english_descriptions = set(load_locale("en").content("regions"))

        self.assertTrue(world.regions)
        self.assertTrue(all(region.description in spanish_descriptions for region in world.regions))
        self.assertTrue(all(region.description not in english_descriptions for region in world.regions))

    def test_rivers_reach_water_or_map_edge(self):
        for index in range(25):
            seed = f"river-continuity-{index}"
            width = 72
            height = 28
            elevation = _field(seed, width, height, "elevation")
            moisture = _field(seed, width, height, "moisture")
            tiles = _terrain(seed, width, height, elevation, moisture)
            rivers = _river_points(seed, width, height, elevation, tiles)

            for component in _river_components(rivers, width, height):
                self.assertTrue(
                    _component_reaches_water_or_edge(component, tiles, width, height),
                    f"{seed} has a river component without water or edge contact: {component}",
                )


def _river_components(rivers: set[tuple[int, int]], width: int, height: int) -> list[set[tuple[int, int]]]:
    pending = set(rivers)
    components: list[set[tuple[int, int]]] = []

    while pending:
        start = min(pending, key=lambda point: (point[1], point[0]))
        stack = [start]
        pending.remove(start)
        component = {start}

        while stack:
            x, y = stack.pop()
            for neighbor in _neighbors(x, y, width, height):
                if neighbor not in pending:
                    continue
                pending.remove(neighbor)
                component.add(neighbor)
                stack.append(neighbor)

        components.append(component)

    return components


def _component_reaches_water_or_edge(
    component: set[tuple[int, int]],
    tiles: list[list[str]],
    width: int,
    height: int,
) -> bool:
    return any(
        _is_edge(x, y, width, height)
        or any(tiles[ny][nx] in WATER_TILES for nx, ny in _neighbors(x, y, width, height))
        for x, y in component
    )


if __name__ == "__main__":
    unittest.main()
