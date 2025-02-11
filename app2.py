from flask import Flask, request, jsonify
import openai
import json
import os
from dotenv import load_dotenv

app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()

# Ambil API key dari .env
openai.api_key = os.getenv("OPENAI_API_KEY")

# File-based storage
def get_history_file(user):
    return f"history_{user}.json"

def save_chat(user, message, response):
    """Menyimpan percakapan user ke dalam file JSON"""
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

def get_chat_history(user):
    """Mengambil riwayat chat user dari file JSON"""
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
    """Endpoint untuk menerima pesan user dan mendapatkan respons dari AI"""
    data = request.json
    user = data.get("user")
    message = data.get("message")
    
    if not user or not message:
        return jsonify({"error": "User and message are required"}), 400

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": message}]
        )
        reply = response["choices"][0]["message"]["content"]
    except Exception as e:
        return jsonify({"error": f"Failed to get response: {str(e)}"}), 500

    save_chat(user, message, reply)
    return jsonify({"user": user, "message": message, "reply": reply})

@app.route("/history", methods=["GET"])
def history():
    """Endpoint untuk mengambil riwayat percakapan user"""
    user = request.args.get("user")
    if not user:
        return jsonify({"error": "User is required"}), 400
    
    history = get_chat_history(user)
    return jsonify({"user": user, "history": history})

@app.route("/summarize", methods=["GET"])
def summarize():
    """Endpoint untuk meringkas percakapan user dengan AI berdasarkan poin-poin penting"""
    user = request.args.get("user")
    if not user:
        return jsonify({"error": "User is required"}), 400

    history = get_chat_history(user)

    if not history:
        return jsonify({"summary": "No chat history found for this user"}), 200

    # Proses percakapan dengan menghapus duplikasi
    seen_messages = set()
    conversation = []
    
    for msg in history:
        message = msg.get("message", "").strip()
        response = msg.get("response", "").strip()
        if message and response and message not in seen_messages:
            conversation.append(f"User: {message}\nBot: {response}")
            seen_messages.add(message)

    conversation_text = "\n\n".join(conversation)

    prompt = (
        "Ringkas percakapan ini dengan poin-poin utama yang mencakup:\n"
        "- Kategori pertanyaan atau permintaan pengguna (misal: informasi, perintah, diskusi teknis, dll.)\n"
        "- Kesimpulan utama dari percakapan\n"
        "- Pola interaksi yang terlihat (misal: eksplorasi ide, troubleshooting, pertanyaan berulang)\n"
        "Berikan ringkasan yang informatif dan jelas."
    )

    try:
        summary_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": conversation_text}
            ]
        )

        summary = summary_response["choices"][0]["message"]["content"]

    except Exception as e:
        return jsonify({"error": f"Failed to summarize: {str(e)}"}), 500

    return jsonify({"user": user, "summary": summary})

if __name__ == "__main__":
    app.run(debug=True)
