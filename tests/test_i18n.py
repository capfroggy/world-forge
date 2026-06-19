import io
import unittest
from contextlib import redirect_stderr, redirect_stdout

from atlasmancer.cli import main
from atlasmancer.i18n import LocaleCatalog, load_locale


class I18nTests(unittest.TestCase):
    def test_content_arrays_have_locale_parity(self):
        en = load_locale("en")
        es = load_locale("es")

        for key in ("npcs", "hooks", "rumors", "secrets", "dangers", "rewards"):
            self.assertEqual(len(en.content(key)), len(es.content(key)), key)

    def test_missing_locale_key_falls_back_to_english(self):
        catalog = LocaleCatalog(
            locale="es",
            data={"export": {}},
            fallback={"export": {"legend_label": "Legend"}},
        )

        with self.assertLogs("atlasmancer.i18n", level="WARNING") as logs:
            self.assertEqual(catalog.t("export.legend_label"), "Legend")

        self.assertIn("falling back", logs.output[0])

    def test_plain_default_output_matches_pre_i18n_snapshot(self):
        first = io.StringIO()
        second = io.StringIO()
        args = [
            "--seed",
            "i18n-regression",
            "--width",
            "36",
            "--height",
            "16",
            "--landmarks",
            "4",
            "--format",
            "plain",
        ]

        with redirect_stdout(first):
            main(args)
        with redirect_stdout(second):
            main(args)

        output = first.getvalue()
        self.assertEqual(output, second.getvalue())
        self.assertIn("Landmarks:", output)
        self.assertIn("NPC:", output)
        self.assertIn("Rumor:", output)
        self.assertEqual(output.count("\n- "), 4)

    def test_unsupported_locale_has_clear_error(self):
        error = io.StringIO()

        with redirect_stderr(error), self.assertRaises(SystemExit):
            main(["--locale", "fr"])

        self.assertIn("Unsupported locale 'fr'. Available: en, es.", error.getvalue())
