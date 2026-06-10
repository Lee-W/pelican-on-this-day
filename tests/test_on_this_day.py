"""Tests for pelican-on-this-day plugin."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

import pelican.plugins.on_this_day.on_this_day as otd_module
from pelican.plugins.on_this_day.on_this_day import (
    _copy_static,
    _initialize,
    _write_on_this_day_data,
    register,
)


def make_article(
    year: int,
    month: int,
    day: int,
    title: str = "Test",
    url: str = "posts/test.html",
) -> SimpleNamespace:
    return SimpleNamespace(
        title=title,
        url=url,
        date=datetime(year, month, day, 12, 0),
    )


def make_generator(
    articles: list,
    output_path: str = "/tmp/output",
    siteurl: str = "https://example.com",
) -> SimpleNamespace:
    return SimpleNamespace(
        articles=articles,
        context={},
        output_path=output_path,
        settings={"SITEURL": siteurl},
    )


def make_pelican(css_override: list | None = None) -> SimpleNamespace:
    return SimpleNamespace(
        settings={"CSS_OVERRIDE": css_override or [], "THEME_TEMPLATES_OVERRIDES": []}
    )


def read_data(output_path: Path) -> dict:
    data_file = output_path / "static" / "pelican_on_this_day" / "on-this-day.json"
    data: dict = json.loads(data_file.read_text(encoding="utf-8"))
    return data


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
    assert (
        pelican.settings["THEME_TEMPLATES_OVERRIDES"].count(otd_module._TEMPLATES_DIR)
        == 1
    )


# ---------------------------------------------------------------------------
# _write_on_this_day_data
# ---------------------------------------------------------------------------


def test_write_groups_by_month_day(tmp_path: Path):
    generator = make_generator(
        [
            make_article(2020, 6, 11, "A"),
            make_article(2021, 6, 11, "B"),
            make_article(2021, 12, 25, "C"),
        ],
        output_path=str(tmp_path),
    )
    _write_on_this_day_data(generator)
    data = read_data(tmp_path)
    assert {a["title"] for a in data["06-11"]} == {"A", "B"}
    assert [a["title"] for a in data["12-25"]] == ["C"]


def test_write_includes_current_year(tmp_path: Path):
    # Year filtering happens client-side against the visitor's clock,
    # so the data must include every year.
    today = datetime.now()
    generator = make_generator(
        [make_article(today.year, 6, 11, "This year")], output_path=str(tmp_path)
    )
    _write_on_this_day_data(generator)
    data = read_data(tmp_path)
    assert data["06-11"][0]["year"] == today.year


def test_write_sorted_newest_first(tmp_path: Path):
    generator = make_generator(
        [
            make_article(2020, 6, 11, "2020"),
            make_article(2018, 6, 11, "2018"),
            make_article(2022, 6, 11, "2022"),
        ],
        output_path=str(tmp_path),
    )
    _write_on_this_day_data(generator)
    data = read_data(tmp_path)
    assert [a["title"] for a in data["06-11"]] == ["2022", "2020", "2018"]


def test_write_empty_when_no_articles(tmp_path: Path):
    generator = make_generator([], output_path=str(tmp_path))
    _write_on_this_day_data(generator)
    assert read_data(tmp_path) == {}


def test_write_url_prefixed_with_siteurl(tmp_path: Path):
    generator = make_generator(
        [make_article(2020, 6, 11, url="posts/foo.html")],
        output_path=str(tmp_path),
        siteurl="https://blog.example",
    )
    _write_on_this_day_data(generator)
    data = read_data(tmp_path)
    assert data["06-11"][0]["url"] == "https://blog.example/posts/foo.html"


def test_write_strips_html_tags_from_title(tmp_path: Path):
    generator = make_generator(
        [make_article(2020, 6, 11, title="Hello <code>world</code>")],
        output_path=str(tmp_path),
    )
    _write_on_this_day_data(generator)
    data = read_data(tmp_path)
    assert data["06-11"][0]["title"] == "Hello world"


def test_write_preserves_non_ascii(tmp_path: Path):
    generator = make_generator(
        [make_article(2020, 6, 11, title="歷史上的今天")], output_path=str(tmp_path)
    )
    _write_on_this_day_data(generator)
    raw = (tmp_path / "static" / "pelican_on_this_day" / "on-this-day.json").read_text(
        encoding="utf-8"
    )
    assert "歷史上的今天" in raw


def test_write_includes_iso_date(tmp_path: Path):
    generator = make_generator([make_article(2020, 6, 11)], output_path=str(tmp_path))
    _write_on_this_day_data(generator)
    data = read_data(tmp_path)
    assert data["06-11"][0]["date"] == "2020-06-11T12:00:00"


# ---------------------------------------------------------------------------
# _copy_static
# ---------------------------------------------------------------------------


def test_copy_static_css(tmp_path: Path):
    generator = make_generator([], output_path=str(tmp_path))
    _copy_static(generator)
    css_dst = tmp_path / "static" / "pelican_on_this_day" / "css" / "on-this-day.css"
    assert css_dst.exists()


def test_copy_static_js(tmp_path: Path):
    generator = make_generator([], output_path=str(tmp_path))
    _copy_static(generator)
    js_dst = tmp_path / "static" / "pelican_on_this_day" / "js" / "on-this-day.js"
    assert js_dst.exists()


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
    assert _write_on_this_day_data in connected
