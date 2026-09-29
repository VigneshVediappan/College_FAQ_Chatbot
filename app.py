from flask import Flask, render_template, request, jsonify
import json

app = Flask(__name__)


# Load FAQ data
with open("data/faqs.json", "r", encoding="utf-8") as file:
    faqs = json.load(file)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask():

    data = request.get_json()
    question = data.get("question", "").lower()

    for faq in faqs:

        faq_question = faq["question"].lower()

        if any(word in faq_question for word in question.split()):
            return jsonify({
                "answer": faq["answer"]
            })

    return jsonify({
        "answer": "Sorry, I couldn't find an answer to that question."
    })


if __name__ == "__main__":
    app.run(debug=True)