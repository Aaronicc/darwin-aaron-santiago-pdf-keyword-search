from flask import Flask, render_template, request, redirect, url_for
import os
import PyPDF2
import re
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

KEYWORDS_FILE = 'keywords.txt'

# Save keywords to a file
def save_keywords(new_keywords):
    existing_keywords = set(load_keywords())
    with open(KEYWORDS_FILE, 'a') as f:
        for keyword in new_keywords:
            if keyword not in existing_keywords:
                f.write(keyword + '\n')

# Load previously saved keywords
def load_keywords():
    if not os.path.exists(KEYWORDS_FILE):
        return []
    with open(KEYWORDS_FILE, 'r') as f:
        return [line.strip() for line in f.readlines() if line.strip()]

# Extract matched lines with context and date
def extract_matches_with_context(pdf_path, keywords):
    results = []
    date_pattern = re.compile(r"\d{2} \w{3} \d{2}")  # e.g., 01 Jul 25

    with open(pdf_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page_num, page in enumerate(reader.pages):
            text = page.extract_text()
            if not text:
                continue

            lines = text.splitlines()
            for line in lines:
                for keyword in keywords:
                    if keyword.lower() in line.lower():
                        date_match = date_pattern.search(line)
                        date_str = date_match.group() if date_match else "N/A"
                        result = f"✅ Page {page_num + 1} | 📅 Date: {date_str} | 🔍 Matched: '{keyword}' | 💬 Line: {line.strip()}"
                        results.append(result)

    return results

@app.route('/', methods=['GET', 'POST'])
def index():
    results = []
    keywords = []
    previous_keywords = load_keywords()

    if request.method == 'POST':
        uploaded_file = request.files['pdf_file']
        keywords = request.form.getlist('keywords')

        if uploaded_file and keywords:
            filename = secure_filename(uploaded_file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            uploaded_file.save(file_path)

            results = extract_matches_with_context(file_path, keywords)
            save_keywords(keywords)

    return render_template('index.html', results=results, previous_keywords=previous_keywords)

if __name__ == '__main__':
    app.run(debug=True)
