"""pelican-on-this-day plugin: emit per-day article data rendered client-side.

Build time writes a JSON map of "MM-DD" -> articles to the output static dir;
the bundled JS picks the visitor's local date so the section stays correct
without daily rebuilds.
"""

from __future__ import annotations

import json
import logging
import re
import shutil
from pathlib import Path
from typing import Any

from pelican import signals

log = logging.getLogger(__name__)

_CSS_STATIC_URL = "/static/pelican_on_this_day/css/on-this-day.css"
_TEMPLATES_DIR = str(Path(__file__).parent / "templates")
_DATA_FILENAME = "on-this-day.json"
_TAG_RE = re.compile(r"<[^>]+>")


def _initialize(pelican: Any) -> None:
    overrides: list[str] = pelican.settings.get("CSS_OVERRIDE", [])
    if _CSS_STATIC_URL not in overrides:
        pelican.settings["CSS_OVERRIDE"] = [*overrides, _CSS_STATIC_URL]

    theme_overrides: list[str] = pelican.settings.get("THEME_TEMPLATES_OVERRIDES", [])
    if _TEMPLATES_DIR not in theme_overrides:
        pelican.settings["THEME_TEMPLATES_OVERRIDES"] = [
            *theme_overrides,
            _TEMPLATES_DIR,
        ]


def _copy_static(generator: Any) -> None:
    static_src = Path(__file__).parent / "static"
    static_dst = Path(generator.output_path) / "static" / "pelican_on_this_day"
    shutil.copytree(static_src, static_dst, dirs_exist_ok=True)
    log.debug("pelican-on-this-day: copied static files to %s", static_dst)


def _write_on_this_day_data(generator: Any) -> None:
    siteurl = generator.settings.get("SITEURL", "")
    data: dict[str, list[dict[str, Any]]] = {}
    for article in sorted(generator.articles, key=lambda a: a.date, reverse=True):
        key = f"{article.date.month:02d}-{article.date.day:02d}"
        data.setdefault(key, []).append(
            {
                "year": article.date.year,
                "date": article.date.isoformat(),
                "title": _TAG_RE.sub("", article.title),
                "url": f"{siteurl}/{article.url}",
            }
        )
    dst = (
        Path(generator.output_path) / "static" / "pelican_on_this_day" / _DATA_FILENAME
    )
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    log.debug(
        "pelican-on-this-day: wrote %d day(s) of article data to %s", len(data), dst
    )


def register() -> None:
    signals.initialized.connect(_initialize)
    signals.article_generator_finalized.connect(_copy_static)
    signals.article_generator_finalized.connect(_write_on_this_day_data)
