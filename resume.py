from flask import Flask, render_template, request, jsonify
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pdfplumber
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "uploads"

# --------- Skill List ----------
SKILLS = ["python", "machine learning", "data analysis", "sql",
          "deep learning", "aws", "statistics", "pandas",
          "numpy", "scikit-learn"]

def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
    return text.lower()

def calculate_score(resume, job_desc):
    docs = [resume, job_desc]
    tfidf = TfidfVectorizer().fit_transform(docs)
    score = cosine_similarity(tfidf[0:1], tfidf[1:2])
    return round(float(score[0][0]) * 100, 2)

def skill_match(resume, job):
    resume_skills = [s for s in SKILLS if s in resume]
    job_skills = [s for s in SKILLS if s in job]
    matched = list(set(resume_skills) & set(job_skills))
    missing = list(set(job_skills) - set(resume_skills))
    return matched, missing

@app.route("/", methods=["GET", "POST"])
def index():
    score = None
    matched = []
    missing = []
    if request.method == "POST":
        job_desc = request.form["job_desc"].lower()

        if "resume_file" in request.files:
            file = request.files["resume_file"]
            path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(path)
            resume_text = extract_text_from_pdf(path)
        else:
            resume_text = request.form["resume"].lower()

        score = calculate_score(resume_text, job_desc)
        matched, missing = skill_match(resume_text, job_desc)

    return render_template("resume.html", score=score, matched=matched, missing=missing)

@app.route("/chatbot", methods=["POST"])
def chatbot():
    user_msg = request.json["message"].lower()
    if "score" in user_msg:
        reply = "Paste resume and job description, then click Check Score."
    elif "improve" in user_msg:
        reply = "Add more skills, projects, and measurable achievements."
    else:
        reply = "I'm here to help analyze your resume!"
    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
