import requests
import os
import json
from dotenv import load_dotenv
from flask import Flask, request, jsonify

load_dotenv()

API_KEY = os.getenv("ANTHROPIC_API_KEY")
API_URL = "https://api.anthropic.com/v1/messages"

if not API_KEY:
    raise ValueError("❌ API Key tidak ditemukan! Pastikan sudah diatur dalam .env atau environment.")

app = Flask(__name__)

# Fungsi untuk mendapatkan respons dari Claude API
def get_response_from_anthropic(prompt):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "anthropic-version": "2023-06-01"
    }
    data = {
        "model": "claude-3-sonnet-20240229",
        "max_tokens": 100,
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        response = requests.post(API_URL, headers=headers, json=data)
        
        # Jika respons error, tampilkan pesan
        if response.status_code == 401:
            return "❌ Unauthorized: API Key tidak valid atau expired."
        if response.status_code != 200:
            return f"❌ Error: {response.status_code} - {response.text}"

        response_data = response.json()
        print(f"Full API Response: {json.dumps(response_data, indent=2)}")  # Debugging log
        
        # Periksa struktur data respons dari Claude API
        if "content" in response_data and isinstance(response_data["content"], list):
            return response_data["content"][0].get("text", "No response found")
        return "No response found"
    except requests.RequestException as e:
        print(f"Error calling API: {str(e)}")
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
