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
