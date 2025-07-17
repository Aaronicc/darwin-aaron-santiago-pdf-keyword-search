from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import os
import PyPDF2
import re

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
KEYWORDS_FILE = "saved_keywords.txt"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
if not os.path.exists(KEYWORDS_FILE):
    with open(KEYWORDS_FILE, "w"): pass

@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    matched_keywords = set()
    total_matches = 0
    keyword_counts = {}

    if request.method == "POST":
        uploaded_file = request.files["pdf_file"]
        keywords = request.form.get("keywords", "")
        previous_keywords = request.form.getlist("previous_keywords")

        all_keywords = [kw.strip() for kw in keywords.split(",") if kw.strip()]
        all_keywords += previous_keywords
        all_keywords = list(set(all_keywords))

        filename = secure_filename(uploaded_file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        uploaded_file.save(file_path)

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
                                keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
                                highlighted_line = re.sub(
                                    rf'(?i)({re.escape(keyword)})',
                                    r'<mark>\1</mark>',
                                    line
                                )
                                results.append(
                                    f"✅ Page {page_num + 1} | 🔍 Matched: '{keyword}' | 💬 Line: {highlighted_line}"
                                )

        # Save searched keywords
        with open(KEYWORDS_FILE, "a") as f:
            for kw in all_keywords:
                f.write(f"{kw}\n")

        # Read all saved keywords
        with open(KEYWORDS_FILE, "r") as f:
            all_saved_keywords = set(kw.strip() for kw in f.readlines())

        return render_template(
            "index.html",
            results=results,
            previous_keywords=sorted(all_saved_keywords),
            summary={
                "total_matches": total_matches,
                "keyword_counts": keyword_counts
            }
        )

    # GET request
    with open(KEYWORDS_FILE, "r") as f:
        all_saved_keywords = set(kw.strip() for kw in f.readlines())
    return render_template("index.html", previous_keywords=sorted(all_saved_keywords))


if __name__ == "__main__":
    app.run(debug=True)
