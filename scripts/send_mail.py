import os
import smtplib
from email.message import EmailMessage
from email.utils import formataddr
from dotenv import load_dotenv
import requests
import re
import sys

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
    """Clean Gemini response: remove markdown/code blocks/newlines/symbols while preserving HTML"""
    # Remove code block markers
    text = re.sub(r"```(html)?", "", text, flags=re.IGNORECASE)
    # Remove special formatting characters
    text = re.sub(r'[`*#\-]', '', text)
    # Collapse multiple spaces/newlines
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def create_fallback_html(time_of_day):
    """Create rich fallback HTML with all required sections"""
    theme_colors = {
        "morning": {"bg": "#fff8e1", "text": "#5d4037", "accent": "#ffd54f"},
        "afternoon": {"bg": "#e3f2fd", "text": "#1565c0", "accent": "#64b5f6"},
        "evening": {"bg": "#f3e5f5", "text": "#6a1b9a", "accent": "#ba68c8"},
        "night": {"bg": "#0d47a1", "text": "#e3f2fd", "accent": "#42a5f5"}
    }
    colors = theme_colors.get(time_of_day.lower(), theme_colors["morning"])
    
    return f"""
<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; 
            background-color: {colors['bg']}; color: {colors['text']}; border-radius: 10px;">
    <h2 style="text-align: center; color: {colors['accent']};">Good {time_of_day.capitalize()}!</h2>
    
    <div style="background: rgba(255,255,255,0.7); padding: 15px; border-radius: 8px; margin: 15px 0;">
        <h3 style="color: {colors['accent']};">📜 Quote</h3>
        <p style="font-style: italic;">"The only way to do great work is to love what you do." - Steve Jobs</p>
    </div>
    
    <div style="background: rgba(255,255,255,0.7); padding: 15px; border-radius: 8px; margin: 15px 0;">
        <h3 style="color: {colors['accent']};">✍️ Poem</h3>
        <p>Each morning brings a hidden blessing,<br>
        A fresh attempt at happiness,<br>
        Embrace the day with open arms,<br>
        And life's abundant kindness.</p>
    </div>
    
    <div style="background: rgba(255,255,255,0.7); padding: 15px; border-radius: 8px; margin: 15px 0;">
        <h3 style="color: {colors['accent']};">🔍 Fun Fact</h3>
        <p>Honey never spoils. Archaeologists have found pots of honey in ancient Egyptian tombs that are over 3,000 years old and still perfectly edible!</p>
    </div>
    
    <div style="background: rgba(255,255,255,0.7); padding: 15px; border-radius: 8px; margin: 15px 0;">
        <h3 style="color: {colors['accent']};">💡 Wellness Tip</h3>
        <p>Start your day with a glass of water to hydrate your body and kickstart your metabolism.</p>
    </div>
    
    <div style="background: rgba(255,255,255,0.7); padding: 15px; border-radius: 8px; margin: 15px 0;">
        <h3 style="color: {colors['accent']};">📖 Short Story</h3>
        <p>As the sun peeked through the curtains, Maya stretched and smiled. Today was full of possibilities. She decided right then to try something new - and that decision changed everything.</p>
    </div>
</div>
"""

def generate_html_content(time_of_day):
    theme_hint = THEME_STYLE_HINTS.get(time_of_day.lower(), "")
    prompt = (
        f"Create a professional HTML email for a {time_of_day} greeting. Include these EXACT sections:\n"
        f"1. Header: 'Good [Time_of_Day]!' in large text\n"
        f"2. Motivational quote (clearly labeled)\n"
        f"3. Short poem (3-4 lines)\n"
        f"4. Interesting fact (labeled 'Fun Fact')\n"
        f"5. Wellness tip\n"
        f"6. 2-3 line short story\n\n"
        f"Use: Inline CSS ONLY, no external resources\n"
        f"Avoid: Markdown, code blocks, lists, or special symbols\n"
        f"Structure: Wrap each section in a DIV with unique background\n"
        f"Design: {theme_hint}\n"
        f"Important: Minimum 500 characters of CONTENT (excluding HTML tags)"
    )
    
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        response = requests.post(GEMINI_URL, headers=GEMINI_HEADERS, json=payload, timeout=30)
        if response.status_code == 200:
            raw_html = response.json()["candidates"][0]["content"]["parts"][0]["text"]
            cleaned = clean_text(raw_html)
            
            # Validation checks
            required_keywords = ["quote", "poem", "fact", "tip", "story"]
            found_keywords = sum(1 for kw in required_keywords if kw in cleaned.lower())
            
            if len(cleaned) < 500 or found_keywords < 3 or "<div" not in cleaned.lower():
                print("⚠️ Gemini response incomplete. Using enhanced fallback")
                return create_fallback_html(time_of_day)
            return cleaned
    except Exception as e:
        print(f"⚠️ Gemini API error: {str(e)}")
    
    return create_fallback_html(time_of_day)

def generate_custom_name(time_of_day):
    prompt = f"Suggest a short (max 3 words) sender name for a {time_of_day} greeting email. No punctuation or symbols."
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        response = requests.post(GEMINI_URL, headers=GEMINI_HEADERS, json=payload, timeout=15)
        if response.status_code == 200:
            name = response.json()["candidates"][0]["content"]["parts"][0]["text"]
            return ' '.join(clean_text(name).split()[:3])
    except Exception:
        pass
    
    return f"{time_of_day.capitalize()} Companion"

def generate_subject_line(time_of_day):
    prompt = (
        f"Write one short, engaging subject line (max 8 words) for a {time_of_day} greeting email. "
        f"Return just one single line, not a list."
    )
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        response = requests.post(GEMINI_URL, headers=GEMINI_HEADERS, json=payload, timeout=15)
        if response.status_code == 200:
            subject = response.json()["candidates"][0]["content"]["parts"][0]["text"]
            first_line = clean_text(subject).split('.')[0]
            return ' '.join(first_line.split()[:8])
    except Exception:
        pass
    
    return f"Wishing You a Wonderful {time_of_day.capitalize()}!"

def get_first_image_url(time_of_day):
    try:
        # Get directory two levels up from current script location
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        images_dir = os.path.join(base_dir, 'images')
        files = sorted([f for f in os.listdir(images_dir) 
                       if f.startswith(time_of_day) and f.endswith('.png')])
        return GITHUB_PAGES_BASE_URL + files[0] if files else None
    except Exception:
        return None

def send_mail(time_of_day, recipients):
    # image_url = get_first_image_url(time_of_day)
    custom_name = generate_custom_name(time_of_day)
    subject_line = generate_subject_line(time_of_day)

    html_content = ""
    # if image_url:
    with open("filename.txt","r") as f:
        rootName = f.read()
    image_url=GITHUB_PAGES_BASE_URL+rootName
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
    msg.set_content('Please view this message in an HTML email client.')
    msg.add_alternative(html_content, subtype='html')

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(main_gmail, app_password)
            smtp.send_message(msg)
            print(f"attached file uri is:{image_url}")
            print(f"✅ Email sent successfully to: {', '.join(recipients)}")
    except Exception as e:
        print(f"❌ Email failed to send: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python send_mail.py <time_of_day> <recipients_comma_separated>")
        exit(1)
    
    time_of_day = sys.argv[1].lower()
    valid_times = ["morning", "afternoon", "evening", "night"]
    
    if time_of_day not in valid_times:
        print(f"❌ Invalid time_of_day. Must be one of: {', '.join(valid_times)}")
        exit(1)
        
    recipients = [email.strip() for email in sys.argv[2].split(',') if email.strip()]
    send_mail(time_of_day, recipients)
