import os
import smtplib
from email.message import EmailMessage
from email.utils import formataddr
from dotenv import load_dotenv
import requests
import re

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


def clean_gemini_response(text):
    """Remove markdown backticks and trim extra whitespace."""
    cleaned = re.sub(r"```html|```", "", text)
    return cleaned.strip()


def generate_html_content(time_of_day):
    prompt = f"Generate a short, cheerful {time_of_day} greeting in HTML mail format. Add quotes, poems, funny info, serious facts, a short story, and health tips. Design should be Gmail-compatible and visually appealing. Remove markdown formatting."
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    response = requests.post(GEMINI_URL, headers=GEMINI_HEADERS, json=payload)
    if response.status_code == 200:
        res_json = response.json()
        parts = res_json.get("candidates", [])[0].get("content", {}).get("parts", [])
        raw_text = parts[0].get("text", "") if parts else ""
        return clean_gemini_response(raw_text)
    else:
        return f"<p>Wishing you a wonderful {time_of_day}!</p>"


def generate_custom_name(time_of_day):
    prompt = f"Suggest a short (1-4 words) creative sender name for a {time_of_day} greeting email. Avoid quotes or punctuation."
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    response = requests.post(GEMINI_URL, headers=GEMINI_HEADERS, json=payload)
    if response.status_code == 200:
        res_json = response.json()
        parts = res_json.get("candidates", [])[0].get("content", {}).get("parts", [])
        name = parts[0].get("text", "") if parts else f"Wishing Master ({time_of_day})"
        name = clean_gemini_response(name)
        return ' '.join(name.split()[:4])  # Limit to 4 words max
    else:
        return f"Wishing Master ({time_of_day})"


def get_all_image_urls(time_of_day):
    """Return list of URLs for all images matching the time_of_day."""
    images_dir = os.path.join(os.path.dirname(__file__), '..', 'images')
    files = [f for f in os.listdir(images_dir) if f.startswith(time_of_day) and f.endswith('.png')]
    return [GITHUB_PAGES_BASE_URL + f for f in sorted(files)] if files else []


def send_mail(time_of_day, recipients):
    image_urls = get_all_image_urls(time_of_day)
    custom_name = generate_custom_name(time_of_day).replace('\n', ' ').replace('\r', ' ').strip()
    
    # Construct image section
    html_images = ""
    for url in image_urls:
        html_images += f'<div style="text-align:center;margin:10px 0;"><img src="{url}" style="max-width:100%;border-radius:16px;"></div>'

    # Final HTML content
    html_content = html_images + generate_html_content(time_of_day)

    # Compose email
    msg = EmailMessage()
    msg['Subject'] = f'{time_of_day.capitalize()} Wishes from {custom_name}'
    msg['From'] = formataddr((custom_name, alias_email))
    msg['To'] = ', '.join(recipients)
    msg.set_content('This is a multi-part message in MIME format.')
    msg.add_alternative(html_content, subtype='html')

    # Send email
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(main_gmail, app_password)
        smtp.send_message(msg)
        print(f"✅ Email sent successfully to: {', '.join(recipients)}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python send_mail.py <time_of_day> <recipients_comma_separated>")
        exit(1)
    time_of_day = sys.argv[1]
    recipients = [email.strip() for email in sys.argv[2].split(',') if email.strip()]
    send_mail(time_of_day, recipients)
