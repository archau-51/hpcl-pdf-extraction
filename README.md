# PDF Table and keyword extraction project

## Installation

1. Clone the repository and cd

   ```shell
   git clone https://github.com/archau-51/hpcl-pdf-extraction.git && cd hpcl-pdf-extraction
   ```

2. Install ghostscript from https://ghostscript.com/ and make sure it is on PATH

3. Install python dependencies

   ```shell
   pip install -r requirements.txt
   ```

4. (Optional, for scanned/image-only PDFs) Install the OCR system dependencies:
   * [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) - the OCR engine used by `pytesseract`.
   * [Poppler](https://poppler.freedesktop.org/) - provides `pdftoppm`/`pdftocairo`, used by `pdf2image` to rasterize pages for OCR. On Windows, grab a build from [oschwartz10612/poppler-windows](https://github.com/oschwartz10612/poppler-windows); on Debian/Ubuntu, `apt install poppler-utils`; on macOS, `brew install poppler`.

   Both need to be on `PATH`. If they aren't found, the app still runs - it just skips OCR for scanned pages with no extractable text and logs a message saying so.

## Usage

1. Run main.py

   ```shell
   python3 main.py
   ```

2. Go to http://127.0.0.1:5000 to access the webUI

## How it works

1. Upload a PDF and, optionally, tick "Keywords" and enter comma-separated keywords (and "Advanced Search" for a HuggingFace QA-based search).
2. Each request gets its own temp directory, so concurrent uploads don't collide, and everything is cleaned up after the response is built.
3. Text is extracted page by page with `pypdf`. Pages with no extractable text (usually scanned pages) fall back to OCR (`pdf2image` + `pytesseract`) if the OCR dependencies are installed; otherwise that page is left blank and a message is logged.
4. `camelot` extracts any tables into a CSV per table.
5. For each keyword, `simple_sc.py` splits the text into sentences (NLTK) and returns every sentence containing it. If "Advanced Search" is ticked, `advanced_sc.py` also asks a HuggingFace `transformers` QA pipeline "What is the `<keyword>`?" against the full text. The pipeline is loaded once per process and reused, not reloaded per keyword.
6. Everything is bundled into one zip (table CSVs + `keywords.csv`) and returned as a download.

Submitting the form without keywords redirects back to the upload page with a message instead of failing silently.

Set the `FLASK_SECRET_KEY` env var to a fixed value for anything long-lived, otherwise a random key is generated each time the app starts (fine for local use, but flashed messages won't survive a restart).

## Testing

Unit tests cover `simple_sc.extract_info` and `advanced_sc.adv_extract` (with the HuggingFace pipeline mocked out, so no model download/network needed; skipped automatically if `transformers` isn't installed).

```shell
pip install -r requirements-dev.txt
pytest
```
