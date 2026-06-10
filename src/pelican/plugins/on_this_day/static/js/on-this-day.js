(function () {
  "use strict";

  var aside = document.getElementById("on-this-day");
  if (!aside || !aside.dataset.source) {
    return;
  }

  var now = new Date();
  var pad = function (n) {
    return String(n).padStart(2, "0");
  };
  var key = pad(now.getMonth() + 1) + "-" + pad(now.getDate());

  fetch(aside.dataset.source)
    .then(function (response) {
      if (!response.ok) {
        throw new Error("HTTP " + response.status);
      }
      return response.json();
    })
    .then(function (data) {
      var entries = (data[key] || []).filter(function (entry) {
        return entry.year !== now.getFullYear();
      });
      if (entries.length === 0) {
        return;
      }

      var grid = aside.querySelector(".on-this-day-grid");
      entries.forEach(function (entry) {
        var link = document.createElement("a");
        link.className = "on-this-day-item";
        link.href = entry.url;

        var teaser = document.createElement("section");
        teaser.className = "post-nav-teaser";

        var meta = document.createElement("p");
        meta.className = "post-nav-meta";
        var time = document.createElement("time");
        time.dateTime = entry.date;
        time.textContent = String(entry.year);
        meta.appendChild(time);

        var title = document.createElement("h2");
        title.className = "post-nav-title";
        title.textContent = entry.title;

        teaser.appendChild(meta);
        teaser.appendChild(title);
        link.appendChild(teaser);
        grid.appendChild(link);
      });

      aside.hidden = false;
    })
    .catch(function () {
      /* leave the section hidden when data can't be loaded */
    });
})();
