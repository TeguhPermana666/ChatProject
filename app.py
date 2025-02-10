from flask import Flask, request, jsonify
import openai
import json
import os
from dotenv import load_dotenv  # Import dotenv

app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()

# Ambil API key dari .env
openai.api_key = os.getenv("OPENAI_API_KEY")

# File-based storage
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
    user = request.args.get("user")
    if not user:
        return jsonify({"error": "User is required"}), 400
    
    history = get_chat_history(user)
    return jsonify({"user": user, "history": history})

@app.route("/summarize", methods=["GET"])
def summarize():
    user = request.args.get("user")
    if not user:
        return jsonify({"error": "User is required"}), 400
    
    history = get_chat_history(user)

    # Debugging: Cetak isi history untuk melihat formatnya
    print(f"Chat history for {user}: {history}")

    if not history:
        return jsonify({"summary": "No chat history found for this user"}), 200

    # Periksa apakah semua entri memiliki 'message' dan 'response'
    conversation = "\n".join([
        f"User: {msg.get('message', '[MISSING]')}\nBot: {msg.get('response', '[MISSING]')}"
        for msg in history if "message" in msg and "response" in msg
    ])

    try:
        summary_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Summarize this conversation:"},
                {"role": "user", "content": conversation}
            ]
        )

        summary = summary_response["choices"][0]["message"]["content"]
    
    except Exception as e:
        print(f"Error in summarize(): {str(e)}")  # Debugging log
        return jsonify({"error": f"Failed to summarize: {str(e)}"}), 500
    
    return jsonify({"user": user, "summary": summary})



if __name__ == "__main__":
    app.run(debug=True)
