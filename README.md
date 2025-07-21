# Mail Template GUI

A PyQt6-based desktop application for generating and sending HTML emails using customizable templates and multi-language support.

## Features

- **Easy-to-use GUI** for entering all email details.
- **Supports multiple email providers** (SMTP and Gmail OAuth2).
- **Multi-language greetings and closings** (Deutsch, English, 日本語).
- **Jinja2 HTML template rendering** for beautiful emails.
- **Saves rendered email as `output.html`** for preview.
- **Settings and translations loaded from JSON files**.

## Requirements

- Python 3.8+
- [PyQt6](https://pypi.org/project/PyQt6/)
- [Jinja2](https://pypi.org/project/Jinja2/)
- [google-auth, google-api-python-client](https://developers.google.com/gmail/api/quickstart/python) (for Gmail OAuth2)
- Other standard libraries: `smtplib`, `ssl`, `json`, `base64`, etc.

Install dependencies with:

```bash
pip install PyQt6 Jinja2 google-auth google-auth-oauthlib google-api-python-client
```

## Usage

1. **Configure your settings:**
   - Edit `Settings/Settings_email.json` for SMTP providers.
   - Edit `Settings/Settings_Lang.json` for translations.

    **Example `Settings/Settings_Lang.json`:**

   ```json
   {
     "greeting": {
       "English": "Dear {name},",
       "Deutsch": "Sehr geehrte/r {name},",
       "日本語": "{name} 様"
     },
     "closing": {
       "English": "Sincerely,",
       "Deutsch": "Mit freundlichen Grüßen,",
       "日本語": "敬具"
     },
     "sender_name": {
       "English": "John Doe",
       "Deutsch": "Johann Schmid",
       "日本語": "ジョン"
     }
     // ... add other fields as needed ...
    }
   ```

2. **Prepare your HTML template:**
   - Edit `mail_template.html` as needed.

3. **Run the application:**

   ```bash
   python substitute.py
   ```

4. **Fill out the form and click "Generate & Send Email".**
   - The email will be sent and the HTML saved as `output.html`.

## Directory Structure

```text
mail_templete/
├── Settings/
│   ├── Settings_email.json
│   └── Settings_Lang.json
├── ico/
│   └── mail_template.ico
├── substitute.py
├── mail_template.html
└── README.md
```

## Google OAuth2 Setup

To send emails via Gmail using OAuth2, you need to set up Google API credentials:

1. **Go to the [Google Cloud Console](https://console.cloud.google.com/apis/credentials).**
2. **Create a new project** (or select an existing one).
3. **Enable the Gmail API** for your project.
4. **Create OAuth client credentials:**
   - Go to "APIs & Services" > "Credentials".
   - Click "Create Credentials" > "OAuth client ID".
   - Choose "Desktop app" as the application type.
   - Download the `credentials.json` file and place it in your project directory.
5. **On first run,** the app will prompt you to log in with your Google account and authorize access. This will generate a `token.json` file for future use.

**Note:**  
- Never commit your `credentials.json` or `token.json` to version control.
- For more details, see the [Gmail API Python Quickstart](https://developers.google.com/gmail/api/quickstart/python).
## Notes

- For Gmail OAuth2, you must set up Google API credentials. See [Gmail API Python Quickstart](https://developers.google.com/gmail/api/quickstart/python).
- The application supports scrollable forms for usability.
- All email content is rendered using the Jinja2 template engine.

## License

MIT License

---

**Author:** Takanori Nagashima