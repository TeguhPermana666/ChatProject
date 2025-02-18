import os
from dotenv import load_dotenv
from anthropic import Anthropic

# Memuat variabel lingkungan dari file .env
load_dotenv()

# Ambil API key dari variabel lingkungan
API_KEY = os.getenv("ANTHROPIC_API_KEY")

if API_KEY is None:
    raise ValueError("API key is not set. Make sure to set ANTHROPIC_API_KEY environment variable.")

client = Anthropic(api_key=API_KEY)

message = client.messages.create(
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
                    "text": "Why is the ocean salty?"
                }
            ]
        }
    ]
)

print(message.content)
