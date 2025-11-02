from PyQt6.QtGui import QIcon
from jinja2 import Template
from datetime import datetime
import sys
import ssl
import smtplib
import os
import json
import base64
from email.message import EmailMessage
from google_oauth2 import gmail_authenticate
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QTextEdit, QVBoxLayout,
    QPushButton, QComboBox, QScrollArea, QLineEdit
)
from inbox_window import InboxWindow

TEMPLATE_PATH = r"mail_template.html"

SETTINGS_PATH = r"Settings/Settings_email.json"

SETTING_LANG_PATH = r"Settings/Settings_Lang.json"

class MailTemplateGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mail Template Input")
        self.setWindowIcon(QIcon("ico/mail_template.ico"))
        self.load_translations()
        self.load_settings()
        self.init_ui()
        try:
            self.inbox_window = InboxWindow(parent=self, translations=self.translations)
            self.inbox_window.setWindowFlags(Qt.WindowType.Window)
            self.inbox_window.show()
            self.inbox_window.email_selected.connect(self.handle_email_selection)
            self.inbox_window.show()
        except Exception as e:
            print("[ERROR] InboxWindow failed to initialize:", e)


    def load_translations(self):
        try:
            with open(SETTING_LANG_PATH, "r", encoding="utf-8") as f:
                self.translations = json.load(f)
        except Exception as e:
            print("[ERROR] Failed to load translations:", e)
            self.translations = {}

    def load_settings(self):
        try:
            with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                self.settings = json.load(f)
        except Exception as e:
            print("[ERROR] Could not load settings.json:", e)
            self.settings = {"provider": "", "accounts": {}}

    def init_ui(self):
        layout = QVBoxLayout()

        # --- Provider selection ---
        self.provider_combo = QComboBox()
        providers = list(self.settings.get("accounts", {}).keys())
        if "gmail_oauth2" not in providers:
            providers.append("gmail_oauth2")
        self.provider_combo.addItems(providers)

        default_provider = self.settings.get("provider", "")
        if default_provider in providers:
            self.provider_combo.setCurrentText(default_provider)

        self.provider_combo.currentTextChanged.connect(self.update_credentials_for_provider)
        layout.addWidget(QLabel("Email Provider:"))
        layout.addWidget(self.provider_combo)

        # --- Email credentials ---
        self.email_input = QLineEdit()
        layout.addWidget(QLabel("Sender Email:"))
        layout.addWidget(self.email_input)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(QLabel("Sender Password:"))
        layout.addWidget(self.password_input)

        # --- Receiver email ---
        self.receiver_email_input = QLineEdit()
        layout.addWidget(QLabel("Receiver Email:"))
        layout.addWidget(self.receiver_email_input)

        # --- Subject ---
        self.subject_input = QLineEdit()
        layout.addWidget(QLabel("Email Subject:"))
        layout.addWidget(self.subject_input)

        # --- Name ---
        self.name_input = QLineEdit()
        layout.addWidget(QLabel("Recipient Name:"))
        layout.addWidget(self.name_input)
        self.name_input.textChanged.connect(self.update_greeting_text_from_lang)

        # --- Language selection ---
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["Deutsch", "English", "日本語"])
        self.lang_combo.currentIndexChanged.connect(self.update_greeting_text_from_lang)
        layout.addWidget(QLabel("Select Language:"))
        layout.addWidget(self.lang_combo)

        # --- Greeting ---
        self.greeting_text_input = QLineEdit()
        layout.addWidget(QLabel("Greeting:"))
        layout.addWidget(self.greeting_text_input)

        # --- Body Text ---
        self.text_input = QTextEdit()
        layout.addWidget(QLabel("Text:"))
        layout.addWidget(self.text_input)

        # --- Keypoint title ---
        self.keypoint_title_input = QLineEdit()
        layout.addWidget(QLabel("Keypoint Title:"))
        layout.addWidget(self.keypoint_title_input)

        # --- Keypoints ---
        self.keypoints_input = QTextEdit()
        layout.addWidget(QLabel("Keypoints (one per line):"))
        layout.addWidget(self.keypoints_input)

        # --- Steps title ---
        self.step_title_input = QLineEdit()
        layout.addWidget(QLabel("Steps Title:"))
        layout.addWidget(self.step_title_input)

        # --- Steps ---
        self.steps_input = QTextEdit()
        layout.addWidget(QLabel("Steps (one per line):"))
        layout.addWidget(self.steps_input)

        # --- Instruction text ---
        self.instruction_input = QTextEdit()
        layout.addWidget(QLabel("Instruction Text:"))
        layout.addWidget(self.instruction_input)

        # --- Sender Name ---
        self.sender_name_input = QLineEdit()
        layout.addWidget(QLabel("Sender Name:"))
        layout.addWidget(self.sender_name_input)

        # --- Sender Position ---
        self.sender_position_input = QLineEdit()
        layout.addWidget(QLabel("Sender Position:"))
        layout.addWidget(self.sender_position_input)

        # --- Company Name ---
        self.company_input = QLineEdit()
        layout.addWidget(QLabel("Company Name:"))
        layout.addWidget(self.company_input)

        # --- Remarks ---
        self.remarks_input = QLineEdit()
        layout.addWidget(QLabel("Remarks:"))
        layout.addWidget(self.remarks_input)   

        # --- Closing ---
        self.closing_input = QLineEdit()
        layout.addWidget(QLabel("Closing:"))
        layout.addWidget(self.closing_input)

        # --- Submit button ---
        self.submit_button = QPushButton("Generate & Send Email")
        self.submit_button.clicked.connect(self.generate_and_send_email)
        layout.addWidget(self.submit_button)
        
        # Put all widgets in a container widget
        content_widget = QWidget()
        content_widget.setLayout(layout)

        # Make scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(content_widget)

        # Final layout for the main window
        main_layout = QVBoxLayout()
        main_layout.addWidget(scroll)
        self.setLayout(main_layout)
        self.update_credentials_for_provider(self.provider_combo.currentText())

    def update_credentials_for_provider(self, provider):
        if provider == "gmail_oauth2":
            self.email_input.setText("me")  # Gmail API uses "me"
            self.email_input.setDisabled(True)
            self.password_input.clear()
            self.password_input.setDisabled(True)
            self.password_input.setPlaceholderText("OAuth2 in use")
        else:
            account = self.settings.get("accounts", {}).get(provider, {})
            self.email_input.setDisabled(False)
            self.password_input.setDisabled(False)
            self.email_input.setText(account.get("EMAIL_ADDRESS", ""))
            self.password_input.setText(account.get("EMAIL_PASSWORD", ""))

    def update_greeting_text_from_lang(self):
        lang = self.lang_combo.currentText()
        name = self.name_input.text().strip()
        greeting_tpl = self.translations.get("greeting", {}).get(lang, "{name},")
        closing_tpl = self.translations.get("closing", {}).get(lang, "Sincerely,")
        self.sender_name_input.setText(self.translations.get("sender_name", {}).get(lang, ""))
        self.sender_position_input.setText(self.translations.get("sender_position", {}).get(lang, ""))
        self.company_input.setText(self.translations.get("company_name", {}).get(lang,""))
        self.remarks_input.setText(self.translations.get("remarks", {}).get(lang, ""))
        self.greeting_text_input.setText(greeting_tpl.format(name=name))
        self.closing_input.setText(closing_tpl)

        # Update button text based on language
        self.button_text = self.translations.get("button_text", {}).get(lang, "My homepage")

    def generate_and_send_email(self):
        with open(TEMPLATE_PATH, encoding="utf-8") as f:
            tmpl = Template(f.read())
        
        rendered = tmpl.render(
            image_url="https://cxu.igu.mybluehost.me/wp-content/uploads/2025/06/Kapibarasan.png",
            greeting_text=self.greeting_text_input.text(),
            text=self.text_input.toPlainText(),
            keypoint_title=self.keypoint_title_input.text(),
            keypoints=[kp for kp in self.keypoints_input.toPlainText().splitlines() if kp.strip()],
            steps_title=self.step_title_input.text(),
            steps=[st for st in self.steps_input.toPlainText().splitlines() if st.strip()],
            instruction_text=self.instruction_input.toPlainText(),
            closing=self.closing_input.text(),
            name=self.sender_name_input.text(),
            position=self.sender_position_input.text(),
            company=self.company_input.text(),
            remarks=self.remarks_input.text(),
            call_to_action="",
            button_link="https://github.com/LoveKapibarasan/mail_templates",
            button_text=self.button_text,
            year=datetime.now().year,
            footer_brand="TryWorks",
            original_message=getattr(self, "original_message", "")
        )

        with open("output.html", "w", encoding="utf-8") as f:
            f.write(rendered)

        self.send_email(
            receiver_email=self.receiver_email_input.text(),
            subject=self.subject_input.text(),
            html_body=rendered
        )

    def send_email(self, receiver_email, subject, html_body):
        provider = self.provider_combo.currentText()
        account = self.settings.get("accounts", {}).get(provider, {})
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()
        server = account.get("server")
        port = account.get("port")

        if provider.lower() == "gmail_oauth2":
            try:
                print("[INFO] Using Gmail API with OAuth2...")
                service = gmail_authenticate()

                msg = EmailMessage()
                msg.set_content("This email requires an HTML-compatible client.")
                msg.add_alternative(html_body, subtype='html')
                msg["To"] = receiver_email
                msg["From"] = email
                msg["Subject"] = subject.replace('\n', "")

                encoded_message = base64.urlsafe_b64encode(msg.as_bytes()).decode()
                create_message = {'raw': encoded_message}

                send_result = service.users().messages().send(userId="me", body=create_message).execute()
                print(f"[SUCCESS] Gmail API: Email sent to {receiver_email}, Message ID: {send_result['id']}")

            except Exception as e:
                print(f"[ERROR] Gmail API failed: {e}")

        elif all([email, password, server, port]):
            msg = EmailMessage()
            msg.set_content("This email requires an HTML-compatible client.")
            msg.add_alternative(html_body, subtype='html')
            msg["Subject"] = subject.replace('\n', "")
            msg["From"] = email
            msg["To"] = receiver_email

            try:
                if port == 465:
                    context = ssl.create_default_context()
                    with smtplib.SMTP_SSL(server, port, context=context) as smtp:
                        smtp.login(email, password)
                        smtp.send_message(msg)
                else:
                    with smtplib.SMTP(server, port) as smtp:
                        smtp.starttls()
                        smtp.login(email, password)
                        smtp.send_message(msg)

                print(f"[SUCCESS] Email sent via {provider} to {receiver_email}")
            except Exception as e:
                print(f"[ERROR] SMTP failed: {e}")
        else:
            print("[ERROR] Missing SMTP configuration.")
        
    def handle_email_selection(self, email_data):
        # Set recipient to sender
        self.receiver_email_input.setText(email_data["from"])
        self.subject_input.setText(f"Re: {email_data['subject']}")
        self.text_input.setPlainText("")  # You can optionally include original text here
        self.instruction_input.setPlainText("")
        self.original_message = email_data['body'] 




if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MailTemplateGUI()
    window.show()
    sys.exit(app.exec())