"""Tests for pelican-on-this-day plugin."""

from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

import pelican.plugins.on_this_day.on_this_day as otd_module
from pelican.plugins.on_this_day.on_this_day import (
    _copy_static,
    _initialize,
    _inject_on_this_day,
    register,
)


def make_article(year: int, month: int, day: int, title: str = "Test") -> SimpleNamespace:
    return SimpleNamespace(
        title=title,
        date=datetime(year, month, day, 12, 0),
    )


def make_generator(articles: list, output_path: str = "/tmp/output") -> SimpleNamespace:
    return SimpleNamespace(
        articles=articles,
        context={},
        output_path=output_path,
    )


def make_pelican(css_override: list | None = None) -> SimpleNamespace:
    return SimpleNamespace(settings={"CSS_OVERRIDE": css_override or [], "THEME_TEMPLATES_OVERRIDES": []})


# ---------------------------------------------------------------------------
# _initialize
# ---------------------------------------------------------------------------


def test_initialize_adds_css_override():
    pelican = make_pelican()
    _initialize(pelican)
    assert otd_module._CSS_STATIC_URL in pelican.settings["CSS_OVERRIDE"]


def test_initialize_css_override_idempotent():
    pelican = make_pelican()
    _initialize(pelican)
    _initialize(pelican)
    assert pelican.settings["CSS_OVERRIDE"].count(otd_module._CSS_STATIC_URL) == 1


def test_initialize_preserves_existing_css():
    pelican = make_pelican(css_override=["/static/custom.css"])
    _initialize(pelican)
    assert "/static/custom.css" in pelican.settings["CSS_OVERRIDE"]
    assert otd_module._CSS_STATIC_URL in pelican.settings["CSS_OVERRIDE"]


def test_initialize_adds_theme_templates_overrides():
    pelican = make_pelican()
    _initialize(pelican)
    assert otd_module._TEMPLATES_DIR in pelican.settings["THEME_TEMPLATES_OVERRIDES"]


def test_initialize_templates_overrides_idempotent():
    pelican = make_pelican()
    _initialize(pelican)
    _initialize(pelican)
    assert pelican.settings["THEME_TEMPLATES_OVERRIDES"].count(otd_module._TEMPLATES_DIR) == 1


# ---------------------------------------------------------------------------
# _inject_on_this_day
# ---------------------------------------------------------------------------


def test_inject_matching_articles():
    today = datetime.now()
    article = make_article(today.year - 1, today.month, today.day, "Past article")
    generator = make_generator([article])
    _inject_on_this_day(generator)
    assert generator.context["on_this_day_articles"] == [article]


def test_inject_excludes_current_year():
    today = datetime.now()
    article = make_article(today.year, today.month, today.day, "This year")
    generator = make_generator([article])
    _inject_on_this_day(generator)
    assert generator.context["on_this_day_articles"] == []


def test_inject_excludes_different_day():
    today = datetime.now()
    other_day = today.day % 28 + 1
    article = make_article(today.year - 1, today.month, other_day, "Other day")
    generator = make_generator([article])
    _inject_on_this_day(generator)
    assert generator.context["on_this_day_articles"] == []


def test_inject_sorted_by_date():
    today = datetime.now()
    a2020 = make_article(2020, today.month, today.day, "2020")
    a2018 = make_article(2018, today.month, today.day, "2018")
    a2022 = make_article(2022, today.month, today.day, "2022")
    generator = make_generator([a2020, a2022, a2018])
    _inject_on_this_day(generator)
    assert generator.context["on_this_day_articles"] == [a2018, a2020, a2022]


def test_inject_empty_when_no_match():
    generator = make_generator([])
    _inject_on_this_day(generator)
    assert generator.context["on_this_day_articles"] == []


def test_inject_multiple_years():
    today = datetime.now()
    articles = [make_article(today.year - i, today.month, today.day) for i in range(1, 4)]
    generator = make_generator(articles)
    _inject_on_this_day(generator)
    assert len(generator.context["on_this_day_articles"]) == 3


# ---------------------------------------------------------------------------
# _copy_static
# ---------------------------------------------------------------------------


def test_copy_static(tmp_path: Path):
    generator = make_generator([], output_path=str(tmp_path))
    _copy_static(generator)
    css_dst = tmp_path / "static" / "pelican_on_this_day" / "css" / "on-this-day.css"
    assert css_dst.exists()


# ---------------------------------------------------------------------------
# register
# ---------------------------------------------------------------------------


def test_register_connects_signals():
    from pelican import signals

    register()
    connected = {r() for r in signals.initialized.receivers.values()}
    assert _initialize in connected
    connected = {r() for r in signals.article_generator_finalized.receivers.values()}
    assert _copy_static in connected
    assert _inject_on_this_day in connected
