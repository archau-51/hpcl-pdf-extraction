# PDF Table and keyword extraction project

## Installation

1. Clone the repository and cd
   
   ```shell
   git clone https://github.com/archau-51/hpcl-pdf-extraction.git && cd hpcl-pdf-extraction
   ```

2.  Install ghostscript from https://ghostscript.com/ and make sure it is on PATH

3. Install python dependencies
   
   ```shell
   pip install -r requirements.txt
   ```

4. (Optional, for scanned/image-only PDFs) Install the OCR system dependencies:
   * [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) - the OCR engine used by `pytesseract`.
   * [Poppler](https://poppler.freedesktop.org/) - provides `pdftoppm`/`pdftocairo`, used by `pdf2image` to rasterize PDF pages for OCR. On Windows, grab a build from [oschwartz10612/poppler-windows](https://github.com/oschwartz10612/poppler-windows) and add its `bin` folder to PATH; on Debian/Ubuntu, `apt install poppler-utils`; on macOS, `brew install poppler`.

   Both binaries need to be on `PATH`. If they aren't found, the app still runs - it just skips OCR for scanned pages that have no extractable text, and logs a message saying so.

## Usage

1. Run main.py
   
   ```shell
   python3 main.py
   ```

2. Go to http://127.0.0.1:5000 to access the webUI

## How it works

1. You upload a PDF and, optionally, tick "Keywords" and enter one or more comma-separated keywords (and optionally tick "Advanced Search" too).
2. Each request gets its own temporary working directory, so concurrent uploads never collide or overwrite each other's output, and everything in it is cleaned up once the response has been built - even if something goes wrong partway through.
3. The uploaded PDF's text is extracted page by page with `pypdf`. If a page has no extractable text (typically a scanned page with no embedded text layer), the app falls back to OCR for that page - rendering it to an image with `pdf2image`/Poppler and reading it with `pytesseract`. If the OCR system dependencies aren't installed, that page is just left blank instead of crashing, and a message is logged.
4. `camelot` extracts any tables in the PDF into a CSV-per-table, zipped up.
5. For each keyword, `simple_sc.py` splits the extracted text into sentences (via NLTK's sentence tokenizer) and returns every sentence containing that keyword.
6. If "Advanced Search" was ticked, `advanced_sc.py` additionally asks a HuggingFace `transformers` question-answering pipeline "What is the `<keyword>`?" against the full extracted text. The pipeline (which is slow to load) is built once per process and reused for every keyword/request afterwards instead of being reloaded each time.
7. All of the above is bundled into a single zip (table CSVs + `keywords.csv`) and returned as a download.

If you submit the form without checking "Keywords" or without typing any actual keywords, you'll be redirected back to the upload page with a message explaining what to fix, instead of the request silently failing.

### Environment variables

* `FLASK_SECRET_KEY` - secret key used to sign the flash-message session cookie. If unset, a random key is generated once when the app starts (fine for local/dev use, but set this explicitly for anything long-lived/production-like so flashed messages survive an app restart).

## Testing

Unit tests cover `simple_sc.extract_info` directly, and `advanced_sc.adv_extract` with the HuggingFace pipeline mocked out (so the tests don't need to download a model or have network access; they're skipped automatically if `transformers` isn't installed).

```shell
pip install -r requirements-dev.txt
pytest
```
