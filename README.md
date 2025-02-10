# Flask Chatbot API

## 📌 Overview
Flask Chatbot API adalah aplikasi berbasis Flask yang memungkinkan pengguna untuk berkomunikasi dengan model OpenAI GPT-3.5 Turbo. Aplikasi ini menyimpan riwayat percakapan per pengguna dan dapat menghasilkan ringkasan percakapan secara otomatis.

## 🚀 Features
- 🔹 **Chat API**: Kirim pesan dan dapatkan respons dari OpenAI GPT-3.5 Turbo.
- 🔹 **History API**: Ambil riwayat chat berdasarkan pengguna.
- 🔹 **Summary API**: Dapatkan ringkasan percakapan pengguna.
- 🔹 **File-Based Storage**: Riwayat percakapan disimpan dalam file JSON per pengguna.

## 🛠 Installation
### 1️⃣ Clone Repository
```bash
git clone https://github.com/your-repo/flask-chatbot.git
cd flask-chatbot
```

### 2️⃣ Buat Virtual Environment & Install Dependencies
```bash
python -m venv env
source env/bin/activate  # Untuk macOS/Linux
env\Scripts\activate  # Untuk Windows
pip install -r requirements.txt
```

### 3️⃣ Buat File `.env`
Buat file `.env` di root folder proyek dan tambahkan API key OpenAI:
```plaintext
OPENAI_API_KEY=your_openai_api_key_here
```

### 4️⃣ Jalankan Aplikasi
```bash
python app.py
```
Aplikasi akan berjalan di `http://127.0.0.1:5000/`.

## 📡 API Endpoints
### 🔹 1. Chat dengan Bot
**Endpoint:** `/chat` (POST)
```json
{
    "user": "user1",
    "message": "Hello!"
}
```
**Response:**
```json
{
    "user": "user1",
    "message": "Hello!",
    "reply": "Hi there!"
}
```

### 🔹 2. Ambil Riwayat Chat
**Endpoint:** `/history` (GET)
```bash
GET /history?user=user1
```
**Response:**
```json
{
    "user": "user1",
    "history": [
        {"message": "Hello!", "response": "Hi there!"}
    ]
}
```

### 🔹 3. Ringkasan Chat
**Endpoint:** `/summarize` (GET)
```bash
GET /summarize?user=user1
```
**Response:**
```json
{
    "user": "user1",
    "summary": "The user greeted the bot and had a friendly conversation."
}
```

## 🔥 Troubleshooting
1️⃣ **Error: API Key Not Found**
   - Pastikan `.env` sudah dibuat dengan variabel `OPENAI_API_KEY`.
   - Pastikan `python-dotenv` sudah terinstal: `pip install python-dotenv`.

2️⃣ **Error: JSON Response Parsing Failed**
   - Cek apakah history tersimpan dalam format JSON yang valid.
   - Jalankan ulang server Flask setelah memperbaiki file history.

## 👨‍💻 Contributors
- **Your Name** - [GitHub](https://github.com/your-profile)

## 📜 License
MIT License

