import unittest

from atlasmancer import generate_world
from atlasmancer.generator import (
    MIN_COUNTRY_LAND_TILES,
    _country_ids_by_land_mass,
    _detect_region_data,
    _field,
    _land_mass_ids,
    _terrain,
)
from atlasmancer.i18n import load_locale


class CivilizationTests(unittest.TestCase):
    def test_countries_are_deterministic_for_same_seed(self):
        first = generate_world(seed="civilization-determinism", width=72, height=28, landmark_count=5)
        second = generate_world(seed="civilization-determinism", width=72, height=28, landmark_count=5)

        self.assertTrue(first.countries)
        self.assertEqual(first.countries, second.countries)
        self.assertEqual(
            [(landmark.id, landmark.name, landmark.x, landmark.y) for landmark in first.landmarks if landmark.kind == "capital"],
            [(landmark.id, landmark.name, landmark.x, landmark.y) for landmark in second.landmarks if landmark.kind == "capital"],
        )

    def test_small_land_masses_do_not_get_countries(self):
        tiles = [
            "~~~~~~~~~~~~",
            "~;;;;~~~~~~~",
            "~;;;;~~~~~~~",
            "~;;;;~~~~AA~",
            "~;;;;~~~~~~~",
            "~;;;;~~~~~~~",
            "~~~~~~~~~~~~",
        ]
        mass_by_tile, main_mass_id = _land_mass_ids(tiles)
        country_by_mass = _country_ids_by_land_mass(mass_by_tile)
        region_data = _detect_region_data(
            "country-threshold",
            tiles,
            load_locale("en"),
            country_by_mass=country_by_mass,
            mass_by_tile=mass_by_tile,
            main_mass_id=main_mass_id,
        )

        self.assertEqual(MIN_COUNTRY_LAND_TILES, 20)
        self.assertEqual(set(country_by_mass.values()), {"co-01"})

        by_kind = {region.kind: region for region in region_data.regions}
        self.assertEqual(by_kind["grassland"].country_id, "co-01")
        self.assertIsNone(by_kind["mountains"].country_id)

    def test_landmarks_zero_still_places_country_capitals(self):
        world = generate_world(seed="capital-without-decor", width=72, height=28, landmark_count=0)

        self.assertTrue(world.countries)
        self.assertEqual(len(world.landmarks), len(world.countries))
        self.assertTrue(all(landmark.kind == "capital" for landmark in world.landmarks))

        capital_ids = {landmark.id for landmark in world.landmarks}
        self.assertEqual({country.capital_landmark_id for country in world.countries}, capital_ids)

    def test_country_fields_and_region_ids_are_populated(self):
        world = generate_world(seed="country-fields", width=72, height=28, landmark_count=4)

        self.assertTrue(world.countries)
        region_ids = {region.id for region in world.regions}
        capital_by_id = {landmark.id: landmark for landmark in world.landmarks if landmark.kind == "capital"}

        for country in world.countries:
            self.assertTrue(country.name)
            self.assertTrue(country.government)
            self.assertTrue(country.resource)
            self.assertTrue(country.current_crisis)
            self.assertIn(country.capital_landmark_id, capital_by_id)
            self.assertEqual(capital_by_id[country.capital_landmark_id].country_id, country.id)
            self.assertTrue(country.region_ids)
            self.assertTrue(set(country.region_ids) <= region_ids)

    def test_landmark_country_id_matches_region_country_id(self):
        world = generate_world(seed="landmark-country", width=72, height=28, landmark_count=8)
        region_data = _region_data_for_world(world)
        country_by_region = {region.id: region.country_id for region in region_data.regions}

        for landmark in world.landmarks:
            region_id = region_data.region_by_tile[(landmark.x, landmark.y)]
            self.assertEqual(landmark.country_id, country_by_region[region_id])

    def test_country_text_respects_locale(self):
        world = generate_world(seed="country-locale", width=72, height=28, landmark_count=4, locale="es")
        es = load_locale("es")
        en = load_locale("en")

        self.assertTrue(world.countries)
        for country in world.countries:
            self.assertIn(country.government, es.content("governments"))
            self.assertIn(country.current_crisis, es.content("crises"))
            self.assertIn(country.resource, es.content("resources"))
            self.assertNotIn(country.government, en.content("governments"))
            self.assertNotIn(country.current_crisis, en.content("crises"))
            self.assertNotIn(country.resource, en.content("resources"))


def _region_data_for_world(world):
    elevation = _field(world.seed, world.width, world.height, "elevation")
    moisture = _field(world.seed, world.width, world.height, "moisture")
    tiles = _terrain(world.seed, world.width, world.height, elevation, moisture)
    mass_by_tile, main_mass_id = _land_mass_ids(tiles)
    country_by_mass = _country_ids_by_land_mass(mass_by_tile)
    return _detect_region_data(
        world.seed,
        tiles,
        load_locale(world.locale),
        country_by_mass=country_by_mass,
        mass_by_tile=mass_by_tile,
        main_mass_id=main_mass_id,
    )


if __name__ == "__main__":
    unittest.main()
