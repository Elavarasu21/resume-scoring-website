from flask import Flask, render_template, request, jsonify, redirect, url_for
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pdfplumber
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "uploads"

# Create uploads folder if not exists
if not os.path.exists("uploads"):
    os.makedirs("uploads")

# ---------------- SKILL DATABASE ----------------
SKILLS = [
    "python", "machine learning", "data analysis", "sql",
    "deep learning", "aws", "statistics", "pandas",
    "numpy", "scikit-learn", "data visualization"
]

# Store scores for dashboard demo (can be replaced by DB later)
score_history = []

# ---------------- PDF TEXT EXTRACTION ----------------
def extract_text_from_pdf(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            if page.extract_text():
                text += page.extract_text()
    return text.lower()

# ---------------- MATCH SCORE ----------------
def calculate_score(resume, job_desc):
    documents = [resume, job_desc]
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(documents)
    score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
    return round(float(score[0][0]) * 100, 2)

# ---------------- SKILL MATCHING ----------------
def skill_match(resume, job):
    resume_skills = [s for s in SKILLS if s in resume]
    job_skills = [s for s in SKILLS if s in job]
    matched = list(set(resume_skills) & set(job_skills))
    missing = list(set(job_skills) - set(resume_skills))
    return matched, missing

# ---------------- MAIN PAGE ----------------
@app.route("/", methods=["GET", "POST"])
def index():
    score = None
    matched = []
    missing = []

    if request.method == "POST":
        job_desc = request.form["job_desc"].lower()

        # If PDF uploaded
        if "resume_file" in request.files and request.files["resume_file"].filename != "":
            file = request.files["resume_file"]
            path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(path)
            resume_text = extract_text_from_pdf(path)
        else:
            resume_text = request.form.get("resume", "").lower()

        score = calculate_score(resume_text, job_desc)
        matched, missing = skill_match(resume_text, job_desc)

        # Store score for dashboard analytics
        score_history.append(score)

    return render_template("resume.html", score=score, matched=matched, missing=missing)

# ---------------- CHATBOT API ----------------
@app.route("/chatbot", methods=["POST"])
def chatbot():
    user_msg = request.json["message"].lower()

    if "score" in user_msg:
        reply = "Upload your resume and job description, then click Analyze Resume to get your match score."
    elif "improve" in user_msg:
        reply = "Add more skills, project experience, and measurable achievements to improve your resume."
    elif "skills" in user_msg:
        reply = "Make sure your resume contains relevant technical and soft skills required for the job."
    else:
        reply = "I'm your AI Resume Assistant! Ask me how to improve your resume."

    return jsonify({"reply": reply})

# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    total_resumes = len(score_history)
    avg_score = round(sum(score_history)/total_resumes, 2) if total_resumes > 0 else 0

    labels = [f"Resume {i+1}" for i in range(len(score_history))]
    scores = score_history

    return render_template("dashboard.html",
                           total_resumes=total_resumes,
                           avg_score=avg_score,
                           labels=labels,
                           scores=scores)

# ---------------- RUN APP ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
