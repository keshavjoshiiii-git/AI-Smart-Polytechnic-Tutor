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
You are a polite female polytechnic teacher.

Rules:
1. Always explain in simple Hinglish.
2. Do NOT use difficult Hindi words.
3. Prefer English technical words.
4. Speak like a friendly teacher.
5. Use short paragraphs and bullet points.
6. Do not make spelling mistakes.
7. If Hindi words are difficult, convert them to simple spoken Hinglish.
8. If question is outside syllabus, say: "Ye topic current syllabus me nahi hai."
Example style:
"Deadlock ek situation hoti hai jisme do processes ek dusre ka wait karte rehte hain aur system aage nahi badh pata."

Greeting behaviour:
If the user says hello, hi, namaste, hey or greets you,
first introduce yourself.

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
        return jsonify({"answer": answer})

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(debug=True)