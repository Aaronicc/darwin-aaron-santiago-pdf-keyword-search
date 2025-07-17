
import os
from flask import Flask, render_template, request
import PyPDF2

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
KEYWORDS_FILE = "keywords.txt"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def search_pdf(pdf_path, keywords):
    results = []
    with open(pdf_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page_num, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                lines = text.split("\n")
                for line in lines:
                    for keyword in keywords:
                        if keyword.lower() in line.lower():
                            results.append(f"Page {page_num + 1}: {line.strip()}")
    return results

def save_keyword(keyword):
    if not os.path.exists(KEYWORDS_FILE):
        open(KEYWORDS_FILE, "w").close()
    with open(KEYWORDS_FILE, "r") as f:
        existing = f.read().splitlines()
    if keyword not in existing:
        with open(KEYWORDS_FILE, "a") as f:
            f.write(keyword + "\n")

def load_keywords():
    if not os.path.exists(KEYWORDS_FILE):
        return []
    with open(KEYWORDS_FILE, "r") as f:
        return f.read().splitlines()

@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    uploaded_filename = ""
    previous_keywords = load_keywords()
    if request.method == "POST":
        uploaded_file = request.files["pdf"]
        keywords_input = request.form["keywords"]
        keywords = [kw.strip() for kw in keywords_input.split(",") if kw.strip()]
        for kw in keywords:
            save_keyword(kw)
        if uploaded_file:
            uploaded_filename = uploaded_file.filename
            file_path = os.path.join(UPLOAD_FOLDER, uploaded_filename)
            uploaded_file.save(file_path)
            results = search_pdf(file_path, keywords)
    return render_template("index.html", results=results, filename=uploaded_filename, keywords=previous_keywords)
