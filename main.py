import gc
import io
import os
import random
import shutil
import string
import tempfile
import camelot
from flask import *
from pypdf import PdfReader
from werkzeug.utils import secure_filename
from simple_sc import extract_info
from advanced_sc import adv_extract
import pandas as pd
import zipfile


def _get_secret_key():
    # Needed for flash() to work. Override with a real secret via the
    # FLASK_SECRET_KEY environment variable for anything long-lived; falls
    # back to a random per-process value, which is fine for flashing a
    # message across a single redirect within the same running app.
    return os.environ.get("FLASK_SECRET_KEY", os.urandom(24))


try:
    import pytesseract
    from pdf2image import convert_from_path

    _OCR_LIBS_AVAILABLE = True
except ImportError:
    pytesseract = None
    convert_from_path = None
    _OCR_LIBS_AVAILABLE = False

# The OCR fallback additionally needs two system binaries that pip can't
# install for us: the Tesseract OCR engine, and poppler (for pdf2image's
# page-to-image rendering). Check for both up front so we can degrade
# gracefully (skip OCR, log why) instead of crashing mid-request.
_TESSERACT_AVAILABLE = _OCR_LIBS_AVAILABLE and shutil.which("tesseract") is not None
_POPPLER_AVAILABLE = _OCR_LIBS_AVAILABLE and (
    shutil.which("pdftoppm") is not None or shutil.which("pdftocairo") is not None
)
OCR_AVAILABLE = _OCR_LIBS_AVAILABLE and _TESSERACT_AVAILABLE and _POPPLER_AVAILABLE

if _OCR_LIBS_AVAILABLE and not OCR_AVAILABLE:
    _missing = []
    if not _TESSERACT_AVAILABLE:
        _missing.append("the 'tesseract' binary")
    if not _POPPLER_AVAILABLE:
        _missing.append("poppler ('pdftoppm'/'pdftocairo')")
    print(
        "OCR fallback disabled: missing "
        + " and ".join(_missing)
        + ". Scanned pages with no extractable text will be left blank."
    )
elif not _OCR_LIBS_AVAILABLE:
    print(
        "OCR fallback disabled: 'pytesseract'/'pdf2image' are not installed. "
        "Scanned pages with no extractable text will be left blank."
    )


def _ocr_page(pdf_path, page_number):
    """Run OCR on a single (1-indexed) page of pdf_path.

    Returns the OCR'd text, or "" if OCR isn't available/fails, so callers
    can degrade gracefully instead of crashing.
    """
    if not OCR_AVAILABLE:
        return ""
    try:
        images = convert_from_path(pdf_path, first_page=page_number, last_page=page_number)
        if not images:
            return ""
        return pytesseract.image_to_string(images[0])
    except Exception as e:
        print(f"OCR failed for page {page_number} of {pdf_path}: {e}")
        return ""


def ocr_pdf(pdf_path):
    """Extract the text of every page in pdf_path.

    Falls back to OCR for any page where normal text extraction returns
    nothing (e.g. a scanned page with no embedded text layer), as long as
    the OCR system dependencies are available (see OCR_AVAILABLE above).

    Returns a list of per-page text, or None if the PDF itself couldn't be
    opened at all.
    """
    try:
        reader = PdfReader(pdf_path)
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
        return None

    texts = []
    for i, page in enumerate(reader.pages, start=1):
        try:
            text = page.extract_text() or ""
        except Exception as e:
            print(f"Error extracting text from page {i} of {pdf_path}: {e}")
            text = ""
        if not text.strip():
            text = _ocr_page(pdf_path, i)
        texts.append(text)
    return texts


# noinspection PyBroadException
def m(n, workdir):
    """Extract tables and text from PDF n into workdir. Returns True on
    success, False if the PDF couldn't be read at all."""
    texts = ocr_pdf(n)
    if texts is None:
        print("Failed to read the PDF.")
        return False
    tables = camelot.read_pdf(n, pages="1-end")
    # n and workdir are unique to this request, so there's no stale
    # out.zip/out.txt from a previous request to worry about here.
    tables.export(os.path.join(workdir, "out.csv"), f="csv", compress=True)
    with open(os.path.join(workdir, "out.txt"), "a+", encoding="utf-8") as f:
        for text in texts:
            f.write(text)
    return True


