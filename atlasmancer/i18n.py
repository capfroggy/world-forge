"""Locale loading and lookup helpers."""

from __future__ import annotations

from dataclasses import dataclass
import json
import logging
from pathlib import Path
from typing import Any


DEFAULT_LOCALE = "en"
SUPPORTED_LOCALES = ("en", "es")

LOGGER = logging.getLogger(__name__)
_MISSING = object()


class UnsupportedLocaleError(ValueError):
    """Raised when a requested locale is not available."""


@dataclass(frozen=True)
class LocaleCatalog:
    """Localized strings with fallback lookup."""

    locale: str
    data: dict[str, Any]
    fallback: dict[str, Any]

    def t(self, key: str, **values: object) -> str:
        value = self.get(key)
        if not isinstance(value, str):
            raise TypeError(f"Locale key '{key}' is not a string")
        if values:
            return value.format(**values)
        return value

    def content(self, key: str) -> list[str]:
        value = self.get(f"content.{key}")
        if not isinstance(value, list):
            raise TypeError(f"Locale key 'content.{key}' is not a list")
        return [str(item) for item in value]

    def get(self, key: str) -> Any:
        value = _lookup(self.data, key)
        if value is not _MISSING:
            return value

        fallback = _lookup(self.fallback, key)
        if fallback is not _MISSING:
            LOGGER.warning("Missing locale key '%s' in '%s'; falling back to '%s'", key, self.locale, DEFAULT_LOCALE)
            return fallback

        raise KeyError(key)


def load_locale(locale: str = DEFAULT_LOCALE) -> LocaleCatalog:
    """Load a locale catalog with English fallback."""

    if locale not in SUPPORTED_LOCALES:
        raise UnsupportedLocaleError(locale)

    fallback = _load_json(DEFAULT_LOCALE)
    data = fallback if locale == DEFAULT_LOCALE else _load_json(locale)
    return LocaleCatalog(locale=locale, data=data, fallback=fallback)


def available_locales() -> tuple[str, ...]:
    return SUPPORTED_LOCALES


def _lookup(data: dict[str, Any], key: str) -> Any:
    current: Any = data
    for part in key.split("."):
        if not isinstance(current, dict) or part not in current:
            return _MISSING
        current = current[part]
    return current


def _load_json(locale: str) -> dict[str, Any]:
    path = _locales_dir() / f"{locale}.json"
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, dict):
        raise TypeError(f"Locale file '{path}' must contain a JSON object")
    return data


def _locales_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "locales"
