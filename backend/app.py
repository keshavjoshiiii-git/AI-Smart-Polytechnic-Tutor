import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from groq import Groq
from backend.syllabus import SYLLABUS

app = Flask(__name__, template_folder="../templates", static_folder="../static")
CORS(app)

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY")
)

SYSTEM_PROMPT = f"""
You are a professional AI teacher for Polytechnic Diploma students.

STRICT RULES:
- Always explain in simple english words and answer clearly.
- Do NOT use Hindi script.
- Do NOT use difficult hindi and english words.
- Use correct spelling and grammar.
- Double-check spelling before sending the answer.
- Keep answers clear, short, and student-friendly.
- Prefer English technical terms.
- Be polite and professional.
- Focus only on syllabus-based teaching.
- If a topic is outside syllabus, say: "This topic is not in the current syllabus... But I will still answer it for you" and then answer.

SYLLABUS:
{SYLLABUS}
"""

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask():
    try:
        data = request.json
        question = data.get("question")
        selected_language = data.get("language", "hinglish")

        # ✅ Language instruction
        if selected_language == "english":
            language_instruction = "Answer only in simple English."
        elif selected_language == "hindi":
            language_instruction = "Answer only in simple Hindi using Devanagari script."
        else:
            language_instruction = "Answer only in simple Hinglish using Roman script."

        # ✅ AI Call
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT + "\n\n" + language_instruction
                },
                {"role": "user", "content": question}
            ],
            model="llama-3.1-8b-instant",
            temperature=0.2
        )

        # ✅ Response cleanup
        answer = chat_completion.choices[0].message.content
        answer = answer.replace("**", "").replace("*", "")
        answer = answer.replace("..", ".").replace("  ", " ")

        return jsonify({"answer": answer})

    except Exception as e:
        return jsonify({"error": str(e)})


if __name__ == "__main__":
    app.run(debug=True)