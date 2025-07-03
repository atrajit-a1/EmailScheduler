import smtplib
from email.message import EmailMessage
from email.utils import formataddr
from dotenv import load_dotenv
import os
# Load environment variables from .env file
load_dotenv()

# Your main Gmail address and app password
main_gmail = os.getenv('main_gmail')
app_password = os.getenv('app_password')

# Alias and custom display name
alias_email = os.getenv('alias_email')
custom_name = "Wishing Master"

# Compose the message
msg = EmailMessage()
msg['Subject'] = 'Test email with custom sender name'
msg['From'] = formataddr((custom_name, alias_email))  # 👈 custom name + alias
msg['To'] = '2tbmagic@gmail.com'
msg.set_content('This email is sent using an alias and a custom sender name.')

# Send the message via Gmail SMTP with app password
with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
    smtp.login(main_gmail, app_password)
    smtp.send_message(msg)
    print('Email sent successfully!')
