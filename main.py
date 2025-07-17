from flask import Flask, request, render_template, redirect, url_for
import os
import PyPDF2
import re
import json

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
KEYWORDS_FILE = "keywords.json"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def load_keywords():
    if os.path.exists(KEYWORDS_FILE):
        with open(KEYWORDS_FILE, "r") as f:
            return json.load(f)
    return []

def save_keywords(new_keywords):
    keywords = load_keywords()
    for kw in new_keywords:
        if kw not in keywords:
            keywords.append(kw)
    with open(KEYWORDS_FILE, "w") as f:
        json.dump(keywords, f)

def extract_lines_with_keywords_and_dates(pdf_path, keywords):
    results = []
    date_pattern = r'\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2})\b'

    with open(pdf_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page_num, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                lines = text.split("\n")
                for line in lines:
                    for keyword in keywords:
                        if keyword.lower() in line.lower():
                            found_dates = re.findall(date_pattern, line)
                            date_info = f" | Date(s): {', '.join(found_dates)}" if found_dates else ""
                            results.append(f"Page {page_num + 1}: {line.strip()}{date_info}")
                            break
    return results

@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    keywords = load_keywords()
    selected_keywords = []

    if request.method == "POST":
        uploaded_file = request.files["pdf_file"]
        input_keywords = request.form.get("keywords", "")
        selected_keywords = request.form.getlist("selected_keywords")

        all_keywords = [kw.strip() for kw in input_keywords.split(",") if kw.strip()] + selected_keywords

        if uploaded_file and all_keywords:
            filename = uploaded_file.filename
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            uploaded_file.save(file_path)

            results = extract_lines_with_keywords_and_dates(file_path, all_keywords)
            save_keywords(all_keywords)

    return render_template("index.html", results=results, keywords=load_keywords())

if __name__ == "__main__":
    app.run(debug=True)
