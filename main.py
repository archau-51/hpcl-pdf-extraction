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


# import spacy


def ocr_pdf(pdf_path):
    try:
        # ocrmypdf.ocr(pdf_path, f"out_{pdf_path}", redo_ocr=True)
        # reader = PdfReader(f"out_{pdf_path}")
        reader = PdfReader(pdf_path)
        for page in reader.pages:
            yield page.extract_text()
    except Exception as e:
        print("Error:", e)
        return None


# noinspection PyBroadException
def m(n, workdir):
    texts = ocr_pdf(n)
    if texts:
        tables = camelot.read_pdf(n, pages="1-end")
        # n and workdir are unique to this request, so there's no stale
        # out.zip/out.txt from a previous request to worry about here.
        tables.export(os.path.join(workdir, "out.csv"), f="csv", compress=True)
        with open(os.path.join(workdir, "out.txt"), "a+", encoding="utf-8") as f:
            for text in texts:
                f.write(text)
    else:
        print("Failed to read the PDF.")


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
            m(pdf_path, workdir)
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
