# pelican-on-this-day

Pelican plugin that shows articles published on the same month/day in previous years — an "On This Day" section.

The section is rendered **client-side**: at build time the plugin writes a JSON map of `"MM-DD"` → articles to the output, and the bundled JS picks the visitor's local date at page load. The section therefore stays correct on a static host without daily rebuilds, and articles from the visitor's current year are excluded.

## Usage

Add to `PLUGINS` in `pelicanconf.py`:

```python
PLUGINS = [
    ...
    "pelican.plugins.on_this_day",
]
```

That's it for the [Attila](https://github.com/Lee-W/attila) theme (needs the version providing the `partials/footer_extra.html` hook) — the plugin overrides that hook with a placeholder and wires everything up:

```html
<aside id="on-this-day" hidden data-source="{{ SITEURL }}/static/pelican_on_this_day/on-this-day.json">
  <div class="inner">
    <p class="on-this-day-label">{% trans %}On This Day{% endtrans %}</p>
    <div class="on-this-day-grid"></div>
  </div>
</aside>
<script src="{{ SITEURL }}/static/pelican_on_this_day/js/on-this-day.js" defer></script>
```

### For other themes

The plugin only needs the placeholder `<aside>` and the script tag somewhere in your templates — no Attila-specific markup or CSS variables required:

```html
<aside id="on-this-day" hidden data-source="{{ SITEURL }}/static/pelican_on_this_day/on-this-day.json">
  <p class="on-this-day-label">On This Day</p>
  <div class="on-this-day-grid"></div>
</aside>
<script src="{{ SITEURL }}/static/pelican_on_this_day/js/on-this-day.js" defer></script>
```

The JS fills `.on-this-day-grid` with `<a class="on-this-day-item">` entries and removes `hidden` when there are matching articles. The section stays hidden when there is nothing to show (or when the data file can't be fetched). The bundled CSS (added to `CSS_OVERRIDE` automatically) styles those classes using `--color-background-contrast`, `--color-content-secondary`, and `--color-primary` custom properties — define them yourself, or skip the bundled CSS (drop `on-this-day.css` from `CSS_OVERRIDE` after the plugin adds it) and style `.on-this-day-item` and friends to match your theme.

## Settings

- `ON_THIS_DAY_MAX_ITEMS` (optional, default unlimited) — cap the number of articles shown per day, keeping the newest ones.

## What gets emitted

- `output/static/pelican_on_this_day/on-this-day.json` — `{"MM-DD": [{"year", "date", "title", "url"}, ...], ...}`, newest first, URLs prefixed with `SITEURL`
- `output/static/pelican_on_this_day/js/on-this-day.js` — client-side renderer
- `output/static/pelican_on_this_day/css/on-this-day.css` — appended to `CSS_OVERRIDE` automatically
