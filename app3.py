import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from anthropic import Anthropic
import json
# Memuat variabel lingkungan dari file .env
load_dotenv()

# Ambil API key dari variabel lingkungan
API_KEY = os.getenv("ANTHROPIC_API_KEY")

if API_KEY is None:
    raise ValueError("❌ API Key tidak ditemukan! Pastikan sudah diatur dalam .env atau environment.")

client = Anthropic(api_key=API_KEY)
app = Flask(__name__)

# Fungsi untuk mendapatkan respons dari Claude API
def get_response_from_anthropic(prompt):
    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",  
            max_tokens=1000,
            temperature=0,
            system="You are a world-class poet. Respond only with short poems.",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ]
        )
        return response.content[0]["text"]
    except Exception as e:
        print(f"Error: {str(e)}")
        return "Error contacting Claude API"

# Fungsi untuk menyimpan dan mengambil riwayat chat
def get_history_file(user):
    return f"history_{user}.json"

def save_chat(user, message, response):
    file_path = get_history_file(user)
    history = []

    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as file:
                history = json.load(file)
        except (json.JSONDecodeError, IOError):
            history = []

    history.append({"message": message, "response": response})

    with open(file_path, "w") as file:
        json.dump(history, file, indent=4)

    print(f"✅ Saved chat for user {user}: {message} -> {response}")

def get_chat_history(user):
    file_path = get_history_file(user)
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as file:
                return json.load(file)
        except (json.JSONDecodeError, IOError):
            return []
    return []

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user = data.get("user")
    message = data.get("message")

    if not user or not message:
        return jsonify({"error": "User and message are required"}), 400

    print(f"📩 Received message from user {user}: {message}")

    try:
        reply = get_response_from_anthropic(message)
        print(f"📝 API response: {reply}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({"error": f"Failed to get response: {str(e)}"}), 500

    save_chat(user, message, reply)
    return jsonify({"user": user, "message": message, "reply": reply})

@app.route("/history", methods=["GET"])
def history():
    user = request.args.get("user")
    if not user:
        return jsonify({"error": "User is required"}), 400

    history = get_chat_history(user)
    print(f"📜 History for user {user}: {history}")
    return jsonify({"user": user, "history": history})

@app.route("/summarize", methods=["GET"])
def summarize():
    user = request.args.get("user")
    if not user:
        return jsonify({"error": "User is required"}), 400

    history = get_chat_history(user)
    print(f"📜 History for summarizing user {user}: {history}")

    if not history:
        return jsonify({"summary": "No chat history found for this user"}), 200

    conversation_text = "\n\n".join([f"User: {msg['message']}\nBot: {msg['response']}" for msg in history])

    prompt = (
        "Ringkas percakapan ini dengan poin-poin utama yang mencakup:\n"
        "- Kategori pertanyaan atau permintaan pengguna (misal: informasi, perintah, diskusi teknis, dll.)\n"
        "- Kesimpulan utama dari percakapan\n"
        "- Pola interaksi yang terlihat (misal: eksplorasi ide, troubleshooting, pertanyaan berulang)\n"
        "Berikan ringkasan yang informatif dan jelas."
    )

    try:
        summary = get_response_from_anthropic(prompt + "\n\n" + conversation_text)
        print(f"📄 Summary response: {summary}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({"error": f"Failed to summarize: {str(e)}"}), 500

    return jsonify({"user": user, "summary": summary})

if __name__ == "__main__":
    app.run(debug=True)
