# Email Scheduler with Gemini 2.0 Flash Integration

## Features
- Sends beautifully designed HTML emails at scheduled times (morning, noon, afternoon, evening, night) according to IST.
- Uses Gemini 2.0 Flash API to generate dynamic HTML content and 3D images tailored to the time of day.
- Automatically commits generated images to the repository and includes their GitHub Pages URLs in emails.
- GitHub Actions workflow schedules email sending and supports manual dispatch for testing.

## Project Structure
- `scripts/` — Python scripts for email sending and image generation
- `images/` — Folder for generated images
- `.github/workflows/` — GitHub Actions workflow files
- `.env` — Environment variables (API keys, email credentials)

## Setup
1. Add your Gmail credentials and Gemini API key to `.env`:
   ```env
   main_gmail=your_main_gmail@gmail.com
   app_password=your_gmail_app_password
   alias_email=your_alias@gmail.com
   GEMINI_API_KEY=your_gemini_api_key
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Configure your repository for GitHub Pages (for image hosting).

## Usage
- Emails are sent automatically at 9:00 AM, 12:00 PM, 4:00 PM, 7:00 PM, and 10:00 PM IST.
- Images and email content are generated dynamically for each time slot.
- Use the workflow dispatcher to test sending emails manually.

---

This project is inspired by the reference `test.py` and extends it with advanced automation and AI-powered content generation.