app = Flask(__name__)
app.secret_key = _get_secret_key()
ALLOWED_EXTENSIONS = {"pdf"}


@app.route("/")
def main():
    return render_template("index.html")


@app.route("/success", methods=["POST"])
def success():
    if request.method == "POST":
        f = request.files.get("file")
        if f is None or f.filename == "":
            flash("Please choose a PDF file to upload.")
            return redirect(url_for("main"))

        k = request.form.getlist('keywords')
        a = request.form.getlist('keywords_a')
        w = request.form.getlist('keywords_l')

        # Previously, forgetting to tick "Keywords" (or leaving the
        # keyword box empty) silently skipped keyword extraction with no
        # feedback, so the user would just get back a zip with no
        # keyword results and no explanation why. Validate up front and
        # send them back to the form with a clear message instead.
        if len(k) != 1:
            flash('Please check the "Keywords" box and enter at least one keyword to search for.')
            return redirect(url_for("main"))

        kwrs = [kw.strip() for kw in w[0].split(",")] if w else []
        kwrs = [kw for kw in kwrs if kw]
        if not kwrs:
            flash("Please enter at least one keyword in the keywords box.")
            return redirect(url_for("main"))

        cs = {}
        cs["Keyword"] = []
        # Every request gets its own directory, so concurrent uploads can
        # no longer stomp on each other's out.csv/out.txt/out.zip, and
        # everything is cleaned up in `finally` once we're done with it.
        workdir = tempfile.mkdtemp(prefix="hpcl_")
        try:
            res = "".join(random.choices(string.ascii_uppercase + string.digits, k=5))
            pdf_path = os.path.join(workdir, secure_filename(res + ".pdf"))
            f.save(pdf_path)
            if not m(pdf_path, workdir):
                flash("Could not read that PDF. Please make sure it isn't corrupted or password protected.")
                return redirect(url_for("main"))
            zip_path = os.path.join(workdir, "out.zip")
            with open(os.path.join(workdir, 'out.txt'), 'r', encoding='utf-8') as f1:
                t = f1.read()
            rest = []
            for i in kwrs:
                rest.append(extract_info(t, i))
            restn = []
            for i in rest:
                restn.append(i)
            rest1 = [x for xs in rest for x in xs]
            cs["Simple Search"] = [x for xs in restn for x in xs]
            count1 = 0
            count2 = 0
            cc = []
            for i in kwrs:
                for j in restn[count1]:
                    if count2 == 0:
                        cc.append(i)
                        count2+=1
                    else:
                        cc.append(" ")
                count1 += 1
                count2 = 0
            cs["Keyword"] = cc
            if len(a) == 1:
                rest2 = []
                count3 = 0
                for i in kwrs:
                    rest2.append(adv_extract(t, i))
                    for x in range(len(restn[count3])-1):
                        rest2.append(" ")
                    count3+=1
                cs["Advanced Search"] = rest2
            print(cs)
            df = pd.DataFrame(cs)
            csv_path = os.path.join(workdir, "out.csv")
            df.to_csv(csv_path, index=False, encoding="utf-8")
            with zipfile.ZipFile(zip_path, "a", compression=zipfile.ZIP_DEFLATED) as zipf:
                destination = 'keywords.csv'
                zipf.write(csv_path, destination)
            # return render_template("acknowledgement.html", name = f.filename)
            # Read the zip into memory before removing workdir: send_file
            # uses direct_passthrough for on-disk paths, which would leave
            # us with no reliable hook to clean the directory up afterwards.
            with open(zip_path, "rb") as zf:
                zip_bytes = zf.read()
        finally:
            # camelot (via pdfminer) keeps its own file handle on the PDF
            # open until it's garbage collected, which can block removing
            # the directory it lives in on Windows - force a collection
            # first so cleanup actually succeeds.
            gc.collect()
            shutil.rmtree(workdir, ignore_errors=True)
        return send_file(io.BytesIO(zip_bytes), as_attachment=True, download_name="out.zip")


if __name__ == "__main__":
    app.run(debug=False)
