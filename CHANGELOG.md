## 0.5.0 (2026-07-13)

### Feat

- add max-items cap, robust tag stripping, theme-agnostic docs

### Fix

- make pytest addopts/testpaths actually apply, add E/F to ruff

## 0.4.0 (2026-06-11)

### Feat

- override Attila's footer_extra hook instead of the whole footer

## 0.3.0 (2026-06-11)

### BREAKING CHANGE

- the on_this_day_articles template variable is no
longer injected; themes must render the hidden aside placeholder and
load js/on-this-day.js (the bundled Attila footer override already
does).

### Feat

- render the section client-side so it tracks the visitor's date

### Fix

- keep the section separator clear of the page's last element

## 0.2.0 (2026-06-03)

### Feat

- add i18n support and pin setup-uv to 8.1.0

## 0.1.0 (2026-06-03)

### Feat

- initial release: inject on_this_day_articles into template context, copy CSS static files
