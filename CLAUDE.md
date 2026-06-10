# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common commands

All tasks run via `uv` + `poe` (poethepoet). Tasks are defined in `pyproject.toml` under `[tool.poe.tasks]`.

```bash
uv run poe format         # ruff check --fix && ruff format
uv run poe lint           # ruff check && mypy
uv run poe test           # pytest -n auto --dist=loadfile
uv run poe cover          # test + coverage report
uv run poe check-commit   # commitizen check on commits since origin/main
uv run poe all            # format → lint → check-commit → cover
uv run poe ci             # check-commit → prek run --all-files → cover
uv run poe setup-pre-commit  # install pre-commit hooks via prek
```

Releases: `cz bump` updates the version in `pyproject.toml` and regenerates `CHANGELOG.md` from conventional-commit history. Don't hand-edit `CHANGELOG.md` — it's regenerated.

## Architecture

The plugin is a single-file implementation: `src/pelican/plugins/on_this_day/on_this_day.py`. Bundled static assets (`static/css/`, `static/js/`) and templates (`templates/partials/`) are injected at build time. The section itself is rendered **client-side** so it stays correct on a static host without daily rebuilds.

### Signal flow

`register()` connects three Pelican signals:

1. `signals.initialized` → `_initialize`: appends the plugin's CSS URL to `CSS_OVERRIDE` and the plugin's `templates/` directory to `THEME_TEMPLATES_OVERRIDES` (both idempotent).
2. `signals.article_generator_finalized` → `_copy_static`: copies `static/` to `output/static/pelican_on_this_day/`.
3. `signals.article_generator_finalized` → `_write_on_this_day_data`: groups **all** articles by `"MM-DD"` key (newest first, titles tag-stripped, URLs prefixed with `SITEURL`) and writes `output/static/pelican_on_this_day/on-this-day.json`. No date filtering happens at build time.

### Template + JS

`templates/partials/footer.html` overrides the [Attila](https://github.com/Lee-W/attila) theme's footer partial. It renders a `hidden` placeholder `<aside id="on-this-day">` carrying the JSON URL in `data-source`, plus a deferred `<script>` tag. `static/js/on-this-day.js` fetches the JSON, picks the visitor's **local** month/day, filters out the visitor's current year, fills `.on-this-day-grid` via `textContent` (no HTML injection), and unhides the aside. On fetch failure or no matches the section stays hidden.

## Conventions

- **Conventional commits** are required — `cz check` runs in pre-commit (and via `poe check-commit`). `cz bump` reads commit history to choose the version bump and write the changelog entry.
- **Type checking**: mypy runs on `src` and `tests`. `pelican.*` modules are untyped, so missing imports are ignored for that namespace only.
- **Pre-commit**: `prek` is the runner. Hooks live in `.pre-commit-config.yaml`.
