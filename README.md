# Physics / Mathematics Problem Archive

A **100% static, GitHub Pages–compatible** library of standalone HTML question papers.
No backend, no database, no build step, no frameworks — just HTML + CSS + JS + MathJax (CDN, papers only).

When you open the site you see a searchable catalogue; clicking **Read paper**
opens that paper as a normal independent page.

## Structure

```text
/
├── index.html               # library homepage (metadata + links only)
├── papers/
│   ├── machines_olympiad.html
│   ├── logistic_regression.html
│   └── example_paper.html   # minimal template — copy it for new papers
├── assets/
│   ├── css/shared.css       # homepage stylesheet (papers are self-contained)
│   └── js/archive.js        # catalogue rendering, search, filters
└── README.md
```

Paper contents live **only** in `papers/*.html`. `index.html` holds just metadata.

## Adding a new paper (3 steps)

1. **Create the HTML file** in `papers/`, e.g. `papers/newtonian_mechanics.html`.
   Easiest: copy `papers/example_paper.html` and replace the problems.
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
3. **Done.** No other file needs editing. Numbering, counts, search and
   filters update automatically.

Use **relative paths** (`papers/x.html`, `assets/...`) — never leading-slash
paths like `/papers/x.html` — so the site works under
`https://username.github.io/repository-name/`.

### Changing metadata

Edit the corresponding object in the `papers` array in `index.html`:
`title`, `category`, `level`, `difficulty`, `problems`, `year`, `description`.
Categories containing "Physics", "Mathematics", "Computer Science" or
"Machine Learning" join those filters automatically; anything else falls
under **Other**.

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

## Deploying to GitHub Pages

1. Push this folder to a GitHub repository.
2. Go to **Settings → Pages → Build and deployment → Deploy from branch**.
3. Select branch (e.g. `main`) and folder `/ (root)`. Save.
4. Open `https://<username>.github.io/<repository-name>/`.

No install, build, server, or environment variable is required.
To preview locally, just open `index.html` in a browser
(or run any static server, e.g. `python3 -m http.server`).

## Notes

- Papers open as full pages (no iframes): `window.location.href = "papers/x.html"` equivalent via plain links.
- Black-and-white academic theme; responsive; keyboard-accessible; print-friendly.
- To scale to hundreds of papers, keep appending to the `papers` array —
  optionally move it to a separate `papers.json`/JS file later (still static).
