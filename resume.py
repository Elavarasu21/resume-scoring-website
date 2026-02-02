import pdfplumber
import os
from flask import Flask, render_template, request
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

def calculate_score(resume, job_desc):
    documents = [resume, job_desc]
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(documents)
    score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
    return round(float(score[0][0]) * 100, 2)

@app.route("/", methods=["GET", "POST"])
def index():
    score = None
    if request.method == "POST":
        resume = request.form["resume"]
        job_desc = request.form["job_desc"]
        score = calculate_score(resume, job_desc)
    return render_template("resume.html", score=score)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
