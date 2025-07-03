import os
import smtplib
from email.message import EmailMessage
from email.utils import formataddr
from dotenv import load_dotenv
import requests
import base64
from datetime import datetime

load_dotenv()

main_gmail = os.getenv('main_gmail')
app_password = os.getenv('app_password')
alias_email = os.getenv('alias_email')
custom_name = "Wishing Master"
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GEN_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-preview-image-generation:generateContent'

PROMPTS = {
    'morning': 'Write a beautifully designed HTML email for a cheerful morning greeting, including a motivational quote, a funny joke, a short inspiring story, and a professional 3D style. Include references to a sunrise and positivity.',
    'noon': 'Write a beautifully designed HTML email for a vibrant noon greeting, including a motivational quote, a funny joke, a short inspiring story, and a professional 3D style. Include references to energy and productivity.',
    'afternoon': 'Write a beautifully designed HTML email for a relaxing afternoon greeting, including a motivational quote, a funny joke, a short inspiring story, and a professional 3D style. Include references to calmness and focus.',
    'evening': 'Write a beautifully designed HTML email for a pleasant evening greeting, including a motivational quote, a funny joke, a short inspiring story, and a professional 3D style. Include references to winding down and gratitude.',
    'night': 'Write a beautifully designed HTML email for a peaceful night greeting, including a motivational quote, a funny joke, a short inspiring story, and a professional 3D style. Include references to rest and dreams.'
}

IMAGE_PROMPTS = {
    'morning': 'A 3D rendered sunrise over a futuristic city with greenery and positive vibes.',
    'noon': 'A 3D rendered cityscape at noon with vibrant activity and lush parks.',
    'afternoon': 'A 3D rendered afternoon scene with long shadows and a lively urban environment.',
    'evening': 'A 3D rendered sunset with glowing lights and a relaxing city atmosphere.',
    'night': 'A 3D rendered night view of a city with neon lights and a peaceful sky.'
}

GITHUB_PAGES_BASE_URL = os.getenv('GITHUB_PAGES_BASE_URL', 'https://yourusername.github.io/yourrepo/images/')


def generate_html_content(time_of_day):
    prompt = PROMPTS.get(time_of_day, PROMPTS['morning'])
    headers = {
        'x-goog-api-key': GEMINI_API_KEY,
        'Content-Type': 'application/json'
    }
    data = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {"responseModalities": ["TEXT"]}
    }
    response = requests.post(GEN_URL, headers=headers, json=data)
    response.raise_for_status()
    result = response.json()
    # Extract HTML content
    html = None
    for candidate in result.get('candidates', []):
        for part in candidate.get('content', {}).get('parts', []):
            if 'text' in part:
                html = part['text']
                break
    if not html:
        raise Exception('No HTML content found in Gemini response.')
    return html

def get_latest_image_url(time_of_day):
    images_dir = os.path.join(os.path.dirname(__file__), '..', 'images')
    files = [f for f in os.listdir(images_dir) if f.startswith(time_of_day) and f.endswith('.png')]
    if not files:
        return None
    latest_file = sorted(files)[-1]
    return GITHUB_PAGES_BASE_URL + latest_file

def send_mail(time_of_day, recipient):
    html_content = generate_html_content(time_of_day)
    image_url = get_latest_image_url(time_of_day)
    if image_url:
        # Insert image at the top of the email
        html_content = f'<div style="text-align:center;"><img src="{image_url}" style="max-width:100%;border-radius:16px;"></div>' + html_content
    msg = EmailMessage()
    msg['Subject'] = f'{time_of_day.capitalize()} Wishes from Wishing Master'
    msg['From'] = formataddr((custom_name, alias_email))
    msg['To'] = recipient
    msg.set_content('This is a multi-part message in MIME format.')
    msg.add_alternative(html_content, subtype='html')
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(main_gmail, app_password)
        smtp.send_message(msg)
        print(f'Email sent successfully to {recipient}!')

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python send_mail.py <time_of_day> <recipient_email>")
        exit(1)
    time_of_day = sys.argv[1]
    recipient = sys.argv[2]
    send_mail(time_of_day, recipient)