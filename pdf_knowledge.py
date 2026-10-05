from pypdf import PdfReader
import os
import re

DOCUMENT_FOLDER = "documents"


def load_pdf_knowledge():

    knowledge = []

    for filename in os.listdir(DOCUMENT_FOLDER):

        if filename.lower().endswith(".pdf"):

            path = os.path.join(DOCUMENT_FOLDER, filename)

            reader = PdfReader(path)

            text = ""

            for page in reader.pages:
                text += page.extract_text() or ""

            # Split PDF into smaller chunks
            chunks = re.split(r"\n\s*\n", text)

            for chunk in chunks:

                chunk = chunk.strip()

                if len(chunk) > 30:

                    knowledge.append({
                        "filename": filename,
                        "text": chunk
                    })

    return knowledge


def search_pdf(question):

    knowledge = load_pdf_knowledge()

    question_words = set(
        re.findall(r"\b[a-zA-Z0-9]+\b", question.lower())
    )

    best_result = None
    best_score = 0

    for document in knowledge:

        document_words = set(
            re.findall(
                r"\b[a-zA-Z0-9]+\b",
                document["text"].lower()
            )
        )

        score = len(
            question_words.intersection(document_words)
        )

        if score > best_score:

            best_score = score
            best_result = document

    return best_result


if __name__ == "__main__":

    result = search_pdf(
        "What are the attendance rules?"
    )

    if result:

        print("Found in:", result["filename"])
        print()
        print(result["text"])

    else:

        print("No relevant PDF found.")