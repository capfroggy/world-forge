# Atlasmancer

Atlasmancer is a free, open-source worldbuilding tool for tabletop campaigns.
The current technical preview ships as a Python CLI while the larger local-first
web app is being designed.

Future web home: `https://Atlasmancer.gt.tc`

Give it a seed and it creates a little world with terrain, landmarks, names, a
legend, and exportable output.

```bash
python -m atlasmancer --seed ember-reef --width 64 --height 24
```

```text
The Amber Wilds of Pyr

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~,,...,,,,,,,,,~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~,.;;;;;|;;;;;;;;;;;....,,~~~~~~~~~~~~~~~~~~~~~~~~~~
~~~~~~,,,,...;;;;;;;;|;;;;;;;;T;;;?;;;.,~~~~~~~~~~~~~~~~~~~~~~~~
~~~~~,,...;;;;;;;AAAAAA;;;AAAA;;;;;;;;;;.,,~~~~~~~~~~~~~~~~~~~~~
~~~~~,,..T;;;;;;AAAAAAAAAAAAAAAAAAA;;;;;;.,,,~~~~~~~~~~~~~~~~~~~
~~~~~~,,..;;;;;;AAAAAAAAAAAAAAAAAAAA;;;;;T.,,~~~~~~~~~~~~~~~~~~~
~~~~~~~~,,..;;;;;;;;;;;;||AAAAAAAAA;;;;;;.,,~~~~~~~~~~~~~~~~~~~~
~~~~~~~~~~~,,X;;;;;;;;C;|^;;;;;?;;;;;;;;.,~~~~~~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~,..;X;;;;|^^;;;;;;;;;;;;.,~~~~~~~~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~~,,,,,,,,,.......,,,~~~~~~~~~~~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Legend: ~ deep water, , shoals, . coast, ; grassland, : drylands, ^ forest,
A mountains, * snow, | river, C capital, v village, X ruin, T tower, ? oddity
```

## Install

From the repo:

```bash
python -m pip install -e .
```

Then run:

```bash
atlasmancer --seed midnight-lantern
```

You can also run it without installing:

```bash
python -m atlasmancer --seed midnight-lantern
```

## Usage

```bash
atlasmancer --help
atlasmancer --seed "salt road" --width 72 --height 28 --landmarks 10
atlasmancer --format markdown --output world.md
atlasmancer --format html --output world.html
atlasmancer --format json --output world.json
```

For printable PNG maps:

```bash
python -m pip install -e .[image]
atlasmancer --seed "dnd-campaign-01" --width 96 --height 48 --landmarks 14 --format png --output world.png
```

Options:

- `--seed`: make the same world again later.
- `--width` / `--height`: control map size.
- `--landmarks`: number of named places to place.
- `--format`: `plain`, `ansi`, `markdown`, `json`, `html`, or `png`.
- `--output`: write to a file instead of stdout.
- `--tile-size`: pixel size for PNG map tiles.

## Why this exists

Because sometimes a small, strange command-line toy is exactly enough momentum
to start making things again.

## Product Direction

The long-term goal is to turn Atlasmancer into a multilingual campaign creation
workspace: continents, regions, countries, settlements, NPCs, factions, quests,
dungeons, printable maps, and player-safe exports in one place.

- [Roadmap](docs/ROADMAP.md)
- [Deployment strategy](docs/DEPLOYMENT_STRATEGY.md)
- [Project decisions](docs/DECISIONS.md)
- [Brand foundation](docs/BRAND.md)
- [Rename plan](docs/RENAME_PLAN.md)

## Development

```bash
python -m unittest
```

## License

MIT
