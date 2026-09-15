/* ==========================================================================
 * archive.js — renders the paper catalogue. No backend. No dependencies.
 *
 * Expects a global `papers` array to be defined BEFORE this script loads,
 * e.g. in index.html:
 *
 *   <script>
 *     const papers = [ { title, file, category, level, difficulty,
 *                        problems, year, description }, ... ];
 *   </script>
 *   <script src="assets/js/archive.js"></script>
 *
 * All links use the relative `file` values verbatim (e.g. "papers/x.html"),
 * so the site works under a GitHub Pages subpath.
 * ========================================================================== */
(function () {
  "use strict";

  var catalogueEl = document.getElementById("catalogue");
  var searchEl = document.getElementById("search");
  var countEl = document.getElementById("archive-count");
  var noResultsEl = document.getElementById("no-results");
  var filterBar = document.getElementById("filters");

  if (!catalogueEl) return;

  var allPapers = Array.isArray(window.papers) ? window.papers
    : (typeof papers !== "undefined" && Array.isArray(papers) ? papers : []);

  var activeCategory = "All";
  var query = "";

  var FILTERS = ["All", "Physics", "Mathematics", "Computer Science", "Machine Learning", "Electronics", "Other"];

  function normalise(s) {
    return String(s == null ? "" : s).toLowerCase();
  }

  function paperMatchesCategory(p, cat) {
    if (cat === "All") return true;
    var hay = normalise(p.category) + " " + normalise(p.level);
    if (cat === "Other") {
      var known = ["physics", "mathematics", "computer science", "machine learning", "electronics"];
      return !known.some(function (k) { return hay.indexOf(k) !== -1; });
    }
    return hay.indexOf(normalise(cat)) !== -1;
  }

  function paperMatchesQuery(p, q) {
    if (!q) return true;
    var hay = [p.title, p.category, p.level, p.description, p.difficulty]
      .map(normalise).join(" ");
    return q.split(/\s+/).every(function (tok) {
      return tok === "" || hay.indexOf(tok) !== -1;
    });
  }

  function factsLine(p) {
    var bits = [];
    if (p.problems) bits.push(String(p.problems) + " problems");
    if (p.difficulty) bits.push(String(p.difficulty));
    if (p.year) bits.push(String(p.year));
    return bits.join("  ·  ");
  }

  function classificationLine(p) {
    var bits = [];
    if (p.category) bits.push(p.category);
    if (p.level) bits.push(p.level);
    return bits.join(" · ");
  }

  function render() {
    var visible = allPapers.filter(function (p) {
      return paperMatchesCategory(p, activeCategory) && paperMatchesQuery(p, query);
    });

    catalogueEl.innerHTML = "";

    visible.forEach(function (p, i) {
      var li = document.createElement("li");
      li.className = "paper-entry";

      var num = document.createElement("div");
      num.className = "paper-number";
      num.setAttribute("aria-hidden", "true");
      num.textContent = String(i + 1).padStart(2, "0");

      var body = document.createElement("div");

      var h = document.createElement("h2");
      h.className = "paper-title";
      h.textContent = p.title || "Untitled paper";

      var cls = document.createElement("p");
      cls.className = "paper-classification";
      cls.textContent = classificationLine(p);

      var facts = document.createElement("p");
      facts.className = "paper-facts";
      facts.textContent = factsLine(p);

      var desc = document.createElement("p");
      desc.className = "paper-desc";
      desc.textContent = p.description || "";

      var row = document.createElement("div");
      row.className = "read-row";

      var a = document.createElement("a");
      a.className = "btn-read";
      a.href = p.file; // relative path, e.g. "papers/x.html"
      a.textContent = "Read paper";
      a.setAttribute("aria-label", "Read paper: " + (p.title || p.file));

      row.appendChild(a);
      body.appendChild(h);
      body.appendChild(cls);
      body.appendChild(facts);
      body.appendChild(desc);
      body.appendChild(row);

      li.appendChild(num);
      li.appendChild(body);
      catalogueEl.appendChild(li);
    });

    var total = allPapers.length;
    var shown = visible.length;
    if (countEl) {
      var noun = total === 1 ? "paper" : "papers";
      if (shown === total) {
        countEl.textContent = total + " " + noun + " in archive";
      } else {
        countEl.textContent = "Showing " + shown + " of " + total + " " + noun;
      }
    }
    if (noResultsEl) noResultsEl.hidden = visible.length !== 0;
    catalogueEl.setAttribute("aria-live", "polite");
  }

  function buildFilters() {
    if (!filterBar) return;
    filterBar.innerHTML = "";
    FILTERS.forEach(function (name) {
      var li = document.createElement("li");
      var btn = document.createElement("button");
      btn.type = "button";
      btn.textContent = name;
      btn.setAttribute("aria-pressed", name === activeCategory ? "true" : "false");
      btn.addEventListener("click", function () {
        activeCategory = name;
        var btns = filterBar.querySelectorAll("button");
        btns.forEach(function (b) {
          b.setAttribute("aria-pressed", b.textContent === name ? "true" : "false");
        });
        render();
      });
      li.appendChild(btn);
      filterBar.appendChild(li);
    });
  }

  if (searchEl) {
    searchEl.addEventListener("input", function (e) {
      query = normalise(e.target.value.trim());
      render();
    });
  }

  buildFilters();
  render();
})();
