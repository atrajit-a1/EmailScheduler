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
GITHUB_PAGES_BASE_URL = os.getenv('GITHUB_PAGES_BASE_URL', 'https://yourusername.github.io/yourrepo/images/')

def get_latest_image_url(time_of_day):
    images_dir = os.path.join(os.path.dirname(__file__), '..', 'images')
    files = [f for f in os.listdir(images_dir) if f.startswith(time_of_day) and f.endswith('.png')]
    if not files:
        return None
    latest_file = sorted(files)[-1]
    return GITHUB_PAGES_BASE_URL + latest_file

def send_mail(time_of_day, recipients):
    image_url = get_latest_image_url(time_of_day)
    custom_name = generate_custom_name(time_of_day)
    html_content = f"<div style=\"text-align:center;\"><img src=\"{image_url}\" style=\"max-width:100%;border-radius:16px;\"></div>"
    html_content += generate_html_content(time_of_day)
    msg = EmailMessage()
    msg['Subject'] = f'{time_of_day.capitalize()} Wishes from {custom_name}'
    msg['From'] = formataddr((custom_name, alias_email))
    msg['To'] = ', '.join(recipients)
    msg.set_content('This is a multi-part message in MIME format.')
    msg.add_alternative(html_content, subtype='html')
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(main_gmail, app_password)
        smtp.send_message(msg)
        print(f"Email sent successfully to: {', '.join(recipients)}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python send_mail.py <time_of_day> <recipients_comma_separated>")
        exit(1)
    time_of_day = sys.argv[1]
    recipients = [email.strip() for email in sys.argv[2].split(',') if email.strip()]
    send_mail(time_of_day, recipients)
