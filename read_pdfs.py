from pypdf import PdfReader
import os

folder = "documents"

for filename in os.listdir(folder):

    if filename.lower().endswith(".pdf"):

        path = os.path.join(folder, filename)

        reader = PdfReader(path)

        text = ""

        for page in reader.pages:
            text += page.extract_text() or ""

        print("\n==============================")
        print(filename)
        print("==============================")
        print(text[:500])

print("\nPDF reading completed!")