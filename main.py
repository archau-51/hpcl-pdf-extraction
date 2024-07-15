import os
import random
import string
import camelot
from flask import *
from pypdf import PdfReader
from werkzeug.utils import secure_filename
from simple_sc import extract_info
from advanced_sc import adv_extract
import pandas as pd
import zipfile


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
        tables.export("out.csv", f="csv", compress=True)
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
        k = request.form.getlist('keywords')
        a = request.form.getlist('keywords_a')
        w = request.form.getlist('keywords_l')
        cs = {}
        cs["Keyword"] = []
        res = "".join(random.choices(string.ascii_uppercase + string.digits, k=5))
        f.save(secure_filename(res + ".pdf"))
        m(res + ".pdf")
        if len(k) == 1:
            with open('out.txt', 'r', encoding='utf-8') as f1:
                t = f1.read()
            kwrs = w[0].split(",")
            rest = []
            for i in kwrs:
                rest.append(x for x in extract_info(t, i))
            restn = []
            for i in rest:
                restn.append(list(i))
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
                        cc.append("")
                count1 += 1
                count2 = 0
            cs["Keyword"] = cc
            if len(a) == 1:
                rest2 = []
                count3 = 0
                for i in kwrs:
                    rest2.append(adv_extract(t, i))
                    for x in range(len(restn[count3])-1):
                        rest2.append("")
                    count3+=1
                cs["Advanced Search"] = rest2
            print(cs)
            df = pd.DataFrame(cs)
            df.to_csv("out.csv", index=False, encoding="utf-8")
            filepath = "out.zip"
            with zipfile.ZipFile(filepath, "a", compression=zipfile.ZIP_DEFLATED) as zipf:
                source_path = 'out.csv'
                destination = 'keywords.csv'
                zipf.write(source_path, destination)
                os.remove("out.csv")
        # return render_template("acknowledgement.html", name = f.filename)
        return send_file("out.zip", as_attachment=True)


if __name__ == "__main__":
    app.run(debug=False)
