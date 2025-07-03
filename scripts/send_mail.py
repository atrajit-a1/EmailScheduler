import os
import smtplib
from email.message import EmailMessage
from email.utils import formataddr
from dotenv import load_dotenv
import requests
import re

# Load .env variables
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

# Theme styles based on time of day
THEME_STYLE_HINTS = {
    "morning": "Use a bright and energetic color scheme with warm tones like yellow, orange, and sky blue.",
    "afternoon": "Use a light, clear design with shades of soft blue, white, and sunlit yellow.",
    "evening": "Use calm and cozy tones like peach, twilight blue, and soft gold.",
    "night": "Use dark mode styling with deep blues, purples, and neon accents for a calm and dreamy vibe."
}


def clean_text(text):
    """Remove markdown and formatting characters."""
    text = re.sub(r'[`*]', '', text)  # Remove backticks and asterisks
    return text.strip()


def generate_html_content(time_of_day):
    theme_hint = THEME_STYLE_HINTS.get(time_of_day.lower(), "")
    prompt = (
        f"Generate a professionally styled, visually appealing HTML email body for a {time_of_day} greeting. "
        f"The design should be modern, Gmail-compatible, and responsive with polished layout and spacing. "
        f"Include: a cheerful greeting, an inspirational quote, a short poem, one health tip, a fun fact, "
        f"and a calming 3-line story. "
        f"Use this style theme: {theme_hint} "
        f"Return raw inline-styled HTML only. No markdown, no backticks, no style blocks."
    )
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    response = requests.post(GEMINI_URL, headers=GEMINI_HEADERS, json=payload)
    if response.status_code == 200:
        res_json = response.json()
        parts = res_json.get("candidates", [])[0].get("content", {}).get("parts", [])
        raw_html = parts[0].get("text", "") if parts else ""
        return clean_text(raw_html)
    else:
        return f"<p>Wishing you a wonderful {time_of_day}!</p>"


def generate_custom_name(time_of_day):
    prompt = f"Suggest a short (max 3 words) sender name for a {time_of_day} themed email. Avoid symbols or formatting."
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    response = requests.post(GEMINI_URL, headers=GEMINI_HEADERS, json=payload)
    if response.status_code == 200:
        res_json = response.json()
        parts = res_json.get("candidates", [])[0].get("content", {}).get("parts", [])
        name = parts[0].get("text", "") if parts else f"Wishing Sender ({time_of_day})"
        name = clean_text(name)
        return ' '.join(name.split()[:3])  # Limit to 3 words
    else:
        return f"Wishing Sender ({time_of_day})"


def get_first_image_url(time_of_day):
    """Return the first matching image URL for time_of_day from ../images/ directory."""
    images_dir = os.path.join(os.path.dirname(__file__), '..', 'images')
    files = [f for f in sorted(os.listdir(images_dir)) if f.startswith(time_of_day) and f.endswith('.png')]
    return GITHUB_PAGES_BASE_URL + files[0] if files else None


def send_mail(time_of_day, recipients):
    image_url = get_first_image_url(time_of_day)
    custom_name = generate_custom_name(time_of_day)

    html_content = ""
    if image_url:
        html_content += (
            f'<div style="text-align:center;margin-bottom:16px;">'
            f'<img src="{image_url}" alt="{time_of_day} image" style="max-width:100%;border-radius:16px;">'
            f'</div>'
        )

    html_content += generate_html_content(time_of_day)

    # Compose email
    msg = EmailMessage()
    msg['Subject'] = f'{time_of_day.capitalize()} Wishes from {custom_name}'
    msg['From'] = formataddr((custom_name, alias_email))
    msg['To'] = ', '.join(recipients)
    msg.set_content('This is a multi-part message in MIME format.')
    msg.add_alternative(html_content, subtype='html')

    # Send email via Gmail SMTP
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(main_gmail, app_password)
        smtp.send_message(msg)
        print(f"✅ Email sent successfully to: {', '.join(recipients)}")


# CLI Entry Point
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python send_mail.py <time_of_day> <recipients_comma_separated>")
        exit(1)
    time_of_day = sys.argv[1]
    recipients = [email.strip() for email in sys.argv[2].split(',') if email.strip()]
    send_mail(time_of_day, recipients)
