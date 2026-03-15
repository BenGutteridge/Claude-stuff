# Fifty Challenging Problems in Probability

Interactive web flashcard app for Mosteller's *Fifty Challenging Problems in Probability*.
Live site: **https://BenGutteridge.github.io/Claude-stuff/**

---

## How to use the site

- **Random Question** — pick a random problem
- **Prev / Next** — step through problems in order
- **Reveal Answer** — show the solution; click again (**Hide Answer**) to conceal it
- **Page links** — open the original scanned page from the book (Q = question, S = solution)
- **Jump to question** — numbered links at the bottom jump directly to any problem
- Keyboard shortcuts: `←`/`p` prev, `→`/`n` next, `r` random, `Space`/`Enter` toggle answer

---

## Replicating this for another PDF book

These are the exact steps taken to turn the Mosteller PDF into this site. An AI agent can follow them verbatim for any problem/solution book.

### Prerequisites

```bash
pip install pdf2image pytesseract Pillow
# Also requires: poppler (for pdf2image) and tesseract-ocr
# Ubuntu/Debian: sudo apt install poppler-utils tesseract-ocr
# macOS:         brew install poppler tesseract
```

---

### Step 1 — Convert PDF pages to images

Script: [`pdf_to_images.py`](pdf_to_images.py)

```python
from pdf2image import convert_from_path
import os

pdf_path = "YourBook.pdf"          # <-- change this
output_dir = "pdf_pages_images"
os.makedirs(output_dir, exist_ok=True)

pages = convert_from_path(pdf_path, dpi=200)
for i, page in enumerate(pages, start=1):
    page.save(os.path.join(output_dir, f"page_{i:03d}.png"), "PNG")
```

Run with:
```bash
python pdf_to_images.py
```

Output: `pdf_pages_images/page_001.png` … `page_NNN.png`
The images are committed to the repo and served directly by GitHub Pages.

---

### Step 2 — OCR every page to text

Script: [`ocr_pages.py`](ocr_pages.py)

```python
import pytesseract
from PIL import Image
import os, glob

images_dir = "pdf_pages_images"
output_dir = "pdf_pages_text"
os.makedirs(output_dir, exist_ok=True)

for img_path in sorted(glob.glob(os.path.join(images_dir, "page_*.png"))):
    basename = os.path.splitext(os.path.basename(img_path))[0]
    text = pytesseract.image_to_string(Image.open(img_path))
    with open(os.path.join(output_dir, f"{basename}.txt"), "w", encoding="utf-8") as f:
        f.write(text)
```

Run with:
```bash
python ocr_pages.py
```

Output: `pdf_pages_text/page_001.txt` … one `.txt` per page.
OCR quality varies; mathematical notation often comes out garbled. That's fine — the text is used only to help Claude locate problem boundaries. The rendered PNG images are the authoritative source.

---

### Step 3 — Build `problems.json` using Claude

This is the most important step. The OCR text is fed to Claude (claude-sonnet or claude-opus recommended) alongside the page images to produce a structured JSON array.

**The prompt given to Claude:**

> "You are processing a scanned maths/puzzle book. I will give you the OCR text of each page and the rendered page images. Your job is to output a JSON array where each element represents one numbered problem in the book. For each problem output:
>
> - `number` (int) — the problem number
> - `title` (string) — a short descriptive title (invent one if the book doesn't give one)
> - `question_pages` (int[]) — list of 1-based page numbers containing the question
> - `solution_pages` (int[]) — list of 1-based page numbers containing the solution/answer
> - `question` (string) — the full verbatim question text, faithfully transcribed (fix OCR errors using the image)
> - `answer` (string) — the full solution, faithfully transcribed and lightly formatted for readability (use Unicode math symbols like ×, ÷, √, ², ∞, ½ instead of ASCII approximations)
>
> Produce only valid JSON, no markdown fences, no commentary."

**Practical approach used here:**

1. The OCR text files (`pdf_pages_text/`) were pasted into the Claude context in one batch to give Claude an overview of the book structure.
2. The page images for the questions section and the solutions section were shared separately.
3. Claude was asked to identify which page ranges contained problems vs solutions, then produce the full JSON in one pass.
4. The output was saved directly as `problems.json`.

For a longer book, split into batches of ~20 problems at a time and concatenate the JSON arrays.

**JSON schema** (`problems.json`):

```json
[
  {
    "number": 1,
    "title": "The Sock Drawer",
    "question_pages": [9],
    "solution_pages": [23, 24],
    "question": "Full verbatim question text...",
    "answer": "Full solution with workings..."
  }
]
```

Optional extra field (used in this repo for some problems):
- `"solution_type": "discussion"` — marks problems whose answer is a qualitative discussion rather than a numeric result; the UI shows a small badge.

---

### Step 4 — Wire up the web app

The site is a single self-contained file: [`index.html`](index.html).

To adapt it for a new book:

1. **Embed the new `problems.json`** — in `index.html`, find the line:
   ```js
   const problems = [...];
   ```
   Replace the array contents with your new JSON (or load it via `fetch('problems.json')` if you prefer a separate file).

2. **Update the title/subtitle** — change the `<h1>` and `.subtitle` `<p>` near the top of `<body>`.

3. **Page image path convention** — images must be at `pdf_pages_images/page_NNN.png` (zero-padded to 3 digits). The `padPage()` function in the JS handles this. If your images use a different naming scheme, update `padPage()` accordingly.

4. No build step, no dependencies, no server required. The whole app runs from static files.

---

### Step 5 — Publish to GitHub Pages

1. Push all files (including `pdf_pages_images/`, `problems.json`, `index.html`, `.nojekyll`) to `main`.
2. In the repo: **Settings → Pages → Source: Deploy from branch → `main` / `(root)` → Save**.
3. Site goes live at `https://<username>.github.io/<repo-name>/`.

The `.nojekyll` file at the repo root tells GitHub Pages not to run Jekyll processing (required so that filenames starting with `_` or directories work correctly and to avoid unnecessary build steps).

---

### File inventory

| File | Purpose |
|---|---|
| `pdf_to_images.py` | Converts the source PDF to per-page PNG images |
| `ocr_pages.py` | Runs Tesseract OCR on each image, outputs `.txt` files |
| `pdf_pages_images/` | PNG images of every page (served by GitHub Pages) |
| `pdf_pages_text/` | Tesseract OCR output (used as Claude input; not served) |
| `problems.json` | Structured Q&A data produced by Claude |
| `index.html` | The entire web app (HTML + CSS + JS, no dependencies) |
| `.nojekyll` | Disables Jekyll on GitHub Pages |
| `Mostellar — 50 Challenging Problems in Probability.pdf` | Source PDF |
