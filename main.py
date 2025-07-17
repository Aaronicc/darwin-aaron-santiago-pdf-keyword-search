from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import os
import PyPDF2
import re

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
KEYWORDS_FILE = "keywords.txt"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    matched_keywords = set()
    total_matches = 0

    if request.method == "POST":
        uploaded_file = request.files["pdf_file"]
        keywords = request.form.get("keywords", "")
        previous_keywords = request.form.getlist("previous_keywords")

        # Combine new and previously selected keywords
        all_keywords = [kw.strip() for kw in (keywords.split(",") if keywords else [])]
        all_keywords += previous_keywords
        all_keywords = list(set(filter(None, all_keywords)))

        # Save the uploaded PDF
        filename = secure_filename(uploaded_file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        uploaded_file.save(file_path)

        # Search the PDF
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page_num, page in enumerate(reader.pages):
                text = page.extract_text()
                if text:
                    lines = text.split("\n")
                    for line in lines:
                        for keyword in all_keywords:
                            if re.search(rf'\b{re.escape(keyword)}\b', line, re.IGNORECASE):
                                matched_keywords.add(keyword)
                                total_matches += 1
                                highlighted = re.sub(
                                    rf'(?i)({re.escape(keyword)})',
                                    r'<mark>\1</mark>',
                                    line
                                )
                                results.append(
                                    f"✅ Page {page_num + 1} | 🔍 Matched: '{keyword}' | 💬 Line: {highlighted}"
                                )

        # Save keywords
        with open(KEYWORDS_FILE, "a") as f:
            for kw in all_keywords:
                f.write(f"{kw}\n")

        # Remove duplicates
        with open(KEYWORDS_FILE, "r") as f:
            all_saved_keywords = set(kw.strip() for kw in f.readlines())

        return render_template(
            "index.html",
            results=results,
            previous_keywords=sorted(all_saved_keywords),
            summary={
                "total_matches": total_matches,
                "unique_keywords": sorted(matched_keywords)
            }
        )

    # GET request
    previous_keywords = []
    if os.path.exists(KEYWORDS_FILE):
        with open(KEYWORDS_FILE, "r") as f:
            previous_keywords = sorted(set(f.read().splitlines()))

    return render_template("index.html", results=None, previous_keywords=previous_keywords)

if __name__ == "__main__":
    app.run(debug=True)
