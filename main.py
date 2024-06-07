import ocrmypdf
from pypdf import PdfReader
import os
from distutils.log import debug
import camelot
from fileinput import filename
from flask import *
import string
import random
from werkzeug.utils import secure_filename


def ocr_pdf(pdf_path):
    try:
        ocrmypdf.ocr(pdf_path, f"out_{pdf_path}", redo_ocr=True)
        reader = PdfReader(f"out_{pdf_path}")
        for page in reader.pages:
            yield page.extract_text()
    except Exception as e:
        print("Error:", e)
        return None


def m(n):
    texts = ocr_pdf(n)
    if texts:
        file1 = open(f"out_{n[:-4]}.txt", "a")
        for text in texts:
            file1.write(text)
        file1.close()
        # tables = camelot.read_pdf("out.pdf", pages='1-end')
        # tables.export('out.csv', f='csv')
        os.remove(f"./out_{n}")
        tables = camelot.read_pdf(n, pages="1-end")
        tables.export(f"out_{n[:-4]}.csv", f="csv", compress=True)
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
        try:
            return send_file("out_" + res + ".zip", as_attachment=True)
        finally:
            pass
            # __import__("time").sleep(200);
            # os.remove("out_" + res + ".zip")


if __name__ == "__main__":
    app.run(debug=True)
