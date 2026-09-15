# CONTRIBUTIONS — How to Contribute

Thank you for wanting to improve the Problem Archive. Contributions of new
problem papers, fixes, styling, docs, and tooling are all welcome.

This project is intentionally low-tech (static HTML/CSS/JS + one Python
helper), so contributing requires nothing beyond a text editor, a browser,
and optionally Python 3.

---

## Table of contents

- [1. Ways to contribute](#1-ways-to-contribute)
- [2. Ground rules](#2-ground-rules)
- [3. Adding a new problem paper](#3-adding-a-new-problem-paper)
- [4. Paper style guide](#4-paper-style-guide)
- [5. Editing homepage metadata](#5-editing-homepage-metadata)
- [6. Working on the catalogue (`index.html`, `archive.js`, `shared.css`)](#6-working-on-the-catalogue-indexhtml-archivejs-sharedcss)
- [7. Working on `sync_papers.py`](#7-working-on-sync_paperspy)
- [8. Suggesting / reporting issues](#8-suggesting--reporting-issues)
- [9. Pull-request checklist](#9-pull-request-checklist)
- [10. Review process](#10-review-process)
- [11. Code of conduct](#11-code-of-conduct)

---

## 1. Ways to contribute

| Contribution | Effort | What to do |
|---|---|---|
| **New problem paper** | ~30–60 min | Copy `papers/example_paper.html`, write problems, register in `index.html` (§3). |
| **Fix a typo / error** | ~5 min | Edit the paper directly; keep solutions consistent. |
| **Improve metadata** | ~5 min | Better title/description/category in the `papers` array. |
| **Homepage / theme fix** | ~15–60 min | Edit `assets/css/shared.css` or `assets/js/archive.js` (§6). |
| **Tooling** | varies | Extend `tools/sync_papers.py` (§7). |
| **Docs** | ~15 min | Fix `README.md` / `ARCHITECTURE.md` / `JOURNEY.md` / this file. |

No contribution is too small. Typo fixes are first-class PRs.

---

## 2. Ground rules

1. **Keep it static.** No backends, databases, build tools, npm packages,
   or frameworks. Vanilla HTML/CSS/JS + Python-stdlib helper only.
2. **Keep papers standalone.** A paper must render with zero project files
   besides itself (plus the MathJax CDN). Never `<link>` to `assets/`
   from a paper.
3. **Relative paths only.** `papers/x.html`, `assets/…`, `../index.html`.
   Never `/papers/x.html` or hardcoded domains.
4. **One paper = two touches max.** New `papers/name.html` + one metadata
   object in `index.html`. No other file should need editing.
5. **Match the academic theme.** Black-and-white, serif, double rules,
   uppercase section heads. No colours, gradients, or webfonts.
6. **Be original or licensed.** Only submit problems you wrote or that are
   compatibly licensed / public domain. Credit sources in the paper footer
   or description where applicable.

---

## 3. Adding a new problem paper

### Step 1 — Create the file

```bash
cp papers/example_paper.html papers/your_topic.html
```

Use lowercase `snake_case` filenames (`newtonian_mechanics.html`,
`probability_basics.html`). Keep the `.html` extension, keep it inside
`papers/`.

### Step 2 — Write the content

Replace the header, instructions, problems, and solutions. Keep the
skeleton, class names, top nav, and MathJax snippet intact (see §4).

Minimum requirements for a new paper:

- [ ] Meaningful `<title>` (used as sync suggestion + browser tab).
- [ ] `<meta name="description">` — one sentence (used as sync suggestion).
- [ ] Header block with problem count, difficulty, time.
- [ ] Numbered `Problem 1…N` headings (`<article class="problem">` each).
- [ ] `../index.html` back-link in nav **and** footer.
- [ ] MathJax snippet present if the paper uses `$…$` math.
- [ ] Solutions section (or an explicit `Solutions to follow` note).

### Step 3 — Register it in `index.html`

**Manual:**

```javascript
{
  title: "Your Topic — Problem Set",
  file: "papers/your_topic.html",
  category: "Physics",              // or "Mathematics", "Mathematics / Machine Learning", …
  level: "Class 11 · Olympiad",
  difficulty: "Intermediate",       // keep vocabulary consistent
  problems: 10,                     // integer, must match the paper
  year: "2026",
  description: "One or two sentences shown on the homepage card."
}
```

**Assisted (recommended for batches):**

```bash
python3 tools/sync_papers.py --dry-run   # see what's missing
python3 tools/sync_papers.py             # prompted; Enter accepts suggestions
```

The script suggests title/description/problem-count from the HTML; you
still fill in `category`, `level`, `difficulty` by hand.

### Step 4 — Verify

- [ ] `index.html` shows the new card with correct title/counts.
- [ ] `Read paper` opens the paper; `Back to Archive` returns.
- [ ] Search finds it (try a distinctive word from the title).
- [ ] Correct filter bucket highlights it (see filter routing in README).
- [ ] No console errors; equations render; print preview is clean.
- [ ] Mobile width (~360 px) has no horizontal overflow.

---

## 4. Paper style guide

Derived from `papers/example_paper.html` — when in doubt, copy it.

**Structure:**

```html
<nav class="topnav">…Back to Archive…Solutions…</nav>
<main class="sheet">
  <header class="paper-head">…title, sub-line, id-grid…</header>
  <section><h2 class="section">Instructions</h2><ol>…</ol></section>
  <section>
    <h2 class="section">Problems</h2>
    <article class="problem">
      <h3>Problem 1 <span class="mark">[5 marks]</span></h3>
      <p>…$inline math$…</p>
      <ol class="parts"><li>…</li></ol>
    </article>
    …
  </section>
  <section><h2 class="section" id="solutions">Solutions</h2>
    <div class="solution"><p><strong>Solution 1.</strong>…</p></div>
  </section>
  <footer>…Back links…End of paper…Made by Reman Dey…</footer>
</main>
```

**Do:**

- Use `$…$` inline, `$$…$$` display math; keep lines under ~80 chars.
- Put marks in `[N marks]`; state calculators / time allowed up front.
- Prefer inline SVG for simple diagrams (scales, prints, needs no files).
- Keep class names (`problem`, `parts`, `solution`, `mark`, `sheet`,
  `topnav`, `paper-head`, `section`) — tooling and CSS rely on them.

**Don't:**

- Don't link `assets/css/shared.css` or any external stylesheet.
- Don't hotlink images for essential content (they break offline/printing).
- Don't use colour to convey meaning (papers print black-and-white).
- Don't paste problems you don't have rights to.

---

## 5. Editing homepage metadata

- Titles: `Topic — Problem Set` with an em dash; keep under ~60 chars.
- Descriptions: 1–2 sentences, plain text (no HTML — rendered via
  `textContent`), no trailing hype.
- Categories: prefer existing buckets (`Physics`, `Mathematics`,
  `Computer Science`, `Machine Learning`, `Other`, or combinations like
  `Mathematics / Machine Learning`). New buckets require an `archive.js`
  filter change — mention it in your PR.
- Difficulty: reuse the vocabulary already in the array
  (`Introductory`, `Intermediate`, `Advanced`, `easy`, …). Normalising to
  one capitalisation is a welcome cleanup PR.
- `problems` must be an integer matching the paper's actual count.
- `year` is the publication year string (`"2026"`).

---

## 6. Working on the catalogue (`index.html`, `archive.js`, `shared.css`)

- **`index.html`**: shell + data only. Don't hand-write `<li>` cards —
  they are generated. Don't rename the `papers` variable or the DOM ids
  (`catalogue`, `search`, `filters`, `archive-count`, `no-results`)
  without updating `archive.js` and `sync_papers.py` together.
- **`assets/js/archive.js`**: vanilla ES5 IIFE. Keep it dependency-free
  and `file://`-safe (no `fetch`). Render text with `textContent`.
  Null-guard any new DOM lookups. Update the `FILTERS` array **and** the
  `Other`-branch `known` list together when adding subjects.
- **`assets/css/shared.css`**: edit `:root` tokens for theming; keep the
  B/W academic look; test 360 px mobile + print preview for every change.
  Focus styles (`:focus-visible`) must remain visible.

Test matrix for catalogue PRs: type a query, clear it, click every filter,
open every `Read paper` link, resize to mobile, print-preview homepage,
open `index.html` via `file://` (no server) to confirm nothing needs HTTP.

---

## 7. Working on `sync_papers.py`

- Canonical location is `tools/sync_papers.py`. A duplicate exists at repo
  root (`sync_papers.py`) — keep both identical or, preferably, delete the
  root copy in your PR and note it.
- Stdlib only — no third-party imports.
- Preserve idempotence (re-run adds nothing) and byte-for-byte preservation
  of the rest of `index.html`.
- Test: `python3 tools/sync_papers.py --dry-run`, then copy the template to
  a temp name, run the real sync, verify the diff, run again (expect
  `Already in sync`), and delete the temp file.

---

## 8. Suggesting / reporting issues

Open a GitHub issue with:

- **Paper request**: topic, level, what should be covered.
- **Bug**: page/file involved, expected vs actual, browser + steps to
  reproduce, screenshot if visual.
- **Typo/error in a problem**: paper + problem number + correction
  (or the corrected working).
- **Feature**: problem it solves, proposed behaviour, why it stays static.

If you're unsure, open the issue first — a short discussion beats a
rejected PR.

---

## 9. Pull-request checklist

- [ ] Scope is narrow (one paper, one fix, or one feature).
- [ ] New paper? File in `papers/` + entry in `papers` array + verified (§3 Step 4).
- [ ] Relative paths only; papers standalone; theme intact.
- [ ] No build artefacts, no binaries, no minified dumps.
- [ ] `python3 tools/sync_papers.py --dry-run` reports `Already in sync`
      (or explains why not).
- [ ] PR description: what changed, why, how you tested
      (browser, search/filter clicks, print preview).

---

## 10. Review process

1. Maintainer checks scope, static-site constraints, paths, and rendering.
2. Problem papers get a content skim (numbering, marks, solutions match).
3. Small fixes merge fast; larger features may ask for a smaller first PR.
4. Once approved, the maintainer merges. No squash requirements — keep
   history readable with imperative commit messages
   (`Add thermodynamics problem set`).

---

## 11. Code of conduct

Be kind, precise, and constructive. Critique the work, not the author.
No harassment, plagiarism, or spam. Problem content must be your own or
compatibly licensed — don't submit textbook scans or copyrighted sets.
Maintainers may close issues/PRs that violate these terms.

Happy contributing — every good problem set makes the archive better.
