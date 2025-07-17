# main.py
import os
import re
from flask import Flask, request, render_template, redirect, url_for
import PyPDF2
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Store searched keywords for re-click
keyword_history = set()

def extract_lines_with_keywords(pdf_path, keywords):
    results = []
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
                        match = re.search(keyword, line, re.IGNORECASE)
                        matched_text = match.group() if match else keyword
                        date_match = re.search(r"\d{2} [A-Za-z]{3} \d{2}", line)
                        date_str = date_match.group() if date_match else "No date found"
                        results.append(
                            f"✅ Page {page_num + 1} | 📅 Date: {date_str} | 🔍 Matched: '{matched_text}' | 💬 Line: {line.strip()}"
                        )
                        break
    return results

@app.route('/', methods=['GET', 'POST'])
def index():
    results = []
    keywords = []
    if request.method == 'POST':
        file = request.files.get('pdf_file')
        raw_keywords = request.form.get('keywords', '')
        keywords = [k.strip() for k in raw_keywords.split(',') if k.strip()]

        # Save searched keywords
        keyword_history.update(keywords)

        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            results = extract_lines_with_keywords(filepath, keywords)
    return render_template('index.html', results=results, keywords=keywords, history=sorted(keyword_history))

if __name__ == '__main__':
    app.run(debug=True)
