from PyQt6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QTextBrowser, QLabel, QPushButton, QMessageBox, QTextEdit
from PyQt6.QtCore import pyqtSignal
from google_oauth2 import gmail_authenticate
import base64

class InboxWindow(QWidget):
    email_selected = pyqtSignal(dict)  

    def __init__(self, parent=None, translations=None):
        super().__init__(parent)
        self.parent_gui = parent
        self.translations = translations or {}  
        self.setWindowTitle("Inbox")
        layout = QVBoxLayout()

        self.email_list = QListWidget()
        self.email_list.itemClicked.connect(self.load_selected_email)

        self.email_body = QTextBrowser()

        self.refresh_button = QPushButton("🔄 Refresh Inbox")
        self.refresh_button.clicked.connect(self.load_inbox_messages)


        self.delete_button = QPushButton("🗑️ Delete Selected Email")
        self.delete_button.clicked.connect(self.delete_selected_email)

        layout.addWidget(QLabel("Inbox Messages"))
        layout.addWidget(self.email_list)
        layout.addWidget(QLabel("Email Body"))
        layout.addWidget(self.email_body)
        layout.addWidget(self.delete_button)
        layout.addWidget(self.refresh_button)

        self.setLayout(layout)
        self.load_inbox_messages()

    def load_inbox_messages(self):
        self.service = gmail_authenticate()
        result = self.service.users().messages().list(userId="me", labelIds=["INBOX"], maxResults=20).execute()
        self.messages = result.get("messages", [])
        self.email_list.clear()

        for msg in self.messages:
            detail = self.service.users().messages().get(userId="me", id=msg["id"]).execute()
            subject = self.get_header(detail, "Subject")
            sender = self.get_header(detail, "From")
            self.email_list.addItem(f"{subject} - {sender}")

    def get_header(self, message, name):
        headers = message.get("payload", {}).get("headers", [])
        return next((h["value"] for h in headers if h["name"] == name), "")

    def extract_body(self, payload):
        if "parts" in payload:
            for part in payload["parts"]:
                if part["mimeType"] == "text/plain":
                    return base64.urlsafe_b64decode(part["body"]["data"]).decode()
        elif "body" in payload and "data" in payload["body"]:
            return base64.urlsafe_b64decode(payload["body"]["data"]).decode()
        return "[No body]"

    def load_selected_email(self, item):
        idx = self.email_list.currentRow()
        msg_id = self.messages[idx]["id"]
        self.selected_msg_id = msg_id  # Save for deletion

        detail = self.service.users().messages().get(userId="me", id=msg_id, format="full").execute()
        payload = detail.get("payload", {})
        body = self.extract_body(payload)

        email_data = {
            "id": msg_id,
            "from": self.get_header(detail, "From"),
            "subject": self.get_header(detail, "Subject"),
            "body": body
        }

        self.email_body.setText(body)
        self.email_selected.emit(email_data)

    def delete_selected_email(self):
        if not hasattr(self, "selected_msg_id"):
            QMessageBox.warning(self, "Error", "Please select an email to delete.")
            return

        confirm = QMessageBox.question(self, "Confirm Delete", "Move this email to the Trash folder?")
        if confirm != QMessageBox.StandardButton.Yes:
            return

        try:
            self.service.users().messages().modify(
                userId="me",
                id=self.selected_msg_id,
                body={'addLabelIds': ['TRASH']}
            ).execute()
            QMessageBox.information(self, "Trashed", "Email moved to Trash.")
            self.load_inbox_messages()
            self.email_body.clear()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to move email to Trash:\n{e}")



