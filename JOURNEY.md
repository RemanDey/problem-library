# JOURNEY — How This Was Made

The story of how a folder of HTML question papers became a searchable,
deploy-anywhere problem archive — the goals, the decisions, the dead ends
avoided, and what comes next.

---

## Table of contents

- [1. The spark](#1-the-spark)
- [2. Constraints first](#2-constraints-first)
- [3. Building in phases](#3-building-in-phases)
- [4. Decisions and trade-offs](#4-decisions-and-trade-offs)
- [5. The sync-script story](#5-the-sync-script-story)
- [6. What the archive holds today](#6-what-the-archive-holds-today)
- [7. Lessons learned](#7-lessons-learned)
- [8. What's next](#8-whats-next)

---

## 1. The spark

The need was simple: a personal library of Physics / Mathematics / Machine
Learning problem sets — olympiad-style, exam-like, printable — that could
live on GitHub Pages and be shared with a link.

Existing options all pulled in the wrong direction: LMS platforms wanted
accounts and databases; static-site generators wanted Node toolchains;
Google Docs / PDFs wanted proprietary editors and broke math rendering.
The goal was something a teacher could fork, edit in Notepad, and publish
in minutes.

So the brief became: **a catalogue page + standalone paper pages, zero
backend, zero build, math that just works.**

---

## 2. Constraints first

Before writing code, the constraints were fixed — they shaped everything:

1. **GitHub Pages, branch-and-root deploy.** No actions, no Jekyll
   processing to fight, no environment variables. Anything committed to
   `/ (root)` must work as-is.
2. **Subpath-safe.** The site lives at
   `https://<user>.github.io/<repo>/`, not the domain root — so every URL
   had to be relative (`papers/x.html`, `assets/…`, `../index.html`).
3. **Papers must survive alone.** A paper emailed as a single file, opened
   from disk, or printed had to look right. That ruled out shared
   stylesheets or JS for papers — each embeds its own CSS.
4. **No toolchain for authors.** Copy a template, write problems, add one
   metadata entry. If a step needed npm, it was the wrong step.
5. **`file://`-safe homepage.** Double-clicking `index.html` with no
   server had to show the catalogue — which ruled out `fetch("papers.json")`
   (blocked by CORS on `file://`) and fixed the inline `papers` array design.
6. **Readable math.** LaTeX `$…$` / `$$…$$` via MathJax CDN — but only
   inside papers, so the homepage stays instant.

These six lines are why the architecture looks the way it does. See
[ARCHITECTURE.md](ARCHITECTURE.md) for how each is enforced.

---

## 3. Building in phases

**Phase 1 — The paper template (`papers/example_paper.html`).**
Started at the leaves, not the root: one beautiful standalone document.
Serif body, `44rem` measure, double-rule masthead, candidate `id-grid`,
uppercase `Instructions` / `Problems` / `Solutions` sections,
`article.problem` blocks with `[marks]`, `(a)–(d)` subparts, an inline-SVG
figure, left-border solutions, MathJax snippet, back-nav top and bottom,
responsive + print rules. Four sample problems (integral, quadratic,
incline, induction) proved every pattern. Every later paper is a copy of
this file with the content swapped.

**Phase 2 — Real papers.** The template was cloned into subject sets:
`machines_olympiad.html` (12 pulley/lever/incline problems),
`logistic_regression.html` (8 probability/log-odds/cross-entropy problems),
`linear_regression_advanced.html` (least squares, MLE/MAP, ridge),
`logistic_regression_advanced.html` (convexity, separability, Newton),
`naive_bayes_quiz.html` (16-question quiz). Writing real content early
exposed template gaps (long display equations on mobile, quiz vs problem-set
metadata) before the catalogue was built.

**Phase 3 — The homepage (`index.html` + `assets/`).**
A static shell (masthead, search, filter bar, empty `<ol>`, count, footer)
plus an inline `PAPER DATABASE` array — one object per paper. All rendering
moved into `assets/js/archive.js` (vanilla IIFE: filter + tokenised search
+ card render + counts), all styling into `assets/css/shared.css` (B/W
academic theme, tokens in `:root`, mobile + print layers). Key detail:
cards render with `textContent`, numbering is generated (`01…`), and links
use the `file` field verbatim.

**Phase 4 — The sync helper (`tools/sync_papers.py`).**
Manual registration worked but didn't scale: authors forgot entries,
mistyped filenames, miscounted problems. The script closes the loop — scan
`papers/`, diff against the array with string-aware bracket matching,
suggest title/description/count from the HTML, prompt for the rest, patch
`index.html` surgically. Idempotent, dry-runnable, stdlib-only.

**Phase 5 — Documentation (this set of files).**
`README.md` grew from a quick-start into a full manual; `ARCHITECTURE.md`
captured the why-behind-the-what; `CONTRIBUTIONS.md` lowered the bar for
the next author; this `JOURNEY.md` wrote down the story while it was fresh.

All of it landed in a single early commit (`adding files`) — the whole
archive, template to tooling, designed as one coherent piece rather than
assembled over months.

---

## 4. Decisions and trade-offs

| Decision | Alternatives rejected | Why this won |
|---|---|---|
| Inline `papers` array in `index.html` | `papers.json` + `fetch` | `fetch` fails on `file://`; inline works everywhere with zero code. |
| Papers embed their own CSS | Shared `assets/css` link | Shared links break the survive-alone guarantee; duplication (~60 lines) is cheap. |
| Full-page paper navigation | iframes / modal preview | Full pages bookmark, print, and work with back-button; iframes fight printing + deep-linking. |
| Substring filter matching | Strict enums / tags | `Mathematics / Machine Learning` joining two filters falls out free; authors never learn a taxonomy. |
| MathJax CDN per paper | KaTeX bundle / self-host | Zero vendoring, always current; graceful degradation to raw TeX offline. |
| Python sync script, not JS | In-browser admin UI | Authors already have Python; a CLI that patches the file beats a UI that can't save on static hosting. |
| B/W serif theme | Colourful modern theme | Prints perfectly, looks academic, zero font downloads, never clashes with math. |

The through-line: **favour the thing with fewer moving parts**, even when
it means mild duplication (embedded CSS, duplicate sync script at root).

---

## 5. The sync-script story

The script deserves its own section because it encodes the project's
philosophy: automate the boring reconciliation, keep the human in charge
of judgment.

Early versions could have auto-registered everything silently — but
`category`, `level`, and `difficulty` need human intent (is this
`Physics` or `Other`? `Advanced` or `Introductory`?). So the script
**suggests what it can parse** (title, description, count — all
mechanically extractable) and **prompts for what it can't** (categorisation,
pedagogy). Enter accepts the suggestion; anything can be overridden.

Implementation notes: the bracket-matcher is string-aware so `]` inside a
description can't corrupt the parse; `suggest_problems` counts distinct
`Problem N` numbers so solutions re-mentioning problems don't inflate the
count; patching preserves the file byte-for-byte outside the array so hand
formatting and comments survive; `--dry-run` and `Ctrl-C`-safety mean it
never writes unexpectedly.

---

## 6. What the archive holds today

- **Homepage** — searchable, filterable catalogue with live counts.
- **6 papers** — machines olympiad, logistic regression (×2), linear
  regression advanced, naive Bayes quiz, plus the example template.
- **Theme** — one homepage stylesheet, per-paper embedded styles.
- **Tooling** — sync helper (canonical `tools/`, convenience root copy).
- **Docs** — README (manual), ARCHITECTURE (internals), CONTRIBUTIONS
  (onboarding), JOURNEY (this story).

Total runtime dependencies: a browser. Total build steps: zero.

---

## 7. Lessons learned

1. **Constraints are a design tool.** Fixing relative-paths, standalone
   papers, and `file://`-safety up front eliminated whole classes of
   framework temptation.
2. **Template first, catalogue second.** Writing real papers against the
   template surfaced requirements (quiz metadata, mobile math overflow)
   that a catalogue-first build would have missed.
3. **Duplication can be a feature.** Embedded paper CSS looks redundant
   until someone emails a single `.html` file and it just works.
4. **Suggest, don't decide.** The sync script's accept-with-Enter pattern
   is the right automation level for authorial metadata.
5. **Docs are part of the build.** A template without a style guide, or a
   filter without documented routing, is a trap for the next contributor.

---

## 8. What's next

Ideas on the table (all must respect the static-only rule):

- **Validation check** — CI or script asserting every `file:` exists and
  every paper is registered; catches the two most common authoring errors.
- **Sorting** — by year / difficulty / problem count, client-side only.
- **Difficulty normalisation** — unify `easy` vs `Introductory` vocabulary.
- **More papers** — thermodynamics, probability, calculus, transformers —
  the archive grows one template-copy at a time.
- **Single sync script** — remove the root duplicate, keep `tools/` canonical.
- **License** — declare one (MIT / CC-BY) so contributions have clear terms.

If any of that sounds like you, read [CONTRIBUTIONS.md](CONTRIBUTIONS.md)
and send a PR. The archive's next chapter is a copied template and a good
problem set.
