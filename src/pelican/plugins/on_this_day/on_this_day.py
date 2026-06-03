"""pelican-on-this-day plugin: inject articles from the same month/day in previous years."""

from __future__ import annotations

import logging
import shutil
from datetime import datetime
from pathlib import Path

from pelican import signals

log = logging.getLogger(__name__)

_CSS_STATIC_URL = "/static/pelican_on_this_day/css/on-this-day.css"
_TEMPLATES_DIR = str(Path(__file__).parent / "templates")


def _initialize(pelican: object) -> None:
    overrides: list[str] = pelican.settings.get("CSS_OVERRIDE", [])  # type: ignore[union-attr]
    if _CSS_STATIC_URL not in overrides:
        pelican.settings["CSS_OVERRIDE"] = [*overrides, _CSS_STATIC_URL]  # type: ignore[union-attr]

    theme_overrides: list[str] = pelican.settings.get("THEME_TEMPLATES_OVERRIDES", [])  # type: ignore[union-attr]
    if _TEMPLATES_DIR not in theme_overrides:
        pelican.settings["THEME_TEMPLATES_OVERRIDES"] = [*theme_overrides, _TEMPLATES_DIR]  # type: ignore[union-attr]


def _copy_static(generator: object) -> None:
    static_src = Path(__file__).parent / "static"
    static_dst = Path(generator.output_path) / "static" / "pelican_on_this_day"  # type: ignore[union-attr]
    shutil.copytree(static_src, static_dst, dirs_exist_ok=True)
    log.debug("pelican-on-this-day: copied static files to %s", static_dst)


def _inject_on_this_day(generator: object) -> None:
    today = datetime.now()
    key = f"{today.month:02d}-{today.day:02d}"
    matching = sorted(
        [
            a
            for a in generator.articles  # type: ignore[union-attr]
            if f"{a.date.month:02d}-{a.date.day:02d}" == key
            and a.date.year != today.year
        ],
        key=lambda a: a.date,
    )
    generator.context["on_this_day_articles"] = matching  # type: ignore[union-attr]
    log.debug("pelican-on-this-day: found %d article(s) for %s", len(matching), key)


def register() -> None:
    signals.initialized.connect(_initialize)
    signals.article_generator_finalized.connect(_copy_static)
    signals.article_generator_finalized.connect(_inject_on_this_day)
