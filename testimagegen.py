import requests
import base64
import json
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Access the environment variable
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# API endpoint
url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-preview-image-generation:generateContent"

# Headers
headers = {
    "x-goog-api-key": GEMINI_API_KEY,
    "Content-Type": "application/json"
}

# Request payload
payload = {
    "contents": [{
        "parts": [
            {
                "text": "Hi, can you create a 3d rendered image of a pig with wings and a top hat flying over a happy futuristic scifi city with lots of greenery?"
            }
        ]
    }],
    "generationConfig": {
        "responseModalities": ["TEXT", "IMAGE"]
    }
}

# Send POST request
response = requests.post(url, headers=headers, json=payload)

# Check status
if response.status_code == 200:
    res_json = response.json()
    parts = res_json.get("candidates", [])[0].get("content", {}).get("parts", [])

    image_found = False

    for i, part in enumerate(parts):
        if "inlineData" in part:
            image_data = part["inlineData"]["data"]
            with open("gemini-native-image.png", "wb") as f:
                f.write(base64.b64decode(image_data))
            print(f"✅ Image saved as gemini-native-image.png (from part {i})")
            image_found = True
        elif "text" in part:
            print(f"📝 Text response (part {i}): {part['text']}")

    if not image_found:
        print("❌ No image data found in the response parts.")
else:
    print(f"❌ Request failed with status code {response.status_code}")
    print(response.text)
