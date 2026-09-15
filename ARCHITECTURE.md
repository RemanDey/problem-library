# ARCHITECTURE — Physics / Mathematics Problem Archive

This document explains **how the system works**: components, data flow,
contracts between files, rendering logic, and the constraints that shaped
every decision.

Audience: contributors who want to modify the catalogue, theme, filters,
or tooling without breaking the static-site guarantees.

---

## Table of contents

- [1. Design goals](#1-design-goals)
- [2. Component map](#2-component-map)
- [3. Data flow](#3-data-flow)
- [4. Component deep-dives](#4-component-deep-dives)
  - [4.1 `index.html` — homepage + metadata store](#41-indexhtml--homepage--metadata-store)
  - [4.2 `assets/js/archive.js` — catalogue engine](#42-assetsjsarchivejs--catalogue-engine)
  - [4.3 `assets/css/shared.css` — homepage theme](#43-assetscsssharedcss--homepage-theme)
  - [4.4 `papers/*.html` — standalone documents](#44-papershtml--standalone-documents)
  - [4.5 `tools/sync_papers.py` — catalogue synchroniser](#45-toolssync_paperspy--catalogue-synchroniser)
- [5. Contracts and invariants](#5-contracts-and-invariants)
- [6. Key algorithms](#6-key-algorithms)
- [7. Dependency and runtime profile](#7-dependency-and-runtime-profile)
- [8. Failure modes](#8-failure-modes)
- [9. Scaling and extension points](#9-scaling-and-extension-points)
- [10. Glossary](#10-glossary)

---

## 1. Design goals

| # | Goal | How it is enforced |
|---|------|--------------------|
| G1 | Deploy to GitHub Pages with zero config | No server code, no build, no env vars; only relative URLs. |
| G2 | Each paper is independently usable | Papers embed CSS, use CDN MathJax, link home via `../index.html`. No import from `assets/`. |
| G3 | Adding a paper touches ≤ 2 files | New `papers/x.html` + one object in the `papers` array (or run the sync script). |
| G4 | No toolchain for readers or authors | Authors need a text editor + browser + (optionally) Python 3 for the helper. |
| G5 | Accessible, printable, fast | Semantic HTML, ARIA wiring, `@media print`, no framework payload, MathJax only where needed. |

Non-goals (deliberate): no user accounts, no server-side search, no WYSIWYG
editor, no PDF pipeline, no client-side routing.

---

## 2. Component map

```text
                    ┌─────────────────────────────────┐
                    │           index.html            │
                    │  static shell + PAPER DATABASE  │
                    │  const papers = [ {…}, … ]      │
                    └────────┬────────────┬───────────┘
                             │ metadata   │ shell (DOM ids)
                             ▼            ▼
              ┌──────────────────┐  ┌──────────────────────┐
              │ assets/js/       │  │ assets/css/          │
              │ archive.js       │  │ shared.css           │
              │ read papers[] ──► │  │ styles shell + cards │
              │ render catalogue │  └──────────────────────┘
              │ search + filters │
              └────────┬─────────┘
                       │ relative <a href="papers/x.html">
                       ▼
              ┌──────────────────┐     ┌──────────────────┐
              │ papers/*.html    │     │ tools/           │
              │ standalone docs  │◄────│ sync_papers.py   │
              │ own <style> +    │ scan│ parses papers/,  │
              │ MathJax CDN      │     │ patches array    │
              └──────────────────┘     └──────────────────┘
```

| Component | Role | Depends on |
|---|---|---|
| `index.html` | Page shell (header, search, filters, catalogue mount points) + the `papers` metadata array | `assets/css/shared.css`, `assets/js/archive.js` |
| `assets/js/archive.js` | Reads global `papers`, renders cards, filters, search, counts | Global `papers` defined before it loads; DOM ids `catalogue`, `search`, `archive-count`, `no-results`, `filters` |
| `assets/css/shared.css` | All homepage styling | Nothing (pure CSS, variables at `:root`) |
| `papers/*.html` | Self-contained question papers | MathJax CDN only (graceful without it — raw TeX remains readable) |
| `tools/sync_papers.py` (+ root duplicate) | Dev-time helper: detect unregistered papers, prompt, patch `index.html` | Python 3 stdlib only; parses `index.html` text |

---

## 3. Data flow

**Homepage load (read path):**

```text
1. Browser parses index.html shell
       │
2. Executes inline <script>: const papers = […]   (global data)
       │
3. Loads + executes assets/js/archive.js
       │
4. archive.js:
      buildFilters()  → creates 7 buttons (All, Physics, Mathematics,
                        Computer Science, Machine Learning, Electronics, Other)
     render()        → filters papers by (category × query)
                     → builds <li class="paper-entry"> per match
                       (number, title, classification, facts,
                        description, Read-paper link)
                     → updates #archive-count + #no-results
       │
5. User types / clicks → state (activeCategory, query) changes → render()
       │
6. User clicks "Read paper" → full-page navigation to papers/x.html
```

**Paper load (independent path):**

```text
papers/x.html → inline <style> applies → MathJax CDN typesets $…$/$$…$$
→ user reads / prints → "Back to Archive" returns to ../index.html
```

No fetch/XHR, no JSON file, no localStorage, no service worker.
The only cross-file runtime link is homepage → paper via plain anchors.

**Authoring (write path):**

```text
copy papers/example_paper.html → edit content
       │
       ├── manual: append object to papers[] in index.html
       │
       └── assisted: python3 tools/sync_papers.py
                       → scans papers/*.html
                       → diffs against file: values in papers[]
                       → prompts (with <title>/<meta>/Problem-N suggestions)
                       → inserts entries before closing ]
```

---

## 4. Component deep-dives

### 4.1 `index.html` — homepage + metadata store

Sections in order:

1. `<head>` — charset, viewport, title, meta description, stylesheet link
   (`assets/css/shared.css`, relative).
2. Skip link → `.archive-header` masthead (kicker, title, subtitle, meta).
3. `main.archive-main` → `section.controls` (visually-hidden catalogue
   heading, search `<label>` + `<input type="search" id="search">`,
   `<ul id="filters">` placeholder) → `<ol id="catalogue">` (empty —
   populated by JS) → `#no-results` (hidden) → `#archive-count` (status).
4. `.archive-footer` — static tagline.
5. Inline `<script>` — `const papers = […]`, marked `PAPER DATABASE`.
   This is the **single source of truth** for the catalogue. Keeping it
   inline (rather than `papers.json` + `fetch`) avoids CORS/`file://`
   fetch failures when double-clicking `index.html` locally.
6. `<script src="assets/js/archive.js">` — must load **after** the array.

The `file` field is used verbatim as the anchor `href`, which is why it
must be a relative path like `papers/x.html`.

### 4.2 `assets/js/archive.js` — catalogue engine

Plain IIFE, `"use strict"`, zero dependencies (~173 lines). State:

- `allPapers` — resolved from `window.papers` (fallback: bare `papers`).
- `activeCategory` (default `"All"`), `query` (lowercased input).

Constants: `FILTERS = ["All", "Physics", "Mathematics", "Computer Science",
"Machine Learning", "Electronics", "Other"]`.

Functions:

| Function | Behaviour |
|---|---|
| `normalise(s)` | `String(s ?? "").toLowerCase()` — all matching is case-insensitive. |
| `paperMatchesCategory(p, cat)` | `All` → true. `Other` → true iff `category + " " + level` contains none of the five known tokens. Otherwise substring test for the category token. |
| `paperMatchesQuery(p, q)` | Splits query on whitespace; **every** token must appear somewhere in `title + category + level + description + difficulty`. Empty query matches all. |
| `factsLine(p)` | Joins non-empty `problems + " problems"`, `difficulty`, `year` with `·`. |
| `classificationLine(p)` | Joins non-empty `category`, `level` with `·`. |
| `render()` | Clears `#catalogue`, appends one `<li class="paper-entry">` per visible paper (zero-padded index `01…`, `h2.paper-title`, `p.paper-classification`, `p.paper-facts`, `p.paper-desc`, `.read-row > a.btn-read`), updates count text (`N papers in archive` vs `Showing X of Y papers`), toggles `#no-results`. All text via `textContent` (XSS-safe). |
| `buildFilters()` | Rebuilds filter buttons; click sets `activeCategory`, updates `aria-pressed`, re-renders. |

Events: search `input` → `query = normalise(value.trim())` → `render()`.

### 4.3 `assets/css/shared.css` — homepage theme

Single stylesheet (~291 lines), no frameworks. Layers:

- **Tokens** — `:root` variables for ink/paper/muted/rule/hairline,
  `--max-width: 44rem`, serif + sans stacks.
- **Base** — box-sizing reset, text-size-adjust, serif body, focus-visible
  outlines, skip-link pattern.
- **Masthead/layout/controls** — double-rule header, centred `44rem`
  column, uppercase sans labels, bordered square search input, pill-less
  rectangular filter buttons (black inverted when `aria-pressed="true"`).
- **Catalogue** — `grid-template-columns: 3rem 1fr` entries with tabular
  numbers, uppercase titles, italic classifications, sans facts, right-
  aligned `Read paper` buttons.
- **Responsive** — under 560 px: single column, full-width buttons,
  slightly smaller body; display-math scroll guard.
- **Print** — hides header/controls/filters/buttons/footer; drops to 11 pt.

Papers do **not** load this file; they carry their own embedded copy of the
sheet styles so they render identically when detached.

### 4.4 `papers/*.html` — standalone documents

Contract for every paper:

- Valid standalone HTML: doctype, charset, viewport, `<title>`,
  `<meta name="description">`.
- Embedded `<style>` (copy from `example_paper.html`): tokens, `.topnav`,
  `.sheet`, `.paper-head`, `.id-grid`, `h2.section`, `.problem`,
  `.parts`, `figure`, `.solution`, `.mark`, footer, focus/responsive/print.
- MathJax config + CDN scripts (exact snippet in README).
- `<nav class="topnav">` with `../index.html` back-link and `#solutions`
  anchor; footer mirrors them plus `End of paper.` and the `Made by Reman Dey` credit.
- Content: `.paper-head` → `Instructions` → `Problems`
  (`article.problem > h3 + parts/figures/math`) → `#solutions` →
  `<footer>`.

`example_paper.html` is the reference implementation: 4 problems covering
integrals, quadratics, mechanics + inline SVG figure, induction; plus
matching solutions. New papers should preserve its class names so future
global tooling (e.g. problem counters) keeps working.

### 4.5 `tools/sync_papers.py` — catalogue synchroniser

Stdlib-only Python (~248 lines; an identical copy sits at repo root for
convenience — canonical location is `tools/`).

Pipeline:

1. **Locate** — resolve `--root`, require `index.html` + `papers/`.
2. **Enumerate** — sorted `papers/*.html`, minus `example_paper.html`
   unless `--include-template`.
3. **Diff** — find `const papers = [` via regex, bracket-match to the
   closing `]` with string-aware scanning; extract known `file:` values;
   `new = on-disk − registered`.
4. **Suggest** — per new file: title from `<title>` (entity-unescaped),
   description from `<meta name="description">` (either attribute order),
   problem count from distinct `Problem N` numbers (fallback: count of
   `class` attributes containing the exact `problem` token).
5. **Prompt** — interactive `ask()` per field (Enter accepts suggestion);
   title/category/problems validated non-empty/numeric; year defaults to
   current year. `--dry-run` stops before prompting. `Ctrl-C` aborts
   without writing.
6. **Patch** — serialise entries with `json.dumps` (unicode-safe),
   append before `]`, repairing a missing trailing comma on the previous
   entry; write file back. Rest of `index.html` preserved byte-for-byte.
   Idempotent: re-running finds zero new files.

---

## 5. Contracts and invariants

1. **Relative URLs only.** `papers/x.html`, `assets/…`, `../index.html`.
   No leading `/`, no absolute domain. (GitHub Pages subpath safety.)
2. **Catalogue data lives in exactly one place**: the `const papers = [`
   array in `index.html`. `archive.js` must not hardcode papers.
3. **DOM id contract**: `archive.js` requires `catalogue`; degrades
   gracefully if `search` / `archive-count` / `no-results` / `filters`
   are absent (null-guarded).
4. **Paper self-containment**: a paper must render correctly when opened
   directly, copied to another folder with its sibling assets absent, or
   printed. No `<link>` to `assets/`, no external images for essential
   diagrams (inline SVG preferred).
5. **Filter token contract**: adding a subject means updating both
   `FILTERS` and the `known` list in the `Other` branch, or `Other` will
   misclassify.
6. **`sync_papers.py` marker contract**: the regex `const\s+papers\s*=\s*\[`
   must keep matching `index.html`. Do not rename the variable without
   updating the script.
7. **Safe text rendering**: catalogue text must go through `textContent`,
   never `innerHTML`, because metadata is author-typed.

---

## 6. Key algorithms

**Substring category routing** (`paperMatchesCategory`): lowercases
`category + " " + level` once, then `indexOf` per filter token. Cost
O(F·L) per paper, trivial for hundreds of entries. Multi-membership
(e.g. `Mathematics / Machine Learning`) falls out naturally.

**Tokenised AND search** (`paperMatchesQuery`): query split on
`/\s+/`; paper matches iff every non-empty token is a substring of the
concatenated haystack. No ranking — filtered set preserves array order,
and visible numbering restarts at 01.

**String-aware bracket matching** (`find_array_bounds`): single pass over
`index.html` tracking `[` depth while skipping `'…"…`…`…'` literals and
escapes — robust against `]` characters inside titles/descriptions.

**Problem-count suggestion** (`suggest_problems`): distinct integers from
`Problem\s+(\d+)` (robust against solutions re-mentioning problems);
fallback counts `class` attributes whose token list includes exactly
`problem`.

---

## 7. Dependency and runtime profile

| Dependency | Where | Required? | Failure behaviour |
|---|---|---|---|
| Modern browser (ES5 JS, CSS grid) | homepage | yes | Catalogue empty on ancient browsers; papers (plain HTML/CSS) still readable. |
| MathJax 3 CDN (`jsdelivr`) | papers only | no | Equations show as raw TeX; rest of paper unaffected. |
| Python 3 (stdlib) | dev-time sync script | no | Manual catalogue editing always works. |

No cookies, no tracking, no backend calls, no localStorage. Page weight is
a few KB plus MathJax on paper pages.

---

## 8. Failure modes

- **Renamed `papers` variable / DOM ids** → `archive.js` renders nothing
  (empty catalogue, `0 papers in archive`). Fix: restore names.
- **Absolute `file` paths** → 404 under `user.github.io/repo/` subpaths.
- **Unescaped `]`/quotes in metadata** → sync script still parses (string-
  aware), but hand-edits should keep JSON-style quoting consistent.
- **MathJax offline** → raw `$…$` visible; acceptable degradation.
- **Duplicate sync scripts drift** — root `sync_papers.py` and
  `tools/sync_papers.py` are currently identical; canonical is `tools/`.
  If both are kept, update both or delete the root copy.

---

## 9. Scaling and extension points

- **Hundreds of papers**: current design holds — array order = display
  order, render is O(n). Past ~500 entries consider paginating `render()`
  or moving the array to a separate `papers.js` (still static, still
  `file://`-safe — unlike `fetch("papers.json")`).
- **New filters**: edit `FILTERS` + `known` list (see §5.5).
- **Sorting**: add a `<select>` + comparator in `render()` (by year,
  difficulty, problem count) — no data migration needed.
- **Tags/difficulty facets**: same pattern as categories; fields already
  searched.
- **PDF export**: rely on print CSS (`Ctrl+P → Save as PDF`); no pipeline
  to maintain.
- **Validation CI**: a 20-line check that every `file:` resolves to an
  existing `papers/*.html` and every `papers/*.html` (minus template) is
  registered would catch the two most common authoring errors.

---

## 10. Glossary

- **Catalogue** — the rendered list of papers on the homepage.
- **PAPER DATABASE** — the inline `const papers = […]` array; sole
  metadata store.
- **Standalone paper** — a `papers/*.html` file needing nothing but a
  browser (+ optional MathJax CDN) to render.
- **Facts line** — the `N problems · Difficulty · Year` card sub-line.
- **Classification line** — the `Category · Level` card sub-line.
- **Sync script** — `tools/sync_papers.py`, the dev-time reconciler.
