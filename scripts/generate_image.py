import os
import requests
import base64
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GEN_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-preview-image-generation:generateContent'

PROMPTS = {
    'morning': 'A 3D rendered sunrise over a futuristic city with greenery and positive vibes.',
    'noon': 'A 3D rendered cityscape at noon with vibrant activity and lush parks.',
    'afternoon': 'A 3D rendered afternoon scene with long shadows and a lively urban environment.',
    'evening': 'A 3D rendered sunset with glowing lights and a relaxing city atmosphere.',
    'night': 'A 3D rendered night view of a city with neon lights and a peaceful sky.'
}

def get_prompt(time_of_day):
    return PROMPTS.get(time_of_day, PROMPTS['morning'])

def generate_image(time_of_day):
    prompt = get_prompt(time_of_day)
    headers = {
        'x-goog-api-key': GEMINI_API_KEY,
        'Content-Type': 'application/json'
    }
    data = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]}
    }
    response = requests.post(GEN_URL, headers=headers, json=data)
    response.raise_for_status()
    result = response.json()
    # Extract base64 image data
    image_data = None
    for candidate in result.get('candidates', []):
        for part in candidate.get('content', {}).get('parts', []):
            if 'inlineData' in part and part['inlineData']['mimeType'].startswith('image/'):
                image_data = part['inlineData']['data']
                break
    if not image_data:
        raise Exception('No image data found in Gemini response.')
    # Unique filename
    now = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"images/{time_of_day}_{now}.png"
    os.makedirs('images', exist_ok=True)
    with open(filename, 'wb') as f:
        f.write(base64.b64decode(image_data))
    print(f"Image saved as {filename}")
    return filename

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python generate_image.py <time_of_day>")
        exit(1)
    time_of_day = sys.argv[1]
    generate_image(time_of_day)