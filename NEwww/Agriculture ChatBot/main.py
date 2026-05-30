import os
import time
from groq import Groq
from gtts import gTTS

# Read Groq API key from environment when available (safer than hardcoding).
# Falls back to the embedded key if the env var is not set so the script still runs.
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
if not GROQ_API_KEY:
    print("Warning: GROQ_API_KEY not set in environment; using key embedded in file.")
    GROQ_API_KEY = "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"

groq_client = Groq(api_key=GROQ_API_KEY)

def transcribe_audio(filepath):
    with open(filepath, "rb") as f:
        response = groq_client.audio.transcriptions.create(
            model="whisper-large-v3-turbo",
            file=f,
        )
    return response.text

def get_answer(question):
    # Use GROQ_MODEL env var if provided, otherwise default to a recommended supported model.
    model = os.environ.get("GROQ_MODEL", "openai/gpt-oss-120b")
    if "GROQ_MODEL" not in os.environ:
        print(f"Info: GROQ_MODEL not set — defaulting to '{model}'. Set GROQ_MODEL to override.")

    try:
        response = groq_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful agriculture chatbot for Indian farmers."},
                {"role": "user", "content": "Give a Brief Of Agriculture Seasons in India"},
                {"role": "system", "content": "In India, the agricultural season consists of three major seasons: the Kharif (monsoon), the Rabi (winter), and the Zaid (summer)..."},
                {"role": "user", "content": question}
            ]
        )
    except Exception as e:
        # Surface helpful guidance if model was decommissioned or request fails
        print("API request failed:", e)
        print("If the error message mentions a decommissioned model, set a supported model in the GROQ_MODEL environment variable.")
        print("Reference: https://console.groq.com/docs/deprecations")
        raise

    return response.choices[0].message.content

def typing_effect(text, delay=0.03):
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()  # Newline at end

def text_to_speech(text, filename):
    tts = gTTS(text)
    output_path = f"{filename}.mp3"
    tts.save(output_path)
    return output_path

def main():
    mode = input("Choose input type ('text' or 'audio'): ").strip().lower()

    if mode == 'text':
        question = input("Enter your question: ").strip()

    elif mode == 'audio':
        filepath = input("Enter the path to your audio file: ").strip()
        if not os.path.exists(filepath):
            print("❌ File not found.")
            return
        print("🎤 Transcribing audio...")
        question = transcribe_audio(filepath)
        print(f"📝 Transcribed Text: {question}")

    else:
        print("❌ Invalid input type. Use 'text' or 'audio'.")
        return

    print("🤖 Getting response from LLM...")
    answer = get_answer(question)

    print("\n✅ Answer:")
    typing_effect(answer) 

    print("\n🔊 Converting answer to speech...")
    audio_file = text_to_speech(answer, "response_audio")
    print(f"🎧 Voice saved to: {audio_file}")

if __name__ == "__main__":
    main()
