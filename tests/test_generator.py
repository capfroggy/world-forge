import json
import unittest

from atlasmancer import generate_world


class GenerateWorldTests(unittest.TestCase):
    def test_same_seed_is_deterministic(self):
        first = generate_world(seed="ember-reef", width=40, height=16)
        second = generate_world(seed="ember-reef", width=40, height=16)

        self.assertEqual(first.tiles, second.tiles)
        self.assertEqual(first.landmarks, second.landmarks)
        self.assertEqual(first.title, second.title)

    def test_world_dimensions_are_respected(self):
        world = generate_world(seed="small", width=32, height=14)

        self.assertEqual(world.width, 32)
        self.assertEqual(world.height, 14)
        self.assertEqual(len(world.tiles), 14)
        self.assertTrue(all(len(row) == 32 for row in world.tiles))

    def test_json_export_contains_landmarks(self):
        world = generate_world(seed="json", width=36, height=16, landmark_count=4)
        payload = json.loads(world.to_json())

        self.assertEqual(payload["seed"], "json")
        self.assertLessEqual(len(payload["landmarks"]), 4 + len(payload["countries"]))
        self.assertIn("tiles", payload)
        self.assertIn("hook", payload["landmarks"][0])

    def test_markdown_export_is_playable(self):
        world = generate_world(seed="playable", width=36, height=16, landmark_count=2)
        markdown = world.to_markdown()

        self.assertIn("Hook:", markdown)
        self.assertIn("NPC:", markdown)
        self.assertIn("Danger:", markdown)

    def test_markdown_export_lists_regions(self):
        world = generate_world(seed="regions-markdown", width=72, height=28, landmark_count=2)
        markdown = world.to_markdown()

        self.assertIn("## Regions", markdown)
        self.assertIn(world.regions[0].name, markdown)
        self.assertIn(world.regions[0].description, markdown)

    def test_player_audience_hides_gm_only_fields(self):
        world = generate_world(seed="playable", width=36, height=16, landmark_count=2)

        markdown = world.to_markdown(audience="player")
        self.assertIn("Hook:", markdown)
        self.assertIn("NPC:", markdown)
        self.assertNotIn("Secret:", markdown)
        self.assertNotIn("Danger:", markdown)
        self.assertNotIn("Reward:", markdown)

        plain = world.render_plain(audience="player")
        self.assertNotIn("Danger:", plain)
        self.assertNotIn("Reward:", plain)

        ansi = world.render_ansi(audience="player")
        self.assertNotIn("Danger:", ansi)
        self.assertNotIn("Reward:", ansi)

    def test_gm_audience_keeps_full_detail_by_default(self):
        world = generate_world(seed="playable", width=36, height=16, landmark_count=2)

        self.assertIn("Secret:", world.to_markdown())
        self.assertIn("Danger:", world.render_plain())
        self.assertIn("Reward:", world.render_ansi())

    def test_landmarks_have_stable_unique_ids(self):
        world = generate_world(seed="ids", width=36, height=16, landmark_count=5)

        ids = [landmark.id for landmark in world.landmarks]
        self.assertEqual(ids, [f"lm-{index + 1:02d}" for index in range(len(world.landmarks))])
        self.assertEqual(len(ids), len(set(ids)))


if __name__ == "__main__":
    unittest.main()
