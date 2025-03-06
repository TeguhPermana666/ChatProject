from flask import Flask, request, jsonify
import openai
import json
import os
from dotenv import load_dotenv

app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Folder untuk menyimpan chat history
HISTORY_DIR = "chat_history"

# Pastikan folder history ada
if not os.path.exists(HISTORY_DIR):
    os.makedirs(HISTORY_DIR)

def get_history_file(user):
    """Mendapatkan path file history untuk user tertentu"""
    return os.path.join(HISTORY_DIR, f"history_{user}.json")

def save_chat(user, message, response):
    """Menyimpan history chat user"""
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
    """Mengambil history chat user"""
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
    """API untuk menangani chat user"""
    data = request.get_json()

    if not data or "user" not in data or "message" not in data:
        return jsonify({"error": "Invalid request"}), 400

    user = data["user"]
    message = data["message"]

    # Cek apakah ada riwayat sebelumnya untuk user
    history = get_chat_history(user)
    history_text = "\n".join([f"{user}: {h['message']}\n{h['response']}" for h in history])

    # Prompt dengan konteks percakapan sebelumnya
    prompt = f"""
    Anda adalah seorang Consultant Artificial Intelligence yang membantu pelanggan dengan ramah dan profesional dalam menyelesaikan permasalahan riset dan pengembangan produk AI. Berikut adalah riwayat percakapan dengan {user}:

    {history_text}

    {user}: {message}
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "Anda adalah seorang Consultant AI yang ahli dalam riset dan pengembangan produk AI. Jawablah dengan profesional dan langsung ke inti permasalahan."},
                      {"role": "user", "content": prompt}]
        )
        bot_reply = response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return jsonify({"error": f"Gagal memproses chat: {str(e)}"}), 500

    # Simpan chat user
    save_chat(user, message, bot_reply)

    return jsonify({"reply": bot_reply})

@app.route("/summary", methods=["GET"])
def summary():
    """Membuat ringkasan percakapan user"""
    user = request.args.get("user")
    if not user:
        return jsonify({"error": "User is required"}), 400

    history = get_chat_history(user)
    if not history:
        return jsonify({"summary": "Tidak ada riwayat percakapan."})

    # Batasi hanya 5 percakapan terakhir agar lebih ringkas
    recent_history = history[-5:]
    conversation_text = "\n".join([f"{user}: {h['message']}\n{h['response']}" for h in recent_history])

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ringkas percakapan berikut dengan singkat dan jelas berdasarkan isi context percakapan yang dilakukan selayaknya menjadi AI Consultant, jangan ajukan pertanyaan ke user."},
                {"role": "user", "content": conversation_text}
            ]
        )
        summary_text = response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        summary_text = "Ringkasan tidak dapat dibuat secara otomatis. Berikut adalah percakapan terakhir:\n" + conversation_text

    return jsonify({"user": user, "summary": summary_text})



if __name__ == "__main__":
    app.run(debug=True)
