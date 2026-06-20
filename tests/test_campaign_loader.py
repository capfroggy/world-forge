import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import replace
from io import StringIO
from pathlib import Path

from atlasmancer import generate_world
from atlasmancer.campaign_loader import CampaignLoadError, load_campaign, localize_world
from atlasmancer.cli import main
from atlasmancer.renderers.campaign import build_campaign, render_campaign


class CampaignLoaderTests(unittest.TestCase):
    def test_round_trip_reconstructs_original_world_field_by_field(self):
        original = generate_world(seed="round-trip", width=40, height=18, landmark_count=5, locale="en")

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "round-trip.campaign.json"
            path.write_text(render_campaign(original), encoding="utf-8")

            reopened = load_campaign(path)

        self.assertEqual(reopened, replace(original, regions=()))

    def test_v0_2_schema_is_still_supported(self):
        original = generate_world(seed="v0-2-save", width=40, height=18, landmark_count=5, locale="en")
        payload = build_campaign(original)
        payload["meta"]["schema_version"] = "0.2.0"

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "old-save.campaign.json"
            path.write_text(json.dumps(payload), encoding="utf-8")

            reopened = load_campaign(path)

        self.assertEqual(reopened, replace(original, regions=()))

    def test_player_safe_campaign_cannot_be_reopened_as_master(self):
        world = generate_world(seed="player-safe-save", width=36, height=16, landmark_count=3)
        payload = build_campaign(world, audience="player")

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "player.campaign.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            error = StringIO()

            with redirect_stderr(error), self.assertRaises(SystemExit):
                main(["--open", str(path), "--locale", "es", "--format", "plain"])

        self.assertIn("no tiene datos de DM", error.getvalue())

    def test_loader_reports_missing_gm_data_without_raw_exception(self):
        world = generate_world(seed="player-safe-loader", width=36, height=16, landmark_count=3)
        payload = build_campaign(world, audience="player")

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "player.campaign.json"
            path.write_text(json.dumps(payload), encoding="utf-8")

            with self.assertRaises(CampaignLoadError) as raised:
                load_campaign(path)

        self.assertIn("no GM data", str(raised.exception))

    def test_campaign_player_audience_output_save_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad-save.campaign.json"
            error = StringIO()

            with redirect_stderr(error), self.assertRaises(SystemExit):
                main(["--format", "campaign", "--audience", "player", "--output", str(path)])

            self.assertFalse(path.exists())

        self.assertIn("Campaign saves always include GM data", error.getvalue())

    def test_unknown_schema_version_is_rejected_with_translated_error(self):
        world = generate_world(seed="future-schema", width=36, height=16, landmark_count=3)
        payload = build_campaign(world)
        payload["meta"]["schema_version"] = "9.9.9"

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "future.campaign.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            error = StringIO()

            with redirect_stderr(error), self.assertRaises(SystemExit):
                main(["--open", str(path), "--format", "plain"])

        self.assertIn("campaign schema '9.9.9'", error.getvalue())
        self.assertIn("0.2.0, 0.3.0", error.getvalue())

    def test_open_ignores_generation_flags_and_can_use_example_fixture(self):
        fixture = Path(__file__).resolve().parents[1] / "examples" / "example-campaign.json"
        output = StringIO()

        with redirect_stdout(output):
            main(
                [
                    "--open",
                    str(fixture),
                    "--seed",
                    "ignored",
                    "--width",
                    "24",
                    "--height",
                    "12",
                    "--landmarks",
                    "0",
                    "--format",
                    "campaign",
                ]
            )

        payload = json.loads(output.getvalue())
        self.assertEqual(payload["meta"]["seed"], "atlasmancer-sample")
        self.assertEqual(payload["meta"]["params"]["width"], 72)
        self.assertEqual(payload["meta"]["params"]["height"], 28)
        self.assertEqual(payload["meta"]["params"]["landmark_count"], 9)

    def test_open_can_export_saved_campaign_in_a_different_locale(self):
        original = generate_world(seed="locale-reopen", width=36, height=16, landmark_count=3, locale="en")
        expected = localize_world(original, "es")

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "english.campaign.json"
            path.write_text(render_campaign(original), encoding="utf-8")
            output = StringIO()

            with redirect_stdout(output):
                main(["--open", str(path), "--locale", "es", "--format", "plain"])

        first_original = original.landmarks[0]
        first_expected = expected.landmarks[0]
        text = output.getvalue()

        self.assertIn("Lugares destacados:", text)
        self.assertIn(first_expected.hook, text)
        self.assertNotIn(first_original.hook, text)
        self.assertIn(first_original.name, text)
        self.assertIn(f"at {first_original.x},{first_original.y}", text)


if __name__ == "__main__":
    unittest.main()
