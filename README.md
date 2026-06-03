# pelican-on-this-day

Pelican plugin that injects articles published on the same month/day in previous years into the template context as `on_this_day_articles`.

## Usage

Add to `PLUGINS` in `pelicanconf.py`:

```python
PLUGINS = [
    ...
    "pelican.plugins.on_this_day",
]
```

Then use `on_this_day_articles` in your theme templates. Example (e.g. in a footer partial):

```html
{% if on_this_day_articles %}
<aside id="on-this-day">
  <div class="inner">
    <p class="on-this-day-label">歷史上的今天</p>
    <div class="on-this-day-grid">
      {% for article in on_this_day_articles %}
        <a class="on-this-day-item" href="{{ SITEURL }}/{{ article.url }}">
          <section class="post-nav-teaser">
            <p class="post-nav-meta"><time datetime="{{ article.date.isoformat() }}">{{ article.date.strftime("%Y") }}</time></p>
            <h2 class="post-nav-title">{{ article.title|striptags|e }}</h2>
          </section>
        </a>
      {% endfor %}
    </div>
  </div>
</aside>
{% endif %}
```

The plugin automatically copies `on-this-day.css` to `output/static/pelican_on_this_day/css/` and appends it to `CSS_OVERRIDE` (used by the [Attila](https://github.com/Lee-W/attila) theme).
