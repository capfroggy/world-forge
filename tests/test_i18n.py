import io
import textwrap
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
        expected = textwrap.dedent(
            """\
            The Shimmering Marches of Fen

            ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            ~~~~~~~~~~~~~~~,,.....X.,,~~~~~~~~~~
            ~~~~~~~~~~~~,,.^^^^^^^;;;;.,~~~~~~~~
            ~~~~~~~~~,,,.^^^^^^^^;;;;;;.,~~~~~~~
            ~~~~~~~~,,..;;^^^^^^^;;;;;;.X,~~~~~~
            ~~~~~~~~,,..;;^^C^^^|;;;;;..,,~~~~~~
            ~~~~~~~~~,,..;;^^^^;;|;..,,,~~~~~~~~
            ~~~~~~~~~~~,,..;^^;;.v,,~~~~~~~~~~~~
            ~~~~~~~~~~~~~~,,,,,,~~~~~~~~~~~~~~~~
            ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

            Legend: ~ deep water, , shoals, . coast, ; grassland, : drylands, ^ forest, A mountains, * snow, | river, C capital, v village, X ruin, T tower, ? oddity

            Landmarks:
            - C Bel Gate (capital) at 16,9: A patron offers coin for proof that the old stories are true.
              NPC: a river priest who collects forbidden maps
              Rumor: Nobody agrees where the oldest road begins.
              Danger: raiders using old border tunnels
              Reward: maps to another forgotten site
            - X JunWick (ruin) at 22,5: The place is peaceful, but every child has drawn the same monster.
              NPC: a quiet scribe carrying a sealed royal order
              Rumor: Nobody agrees where the oldest road begins.
              Danger: bandits with military discipline
              Reward: a legal claim to land nobody wants yet
            - X Sol Run (ruin) at 28,8: A sealed door has opened for the first time in a century.
              NPC: a river priest who collects forbidden maps
              Rumor: The wells hum after midnight.
              Danger: sinkholes hidden beneath moss and flowers
              Reward: maps to another forgotten site
            - v Nor Mere (village) at 21,11: A sealed door has opened for the first time in a century.
              NPC: a river priest who collects forbidden maps
              Rumor: Every seventh bridge is older than the river.
              Danger: raiders using old border tunnels
              Reward: a chest of old coins and newer blackmail
            """
        )
        output = io.StringIO()

        with redirect_stdout(output):
            main(["--seed", "i18n-regression", "--width", "36", "--height", "16", "--landmarks", "4", "--format", "plain"])

        self.assertEqual(output.getvalue(), expected)

    def test_unsupported_locale_has_clear_error(self):
        error = io.StringIO()

        with redirect_stderr(error), self.assertRaises(SystemExit):
            main(["--locale", "fr"])

        self.assertIn("Unsupported locale 'fr'. Available: en, es.", error.getvalue())
