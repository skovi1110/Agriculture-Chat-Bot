from flask import Flask, request, jsonify, render_template
from groq import Groq
from gtts import gTTS
import os

app = Flask(__name__)

# Groq Client
client = Groq(
    api_key="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"
)

# Supported model
MODEL = "openai/gpt-oss-20b"

# Static folder
os.makedirs("static", exist_ok=True)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    try:
        question = request.form.get("text")

        if not question:
            return jsonify({
                "text": "Please enter a question.",
                "voice": None
            })

        print("Question:", question)
        print("Calling Groq API...")

        response = client.chat.completions.create(
            model=MODEL,
            messages=[
               {
    "role": "system",
    "content": """
    You are an agriculture expert chatbot for Indian farmers.

    Detect the language used by the user automatically.

    If the user asks in Tamil, answer in Tamil.
    If the user asks in Telugu, answer in Telugu.
    If the user asks in Malayalam, answer in Malayalam.
    If the user asks in Kannada, answer in Kannada.
    If the user asks in English, answer in English.

    Give clear, simple, farmer-friendly answers.
    """
},
                {
                    "role": "user",
                    "content": question
                }
            ],
            temperature=0.5,
            max_tokens=500
        )

        answer = response.choices[0].message.content

        print("Answer Generated Successfully")

        # Generate Audio
        audio_path = os.path.join("static", "output.mp3")

        try:
            tts = gTTS(text=answer, lang="en")
            tts.save(audio_path)
            voice_url = "/static/output.mp3"
        except Exception as audio_error:
            print("Audio Error:", audio_error)
            voice_url = None

        return jsonify({
            "text": answer,
            "voice": voice_url
        })

    except Exception as e:
        print("FULL ERROR:", str(e))

        return jsonify({
            "text": f"Error: {str(e)}",
            "voice": None
        })


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)