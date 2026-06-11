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
