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
        self.assertIn("Session Places", html)
        self.assertIn("DM secret", html)

    def test_cli_writes_html(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "world.html"
            result = main(["--seed", "html", "--format", "html", "--output", str(output)])

            self.assertEqual(result, 0)
            self.assertIn("Session Places", output.read_text(encoding="utf-8"))

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
