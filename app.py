import json
from flask import Flask, jsonify

app = Flask(__name__)

from flask import render_template

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/questions")
def get_questions():
    with open("questions.json", "r", encoding="utf-8") as f:
        questions = json.load(f)
    return jsonify(questions)
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)