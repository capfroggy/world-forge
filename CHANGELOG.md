# Changelog

## 0.5.0 - Unreleased

### Added

- Civilized land masses now generate countries with governments, resources, crises, and one capital each.

### Changed

- Capital landmarks are generated per qualified land mass and no longer consume the `--landmarks` budget; existing seeds may have a different number or placement of capitals.

## 0.4.0 - Unreleased

### Added

- Geography regions are now serialized in `campaign.json`, reopened with `--open`, and shown in Markdown and HTML exports.

### Changed

- Geography region detection and river continuity fixes may change region or river layouts for existing seeds compared with earlier versions.

## 0.3.0 - Unreleased

### Added

- `--open <campaign.json>` to reopen saved campaign files and export them without regenerating from the seed.
- Campaign loading with explicit support for schema versions `0.2.0` and `0.3.0`.

### Changed

- Campaign saves written to files must include GM data; `--format campaign --audience player --output <file>` is rejected to prevent accidental data loss.

## 0.2.0 - Unreleased

### Added

- `--locale en|es` flag with full i18n coverage of CLI help, legends, and narrative content.
- `--audience gm|player` flag. `player` strips secrets, dangers, and rewards from every text, HTML, PNG, and campaign export.
- `--format campaign`, producing a versioned, portable `campaign.json` (see `docs/ATLASMANCER_V0.2_SPEC.md` section 5) with stable landmark `id`s, a `world_id` derived from the seed, and reserved `regions`/`countries`/`factions`/`quests`/`dungeons` arrays for future phases.

### Changed

- Renamed the project from `world-forge` to **Atlasmancer**.
- Renamed the Python package from `world_forge` to `atlasmancer`.
- Renamed the CLI command from `world-forge` to `atlasmancer`.
- Expanded NPC and rumor content banks; flavor text for existing seeds may change as a result.
- `--format json` is deprecated in favor of `--format campaign`; it still works unchanged.

### Breaking

- `world-forge` is no longer installed as a console command.
- `python -m world_forge` is replaced by `python -m atlasmancer`.
- `Landmark` and `World` gained required `id`/`world_id` fields; code constructing these dataclasses directly (not via `generate_world`) must be updated.

## 0.1.0

- Initial deterministic ASCII world generator.
- Markdown, JSON, HTML, ANSI, and PNG exports.
- Printable atlas prototype with landmarks and GM notes.
