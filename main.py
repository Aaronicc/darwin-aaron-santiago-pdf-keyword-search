import os
import fitz  # PyMuPDF
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Store previously searched keywords
keyword_history = set()

def extract_keyword_matches(pdf_path, keywords):
    results = []
    keyword_counts = {kw.lower(): 0 for kw in keywords}

    with fitz.open(pdf_path) as doc:
        for page_num, page in enumerate(doc):
            lines = page.get_text("text").split('\n')
            for line in lines:
                for keyword in keywords:
                    if keyword.lower() in line.lower():
                        keyword_counts[keyword.lower()] += 1

                        # Highlight all variants of the keyword
                        highlighted_line = line
                        highlighted_line = highlighted_line.replace(keyword, f"<mark>{keyword}</mark>")
                        highlighted_line = highlighted_line.replace(keyword.upper(), f"<mark>{keyword.upper()}</mark>")
                        highlighted_line = highlighted_line.replace(keyword.lower(), f"<mark>{keyword.lower()}</mark>")

                        results.append(
                            f"✅ Page {page_num + 1} | 🔍 Matched: '{keyword}' | 💬 Line: {highlighted_line.strip()}"
                        )
                        break  # Prevent duplicate match for multiple keywords in the same line

    return results, keyword_counts

@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    counts = {}
    keywords = []

    if request.method == "POST":
        uploaded_file = request.files["pdf_file"]
        keywords_text = request.form.get("keywords", "")
        keywords = [kw.strip() for kw in keywords_text.split(",") if kw.strip()]
        keyword_history.update(keywords)

        if uploaded_file and uploaded_file.filename.endswith(".pdf"):
            filename = secure_filename(uploaded_file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            uploaded_file.save(filepath)

            try:
                results, counts = extract_keyword_matches(filepath, keywords)
            except Exception as e:
                results = [f"❌ Error reading PDF: {str(e)}"]

    return render_template(
        "index.html",
        results=results,
        keywords=keywords,
        keyword_history=sorted(keyword_history),
        counts=counts
    )

if __name__ == "__main__":
    app.run(debug=True)
