import tempfile
import unittest
from pathlib import Path

from atlasmancer import generate_world
from atlasmancer.cli import main
from atlasmancer.renderers.html import render_html


class RendererTests(unittest.TestCase):
    def test_html_renderer_is_printable_atlas(self):
        world = generate_world(seed="atlas", width=36, height=16, landmark_count=3)
        html = render_html(world)

        self.assertIn("<!doctype html>", html)
        self.assertIn("Printable GM atlas", html)
        self.assertIn("Regions", html)
        self.assertIn("Landmarks", html)
        self.assertIn(world.regions[0].name, html)
        self.assertIn("Secret", html)

    def test_html_renderer_uses_spanish_locale(self):
        world = generate_world(seed="atlas", width=36, height=16, landmark_count=3, locale="es")
        html = render_html(world)

        self.assertIn('<html lang="es">', html)
        self.assertIn("Lugares destacados", html)
        self.assertIn("Leyenda", html)

    def test_html_renderer_hides_gm_secrets_for_player_audience(self):
        world = generate_world(seed="atlas", width=36, height=16, landmark_count=3)
        html = render_html(world, audience="player")

        self.assertNotIn("Secret", html)
        self.assertNotIn("Danger", html)
        self.assertNotIn("Reward", html)
        self.assertIn("Player-safe copy", html)

    def test_cli_writes_html(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "world.html"
            result = main(["--seed", "html", "--format", "html", "--output", str(output)])

            self.assertEqual(result, 0)
            self.assertIn("Landmarks", output.read_text(encoding="utf-8"))

    def test_cli_writes_png_when_pillow_is_installed(self):
        try:
            import PIL  # noqa: F401
        except ImportError:
            self.skipTest("Pillow is not installed")

        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "world.png"
            result = main(
                [
                    "--seed",
                    "png",
                    "--width",
                    "32",
                    "--height",
                    "14",
                    "--format",
                    "png",
                    "--output",
                    str(output),
                    "--tile-size",
                    "8",
                ]
            )

            self.assertEqual(result, 0)
            self.assertGreater(output.stat().st_size, 1000)

    def test_cli_writes_player_safe_png_when_pillow_is_installed(self):
        try:
            import PIL  # noqa: F401
        except ImportError:
            self.skipTest("Pillow is not installed")

        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "world-player.png"
            result = main(
                [
                    "--seed",
                    "png-player",
                    "--width",
                    "32",
                    "--height",
                    "14",
                    "--format",
                    "png",
                    "--audience",
                    "player",
                    "--output",
                    str(output),
                    "--tile-size",
                    "8",
                ]
            )

            self.assertEqual(result, 0)
            self.assertGreater(output.stat().st_size, 1000)
