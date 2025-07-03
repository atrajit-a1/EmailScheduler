import os
import smtplib
from email.message import EmailMessage
from email.utils import formataddr
from dotenv import load_dotenv
import requests
import re

# Load environment variables
load_dotenv()

main_gmail = os.getenv('main_gmail')
app_password = os.getenv('app_password')
alias_email = os.getenv('alias_email')
GITHUB_PAGES_BASE_URL = os.getenv('GITHUB_PAGES_BASE_URL', 'https://yourusername.github.io/yourrepo/images/')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
GEMINI_HEADERS = {
    "Content-Type": "application/json",
    "x-goog-api-key": GEMINI_API_KEY
}

THEME_STYLE_HINTS = {
    "morning": "Use bright and energetic colors like yellow, orange, and sky blue.",
    "afternoon": "Use light and clear tones like white, soft blue, and sunlit accents.",
    "evening": "Use warm, calming tones like peach, twilight blue, and soft gold.",
    "night": "Use dark mode styling with deep blues, purples, and glowing neon effects."
}

def clean_text(text):
    """Clean Gemini response: remove markdown/code blocks/newlines/symbols."""
    text = re.sub(r"```[\s\S]*?```", "", text)
    text = re.sub(r'[`*]', '', text)
    return text.replace('\n', ' ').replace('\r', ' ').strip()

def generate_html_content(time_of_day):
    theme_hint = THEME_STYLE_HINTS.get(time_of_day.lower(), "")
    prompt = (
        f"Generate a beautiful, Gmail-compatible HTML email body for a {time_of_day} greeting. "
        f"Include a heading, quote, poem, health tip, fun fact, and a short 3-line calming story. "
        f"Use inline CSS styles and no markdown or code blocks. Keep it professionally styled."
        f" Theme hint: {theme_hint}"
    )
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    response = requests.post(GEMINI_URL, headers=GEMINI_HEADERS, json=payload)
    if response.status_code == 200:
        parts = response.json().get("candidates", [])[0].get("content", {}).get("parts", [])
        raw_html = parts[0].get("text", "") if parts else ""
        cleaned = clean_text(raw_html)
        if len(cleaned) < 100 or not any(tag in cleaned.lower() for tag in ['<div', '<p', '<html']):
            return (
                f"<div style='text-align:center; font-family:sans-serif;'>"
                f"<h2 style='color:#333;'>Wishing You a Lovely {time_of_day.capitalize()}!</h2>"
                f"<p style='color:#666;'>May your day be filled with peace, purpose, and small joys.</p>"
                f"</div>"
            )
        return cleaned
    else:
        return f"<p style='font-family:sans-serif;'>Wishing you a wonderful {time_of_day}!</p>"

def generate_custom_name(time_of_day):
    prompt = f"Suggest a short (max 3 words) sender name for a {time_of_day} greeting email. No punctuation or symbols."
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    response = requests.post(GEMINI_URL, headers=GEMINI_HEADERS, json=payload)
    if response.status_code == 200:
        parts = response.json().get("candidates", [])[0].get("content", {}).get("parts", [])
        name = parts[0].get("text", "") if parts else f"{time_of_day.capitalize()} Sender"
        return ' '.join(clean_text(name).split()[:3])
    else:
        return f"{time_of_day.capitalize()} Sender"

def generate_subject_line(time_of_day):
    prompt = (
        f"Write one short, engaging subject line (max 8 words) for a {time_of_day} greeting email. "
        f"Return just one single line, not a list."
    )
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    response = requests.post(GEMINI_URL, headers=GEMINI_HEADERS, json=payload)
    if response.status_code == 200:
        parts = response.json().get("candidates", [])[0].get("content", {}).get("parts", [])
        subject = parts[0].get("text", "") if parts else f"{time_of_day.capitalize()} Greetings!"
        first_line = clean_text(subject).split('.')[0]
        return ' '.join(first_line.split()[:8])
    else:
        return f"{time_of_day.capitalize()} Greetings!"

def get_first_image_url(time_of_day):
    images_dir = os.path.join(os.path.dirname(__file__), '..', 'images')
    files = sorted([f for f in os.listdir(images_dir) if f.startswith(time_of_day) and f.endswith('.png')])
    return GITHUB_PAGES_BASE_URL + files[0] if files else None

def send_mail(time_of_day, recipients):
    image_url = get_first_image_url(time_of_day)
    custom_name = generate_custom_name(time_of_day)
    subject_line = generate_subject_line(time_of_day)

    html_content = ""
    if image_url:
        html_content += (
            f'<div style="text-align:center;margin-bottom:16px;">'
            f'<img src="{image_url}" alt="{time_of_day} image" style="max-width:100%;border-radius:16px;">'
            f'</div>'
        )

    html_content += generate_html_content(time_of_day)

    msg = EmailMessage()
    msg['Subject'] = clean_text(subject_line)
    msg['From'] = formataddr((clean_text(custom_name), alias_email))
    msg['To'] = ', '.join(recipients)
    msg.set_content('This is a multi-part message in MIME format.')
    msg.add_alternative(html_content, subtype='html')

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(main_gmail, app_password)
        smtp.send_message(msg)
        print(f"✅ Email sent successfully to: {', '.join(recipients)}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python send_mail.py <time_of_day> <recipients_comma_separated>")
        exit(1)
    time_of_day = sys.argv[1].lower()
    recipients = [email.strip() for email in sys.argv[2].split(',') if email.strip()]
    send_mail(time_of_day, recipients)
