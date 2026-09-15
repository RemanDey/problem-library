# Physics / Mathematics Problem Archive

A **100% static, GitHub Pages–compatible** library of standalone HTML question papers.

No backend. No database. No build step. No frameworks. No npm install.
Just `HTML + CSS + vanilla JS`, with MathJax loaded from CDN inside papers only.

When you open the site you see a searchable, filterable catalogue; clicking
**Read paper** opens that paper as a normal independent page (full navigation,
not an iframe).

**Live use:** open `index.html` in a browser, or serve the folder with any
static server. Deploy by pushing to GitHub and enabling Pages.

---

## Table of contents

- [Features](#features)
- [Live demo / preview](#live-demo--preview)
- [Repository structure](#repository-structure)
- [How it works (30-second version)](#how-it-works-30-second-version)
- [Adding a new paper](#adding-a-new-paper)
  - [Option A — manual (3 steps)](#option-a--manual-3-steps)
  - [Option B — assisted with `sync_papers.py`](#option-b--assisted-with-sync_paperspy)
- [Metadata reference](#metadata-reference)
- [Paper authoring guide](#paper-authoring-guide)
- [Homepage catalogue guide](#homepage-catalogue-guide)
- [Styling and theme](#styling-and-theme)
- [Deploying to GitHub Pages](#deploying-to-github-pages)
- [Local development](#local-development)
- [Accessibility, responsive, print](#accessibility-responsive-print)
- [Troubleshooting / FAQ](#troubleshooting--faq)
- [Further reading](#further-reading)
- [License / reuse](#license--reuse)

---

## Features

- **Searchable catalogue** — tokenised AND-search across title, category,
  level, description, and difficulty (`assets/js/archive.js`).
- **Subject filters** — All, Physics, Mathematics, Computer Science,
  Machine Learning, Other. Matching is substring-based on
  `category + level`, so `Mathematics / Machine Learning` appears under both
  Mathematics and Machine Learning.
- **Auto-numbered entries** — `01`, `02`, … generated at render time; no
  manual numbering.
- **Live result counts** — `N papers in archive` / `Showing X of Y papers`,
  plus a `No papers match your search` empty state.
- **Standalone papers** — every file in `papers/*.html` embeds its own
  `<style>`, works offline (except MathJax CDN), prints cleanly, and links
  back with `<a href="../index.html">&larr; Back to Archive</a>`.
- **MathJax per paper** — LaTeX via `$…$` / `$$…$$` (and `\(…\)` / `\[…\]`).
  The homepage itself loads no MathJax, so it stays fast.
- **Zero-dependency sync helper** — `tools/sync_papers.py` scans `papers/`,
  suggests title / description / problem count from the HTML, and inserts
  new entries into `index.html` idempotently.
- **Accessible + responsive + print-friendly** — skip link, `aria-pressed`
  filters, `aria-live` catalogue, keyboard focus rings, mobile layout,
  and `@media print` rules.

---

## Live demo / preview

No build required. Pick one:

```bash
# fastest — just open the file
xdg-open index.html        # Linux
open index.html            # macOS
start index.html           # Windows

# or serve locally (recommended — closer to GitHub Pages behaviour)
python3 -m http.server 8000
# then visit http://localhost:8000/
```

---

## Repository structure

```text
/
├── index.html                  # library homepage + PAPER DATABASE metadata array
├── papers/
│   ├── machines_olympiad.html
│   ├── logistic_regression.html
│   ├── linear_regression_advanced.html
│   ├── logistic_regression_advanced.html
│   ├── naive_bayes_quiz.html
│   └── example_paper.html      # minimal template — copy it for new papers
├── assets/
│   ├── css/shared.css          # homepage stylesheet (papers are self-contained)
│   ├── js/archive.js           # catalogue rendering, search, filters
│   └── images/                 # static images (currently empty / reserved)
├── tools/
│   └── sync_papers.py          # scan papers/ → insert missing entries into index.html
├── sync_papers.py              # duplicate of tools/sync_papers.py kept at root for convenience
├── ARCHITECTURE.md             # how the system works internally
├── CONTRIBUTIONS.md            # how to contribute papers, fixes, features
├── JOURNEY.md                  # how this project was built, step by step
└── README.md                   # this file
```

Key principle: **paper content lives only in `papers/*.html`.**
`index.html` holds just metadata (one object per paper). `assets/` holds
only homepage chrome. Papers never import `assets/` — they are portable.

---

## How it works (30-second version)

1. `index.html` defines a global `const papers = [ … ]` array
   (marked `PAPER DATABASE`) with one object per paper: `title`, `file`,
   `category`, `level`, `difficulty`, `problems`, `year`, `description`.
2. `assets/js/archive.js` reads that array, renders an `<li>` card per paper
   into `<ol id="catalogue">`, and wires up the search box + filter buttons.
3. Clicking **Read paper** follows the relative `file` link verbatim,
   e.g. `papers/machines_olympiad.html` — a full standalone document.
4. Each paper embeds its own CSS + MathJax snippet, so it renders correctly
   with zero shared dependencies.

See [ARCHITECTURE.md](ARCHITECTURE.md) for the full data-flow, file
contracts, and design decisions.

---

## Adding a new paper

### Option A — manual (3 steps)

1. **Create the HTML file** in `papers/`, e.g. `papers/newtonian_mechanics.html`.
   Easiest: copy the template:
   ```bash
   cp papers/example_paper.html papers/newtonian_mechanics.html
   ```
   Keep it standalone: embed its `<style>`, use the MathJax snippet below,
   and include the top nav:
   ```html
   <a href="../index.html">&larr; Back to Archive</a>
   ```
2. **Add one entry** to the `papers` array in `index.html` (marked `PAPER DATABASE`):
   ```javascript
   {
     title: "Newtonian Mechanics — Problem Set",
     file: "papers/newtonian_mechanics.html",
     category: "Physics",
     level: "Class 11 · Olympiad",
     difficulty: "Intermediate",
     problems: 10,
     year: "2026",
     description: "Short description shown on the homepage card."
   }
   ```
3. **Done.** Refresh `index.html`. Numbering, counts, search and filters
   update automatically. No other file needs editing.

> **Relative paths only.** Use `papers/x.html` and `assets/…` — never
> leading-slash paths like `/papers/x.html` — so the site works under
> `https://<username>.github.io/<repository-name>/`.

### Option B — assisted with `sync_papers.py`

The helper finds HTML files in `papers/` missing from `index.html` and
prompts for metadata, pre-filling suggestions parsed from each file
(`<title>`, `<meta name="description">`, `Problem N` headings).

```bash
# preview what would be added (no writes, no prompts)
python3 tools/sync_papers.py --dry-run

# interactively add missing papers
python3 tools/sync_papers.py

# also consider example_paper.html (skipped by default)
python3 tools/sync_papers.py --include-template

# run against a different checkout
python3 tools/sync_papers.py --root /path/to/problem-library
```

Behaviour: scans `papers/*.html` (sorted by filename), compares against
`file:` values in `const papers = […]`, prompts per new file, then inserts
new entries before the closing `]` while preserving the rest of
`index.html` byte-for-byte. Re-runs are idempotent — already-registered
files are never duplicated. `Ctrl-C` aborts without writing.

---

## Metadata reference

Each object in the `papers` array:

| Field         | Type     | Required | Example                                | Notes |
|---------------|----------|----------|----------------------------------------|-------|
| `title`       | string   | yes      | `"Machines — Olympiad Problem Set"`    | Card heading; also used in search + aria-label. |
| `file`        | string   | yes      | `"papers/machines_olympiad.html"`      | Relative path, verbatim into `<a href>`. Must match actual file. |
| `category`    | string   | yes      | `"Physics"`, `"Mathematics / Machine Learning"` | Drives filter matching (substring, case-insensitive, on `category + level`). |
| `level`       | string   | no       | `"Class 10 · Olympiad"`, `"Advanced"`  | Shown in classification line; also filter-matched. |
| `difficulty`  | string   | no       | `"Advanced"`, `"easy"`                 | Shown in facts line; searched. Free text, but keep values consistent. |
| `problems`    | number   | no       | `12`                                   | Shown as `12 problems` in facts line. Must be an integer if set. |
| `year`        | string   | no       | `"2026"`                               | Shown in facts line. |
| `description` | string   | no       | `"Rigorous problems on …"`             | Card body text; searched. Keep to 1–2 sentences. |

### Filter routing

`assets/js/archive.js` → `paperMatchesCategory()`:

- `All` matches everything.
- `Physics`, `Mathematics`, `Computer Science`, `Machine Learning` match if
  the lowercased `category + " " + level` contains that token. So
  `category: "Mathematics / Machine Learning"` joins **both** filters.
- `Other` matches papers containing **none** of the four known tokens —
  e.g. `category: "Other"` or anything bespoke.

To add a new filter bucket, edit the `FILTERS` array in `archive.js` and
extend the `known` list in the `Other` branch.

### Changing metadata

Edit the corresponding object in the `papers` array in `index.html` —
`title`, `category`, `level`, `difficulty`, `problems`, `year`,
`description`. Save, refresh. Nothing else to rebuild.

### MathJax snippet (for papers)

```html
<script>
MathJax = {
  tex: {
    inlineMath: [['$', '$'], ['\\(', '\\)']],
    displayMath: [['$$', '$$'], ['\\[', '\\]']]
  }
};
</script>
<script async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
```

The homepage itself needs no MathJax.

---

## Paper authoring guide

Start from `papers/example_paper.html`. It demonstrates every pattern:

- **Document shell** — `<!DOCTYPE html>`, `<meta charset>`, `<meta viewport>`,
  `<title>`, `<meta name="description">` (reused by `sync_papers.py` as the
  description suggestion).
- **Embedded stylesheet** — `:root` tokens (`--ink`, `--paper`, `--muted`,
  `--hair`), serif body, `.sheet` column (`max-width: 44rem`), double-rule
  masthead, `.problem` blocks, `.parts` subparts `(a)–(d)`,
  `.solution` left-border blocks, `.mark` labels, focus + responsive +
  print rules. Copy and adapt; do not link `assets/css/shared.css` —
  papers must stay standalone.
- **Top nav** — `<nav class="topnav">` with `Back to Archive`
  (`../index.html`) + anchor to `#solutions`.
- **Header block** — `.paper-head` with kicker, `<h1>`, sub-line
  (`N problems · Difficulty · minutes`), and an `id-grid`
  (Name / Date / Class / Score).
- **Instructions + Problems** — `<h2 class="section">` sections;
  each problem is `<article class="problem"><h3>Problem N <span class="mark">`
  with optional `<ol class="parts">`, `<figure>`/inline SVG, and display math.
- **Solutions** — `<section id="solutions">` with `.solution` divs.
- **Footer** — back links + `End of paper.` + `Made by Reman Dey` credit.

Conventions: one concept per problem, marks in `[N marks]`, SVG for simple
diagrams (no external images), `mjx-container` horizontal-scroll guard for
long display equations on mobile.

---

## Homepage catalogue guide

- `index.html` skeleton: skip link → `.archive-header` masthead →
  `main.archive-main` → `section.controls` (search + `<ul id="filters">`) →
  `<ol id="catalogue">` (populated by JS) → `#no-results` + `#archive-count`
  → `.archive-footer` → `PAPER DATABASE` script → `archive.js`.
- `archive.js` (IIFE, strict mode, no dependencies): `FILTERS` constant,
  `normalise()` lowercasing, `paperMatchesCategory()` / `paperMatchesQuery()`
  (all query tokens must match), `factsLine()` / `classificationLine()`,
  `render()` (rebuilds `<li class="paper-entry">` cards with zero-padded
  numbers, title, classification, facts, description, `Read paper` link),
  `buildFilters()` (generates buttons with `aria-pressed`).
- Cards use `textContent` (not `innerHTML`), so metadata with `<`, `&`,
  quotes renders safely.
- Search input listens on `input` events; filters re-render on click.
  Catalogue has `aria-live="polite"`; count uses `role="status"`.

---

## Styling and theme

- `assets/css/shared.css` — single homepage stylesheet. Black-and-white
  academic theme: serif body, double-rule header/footer, bordered search,
  toggle filter buttons (inverted when active), grid catalogue entries
  (`3rem 1fr` number + body), solid black `Read paper` buttons (full-width
  on mobile), muted italic metadata.
- CSS variables (`--ink`, `--paper`, `--muted`, `--rule`, `--hairline`,
  `--max-width: 44rem`, `--serif`, `--sans`) at the top make re-theming a
  one-place edit.
- Papers intentionally **do not** use this file — each embeds its own copy
  of the sheet styles so a paper can be downloaded / emailed / hosted alone.

---

## Deploying to GitHub Pages

1. Push this folder to a GitHub repository.
2. Go to **Settings → Pages → Build and deployment → Deploy from branch**.
3. Select branch (e.g. `main`) and folder `/ (root)`. Save.
4. Open `https://<username>.github.io/<repository-name>/`.

No install, build, server, or environment variable is required. The only
network dependency at runtime is the MathJax CDN inside papers.

---

## Local development

```bash
git clone <your-repo-url> problem-library
cd problem-library
python3 -m http.server 8000
# edit papers/*.html, index.html, assets/…
# refresh the browser — no build step
python3 tools/sync_papers.py --dry-run   # check catalogue sync
```

Validate quickly: open DevTools console (no errors), test search
(e.g. `logistic`), click each filter, click every `Read paper` link,
resize to 360 px, print-preview one paper.

---

## Accessibility, responsive, print

- Skip link, semantic landmarks (`header`/`main`/`footer`/`nav`/`section`),
  labelled search, `aria-pressed` filters, `aria-live` catalogue,
  visible `:focus-visible` outlines, ≥44 px touch targets.
- Single-column `44rem` measure; catalogue collapses to one column under
  560 px; display equations scroll horizontally instead of overflowing.
- Print stylesheets on both homepage and papers hide navigation/search/
  buttons and reset to clean black-on-white output.

---

## Troubleshooting / FAQ

| Symptom | Cause / fix |
|---|---|
| Paper link 404 on GitHub Pages | `file` uses a leading slash or wrong case. Must be exactly `papers/name.html`, relative, case-matching. |
| New paper not listed | No entry in the `papers` array yet — add manually or run `tools/sync_papers.py`. |
| Math not rendering | Missing MathJax snippet, or offline. Homepage intentionally has no MathJax — check inside the paper file. |
| Filter shows paper in wrong bucket | Category/level text contains (or lacks) the filter token. See [Filter routing](#filter-routing). |
| Styles broken | `index.html` must reference `assets/css/shared.css` relatively; papers must embed their own `<style>`. |
| `sync_papers.py` says `const papers = [` not found | `index.html` array was renamed/removed. Restore the `const papers = [` marker. |
| Duplicate root `sync_papers.py` vs `tools/sync_papers.py` | Both copies are currently identical; canonical one is `tools/sync_papers.py`. Keep them in sync or remove the root copy. |

---

## Further reading

- [ARCHITECTURE.md](ARCHITECTURE.md) — components, data flow, contracts, constraints, scaling notes.
- [CONTRIBUTIONS.md](CONTRIBUTIONS.md) — how to add papers, report issues, propose features, style rules.
- [JOURNEY.md](JOURNEY.md) — how this project was designed and built.

---

## License / reuse

No license file is currently declared. If you plan to accept external
contributions or publish widely, add a `LICENSE` (e.g. MIT / CC-BY for
problem content) and reference it here. Until then, treat all content as
all-rights-reserved to the repository owner.
