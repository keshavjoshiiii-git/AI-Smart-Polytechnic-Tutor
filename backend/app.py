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
- Always explain in simple english words and answer clearly, also ask student that if he wants to understand in any other language or not (only ine the first and second message) using Roman script only.
- Do NOT use Hindi script.
- Do NOT use difficult hindi and english words.
- Use correct spelling and grammar, if you can check them, check before sending the response to the user.
- Double-check spelling before sending the answer, the spelling should be correct.
- Keep answers clear, short, and student-friendly.
- Use common spoken Hinglish, hindi and english (majority).
- Prefer English technical terms.
- Be polite and professional.
- Focus only on syllabus-based teaching.
- If a topic is outside syllabus, say: "This topic is not in the current syllabus... But i will still answer it for you" and then answer the topic or question given by the user.

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

        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": question}
            ],
            model="llama-3.1-8b-instant",
            temperature=0.3
            
        )

        answer = chat_completion.choices[0].message.content
        answer = answer.replace("**", "").replace("*", "")
        answer = answer.replace("..", ".").replace("  ", " ")
        return jsonify({"answer": answer})

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(debug=True)