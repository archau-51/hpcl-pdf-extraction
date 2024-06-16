import os
import random
import string

import camelot
import ocrmypdf
from flask import *
from pypdf import PdfReader
from werkzeug.utils import secure_filename
from pypdf import PdfReader


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
def m(n):
    texts = ocr_pdf(n)
    if texts:
        tables = camelot.read_pdf(n, pages="1-end")
        try:
            os.remove("out.zip")
            os.remove("out.txt")
        except:
            pass
        tables.export(f"out.csv", f="csv", compress=True)
        with open("out.txt", "a+", encoding="utf-8") as f:
            for text in texts:
                f.write(text)
        os.remove(n)
    else:
        print("Failed to read the PDF.")


app = Flask(__name__)
ALLOWED_EXTENSIONS = {"pdf"}


@app.route("/")
def main():
    return render_template("index.html")


@app.route("/success", methods=["POST"])
def success():
    if request.method == "POST":
        f = request.files["file"]
        res = "".join(random.choices(string.ascii_uppercase + string.digits, k=5))
        f.save(secure_filename(res + ".pdf"))
        m(res + ".pdf")
        # return render_template("acknowledgement.html", name = f.filename)
        return send_file("out.zip", as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
