# world-forge

`world-forge` is a tiny deterministic fantasy world generator for terminal
explorers, tabletop notes, writing prompts, and questionable cartography
decisions.

Give it a seed and it creates a little world with terrain, landmarks, names, a
legend, and exportable output.

```bash
python -m world_forge --seed ember-reef --width 64 --height 24
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
world-forge --seed midnight-lantern
```

You can also run it without installing:

```bash
python -m world_forge --seed midnight-lantern
```

## Usage

```bash
world-forge --help
world-forge --seed "salt road" --width 72 --height 28 --landmarks 10
world-forge --format markdown --output world.md
world-forge --format html --output world.html
world-forge --format json --output world.json
```

For printable PNG maps:

```bash
python -m pip install -e .[image]
world-forge --seed "dnd-campaign-01" --width 96 --height 48 --landmarks 14 --format png --output world.png
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

The long-term goal is to turn World Forge into a free, open-source, multilingual
worldbuilding tool for D&D/TTRPG campaigns: continents, regions, countries,
settlements, NPCs, factions, quests, dungeons, printable maps, and player-safe
exports in one place.

- [Roadmap](docs/ROADMAP.md)
- [Deployment strategy](docs/DEPLOYMENT_STRATEGY.md)

## Development

```bash
python -m unittest
```

## License

MIT
