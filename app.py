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

if __name__ == "__main__":
    app.run(debug=True)