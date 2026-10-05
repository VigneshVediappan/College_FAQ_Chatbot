from flask import Flask, render_template, request, jsonify
import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from database import create_database, save_chat, get_chat_history
from pdf_knowledge import search_pdf


load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


app = Flask(__name__)

create_database()


with open("data/faqs.json", "r", encoding="utf-8") as file:
    faqs = json.load(file)


STOP_WORDS = {
    "what", "where", "when", "how", "can", "i",
    "is", "the", "a", "an", "are", "my", "for",
    "to", "do", "does", "and", "of", "in", "on",
    "tell", "me", "about"
}


@app.route("/")
def home():

    return render_template("index.html")


@app.route("/history", methods=["GET"])
def history():

    chats = get_chat_history()

    history_data = []

    for chat in chats:

        history_data.append({
            "user": chat[0],
            "bot": chat[1],
            "time": chat[2]
        })

    return jsonify(history_data)


@app.route("/ask", methods=["POST"])
def ask():

    data = request.get_json()

    question = data.get("question", "").lower().strip()

    if not question:

        return jsonify({
            "answer": "Please enter a question."
        })


    user_words = {
        word.strip(".,?!")
        for word in question.split()
        if word.strip(".,?!") not in STOP_WORDS
    }


    best_match = None
    highest_score = 0


    for faq in faqs:

        faq_words = {
            word.strip(".,?!")
            for word in faq["question"].lower().split()
            if word.strip(".,?!") not in STOP_WORDS
        }

        score = len(
            user_words.intersection(faq_words)
        )

        if score > highest_score:

            highest_score = score
            best_match = faq

    # Search college PDF documents

    pdf_result = search_pdf(question)

    if pdf_result:

        pdf_answer = pdf_result["text"][:1500]

        save_chat(question, pdf_answer)

        return jsonify({
            "answer": pdf_answer,
            "source": pdf_result["filename"]
        })

    # Use FAQ answer when a match exists

    if best_match and highest_score >= 1:

        answer = best_match["answer"]

        save_chat(question, answer)

        return jsonify({
            "answer": answer
        })


    # Otherwise use AI

    try:

        faq_context = "\n\n".join(
            [
                f"Question: {faq['question']}\n"
                f"Answer: {faq['answer']}"
                for faq in faqs
            ]
        )


        response = client.responses.create(

            model="gpt-5.6",

            input=(
                "You are a helpful College AI Assistant.\n\n"

                "Use the college FAQ information below "
                "when it is relevant.\n\n"

                "COLLEGE FAQ INFORMATION:\n"
                f"{faq_context}\n\n"

                "STUDENT QUESTION:\n"
                f"{question}\n\n"

                "Give a clear and concise answer. "
                "Do not invent college-specific information. "
                "If the FAQ does not contain the required "
                "information, tell the student to check "
                "the official college source."
            )
        )


        answer = response.output_text


    except Exception as error:

        print("AI Error:", error)

        answer = (
            "🤔 I couldn't find that information right now. "
            "Please check the official college website or notice."
        )


    save_chat(question, answer)


    return jsonify({
        "answer": answer
    })


if __name__ == "__main__":

    app.run(debug=True)
    