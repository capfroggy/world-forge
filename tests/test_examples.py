import json
import tempfile
import unittest
from pathlib import Path

from scripts.build_examples import EXAMPLE_OUTPUTS, build_examples


class ExampleBuildTests(unittest.TestCase):
    def test_build_examples_creates_expected_exports(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp)
            generated = build_examples(output_dir)

            expected_names = {filename for filename, _, _, _ in EXAMPLE_OUTPUTS}
            self.assertEqual({path.name for path in generated}, expected_names)

            for path in generated:
                self.assertTrue(path.exists(), path)
                self.assertGreater(path.stat().st_size, 100, path)

            campaign = json.loads((output_dir / "example-campaign.json").read_text(encoding="utf-8"))
            self.assertEqual(campaign["meta"]["seed"], "atlasmancer-sample")
            self.assertEqual(campaign["meta"]["audience"], "gm")
            self.assertTrue(all("gm" in landmark for landmark in campaign["landmarks"]))

            en_player = (output_dir / "example-en-player.html").read_text(encoding="utf-8")
            es_player = (output_dir / "example-es-player.html").read_text(encoding="utf-8")

            for label in ("Secret", "Danger", "Reward"):
                self.assertNotIn(label, en_player)
            for label in ("Secreto", "Peligro", "Recompensa"):
                self.assertNotIn(label, es_player)


if __name__ == "__main__":
    unittest.main()
