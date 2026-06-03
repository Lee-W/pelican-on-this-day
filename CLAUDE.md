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

The plugin is a single-file implementation: `src/pelican/plugins/on_this_day/on_this_day.py`. Bundled static assets (`static/css/`) and templates (`templates/partials/`) are injected at build time.

### Signal flow

`register()` connects three Pelican signals:

1. `signals.initialized` → `_initialize`: appends the plugin's CSS URL to `CSS_OVERRIDE` and the plugin's `templates/` directory to `THEME_TEMPLATES_OVERRIDES` (both idempotent).
2. `signals.article_generator_finalized` → `_copy_static`: copies `static/` to `output/static/pelican_on_this_day/`.
3. `signals.article_generator_finalized` → `_inject_on_this_day`: filters all articles to those matching today's month/day from previous years, sorts by date, and injects the result as `on_this_day_articles` into the generator context.

### Template

`templates/partials/footer.html` overrides the [Attila](https://github.com/Lee-W/attila) theme's footer partial. It renders `on_this_day_articles` (year + title per item) above the standard copyright bar, and is conditionally hidden when the list is empty.

## Conventions

- **Conventional commits** are required — `cz check` runs in pre-commit (and via `poe check-commit`). `cz bump` reads commit history to choose the version bump and write the changelog entry.
- **Type checking**: mypy runs on `src` and `tests`. `pelican.*` modules are untyped, so missing imports are ignored for that namespace only.
- **Pre-commit**: `prek` is the runner. Hooks live in `.pre-commit-config.yaml`.
