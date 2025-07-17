from flask import Flask, render_template, request
import os
import PyPDF2
import re
import json

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
SAVED_KEYWORDS_FILE = 'saved_keywords.json'

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load previously saved keywords
def load_saved_keywords():
    if os.path.exists(SAVED_KEYWORDS_FILE):
        with open(SAVED_KEYWORDS_FILE, 'r') as f:
            return json.load(f)
    return []

# Save keyword if new
def save_keyword(keyword):
    keywords = load_saved_keywords()
    if keyword not in keywords:
        keywords.append(keyword)
        with open(SAVED_KEYWORDS_FILE, 'w') as f:
            json.dump(keywords, f)

# Extract whole lines where keywords are found, with dates if available
def search_pdf_for_keywords(pdf_path, keywords):
    results = []
    date_pattern = r'\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2})\b'

    with open(pdf_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page_num, page in enumerate(reader.pages):
            text = page.extract_text()
            if not text:
                continue
            lines = text.split('\n')
            for line in lines:
                for keyword in keywords:
                    if keyword.lower() in line.lower():
                        found_dates = re.findall(date_pattern, line)
                        date_info = f" | Date(s): {', '.join(found_dates)}" if found_dates else ""
                        results.append(f"Page {page_num + 1}: {line.strip()}{date_info}")
                        save_keyword(keyword)
    return results

@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    saved_keywords = load_saved_keywords()
    if request.method == "POST":
        uploaded_file = request.files["pdf"]
        keywords_input = request.form.get("keywords", "")
        keywords = [k.strip() for k in keywords_input.split(",") if k.strip()]

        if uploaded_file and keywords:
            filename = uploaded_file.filename
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            uploaded_file.save(file_path)
            results = search_pdf_for_keywords(file_path, keywords)

    return render_template("index.html", results=results, saved_keywords=load_saved_keywords())

if __name__ == "__main__":
    app.run(debug=True)
