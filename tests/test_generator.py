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
        self.assertLessEqual(len(payload["landmarks"]), 4)
        self.assertIn("tiles", payload)
        self.assertIn("hook", payload["landmarks"][0])

    def test_markdown_export_is_playable(self):
        world = generate_world(seed="playable", width=36, height=16, landmark_count=2)
        markdown = world.to_markdown()

        self.assertIn("Hook:", markdown)
        self.assertIn("NPC:", markdown)
        self.assertIn("Danger:", markdown)


if __name__ == "__main__":
    unittest.main()
