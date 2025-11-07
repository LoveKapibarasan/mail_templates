from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QTextEdit, QVBoxLayout,
    QPushButton, QMessageBox, QHBoxLayout, QComboBox
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize
import sys
import os
import json
import webbrowser
from datetime import datetime

# Add script directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'script'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'type'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'email'))

from substitute import template
from Lang import Lang, Langs
from Mode import Mode, Modes, Gender, Formal
from send_email import send_email

class MailTemplateGUI(QWidget):
    """Main email template GUI application"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.setup_paths()
    
    def init_ui(self):
        self.setWindowTitle("Mail Template Generator")
        self.setGeometry(100, 100, 500, 400)
        
        # Set window icon (try PNG first for better Linux compatibility, then ICO)
        icon_dir = os.path.join(os.path.dirname(__file__), '..', 'ico')
        # Set window icon
        icon_path = os.path.join(os.path.dirname(__file__), '..', 'ico', 'mail_template.ico')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        layout = QVBoxLayout()
        
        # 1. Sender Email input
        sender_layout = QHBoxLayout()
        sender_layout.addWidget(QLabel("Sender:"))
        self.sender_input = QLineEdit()
        self.sender_input.setPlaceholderText("your-name@example.com")
        sender_layout.addWidget(self.sender_input)
        layout.addLayout(sender_layout)

        # 2. Receiver Email input
        receiver_layout = QHBoxLayout()
        receiver_layout.addWidget(QLabel("Receiver:"))
        self.receiver_input = QLineEdit()
        self.receiver_input.setPlaceholderText("recipient@example.com")
        receiver_layout.addWidget(self.receiver_input)
        layout.addLayout(receiver_layout)
        
        # 3. Subject input
        subject_layout = QHBoxLayout()
        subject_layout.addWidget(QLabel("Subject:"))
        self.subject_input = QLineEdit()
        self.subject_input.setPlaceholderText("Email Subject")
        subject_layout.addWidget(self.subject_input)
        layout.addLayout(subject_layout)

        # 4. Receiver Name input
        receiver_name_layout = QHBoxLayout()
        receiver_name_layout.addWidget(QLabel("Receiver Name:"))
        self.receiver_name_input = QLineEdit()
        self.receiver_name_input.setPlaceholderText("Recipient Name")
        receiver_name_layout.addWidget(self.receiver_name_input)
        layout.addLayout(receiver_name_layout)

        # 5. Body input
        layout.addWidget(QLabel("Body:"))
        self.body_input = QTextEdit()
        self.body_input.setPlaceholderText("Enter your email message here...")
        layout.addWidget(self.body_input)

        # 6. Language combo
        # import LANG type to find all candidates
        lang_layout = QHBoxLayout()
        lang_layout.addWidget(QLabel("Language:"))
        self.lang_combo = QComboBox()
        # Get available languages from Langs type
        langs_container = Langs()
        available_lang_codes = langs_container.get_language_codes()
        self.lang_combo.addItems(available_lang_codes)
        lang_layout.addWidget(self.lang_combo)
        layout.addLayout(lang_layout)

        # 7. Mode button
        # import MODE type to find all candidates
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Mode:"))
        self.mode_combo = QComboBox()
        # Get available modes from Modes type
        modes_container = Modes()
        available_genders = modes_container.get_available_genders()
        available_formal_levels = modes_container.get_available_formal_levels()
        # Create mode combinations
        for gender in available_genders:
            for formal in available_formal_levels:
                mode_display = f"{gender.title()}, {formal.title()}"
                self.mode_combo.addItem(mode_display, (gender, formal))
        mode_layout.addWidget(self.mode_combo)
        layout.addLayout(mode_layout)
        
        # Send button
        self.send_btn = QPushButton("Send Email")
        self.send_btn.clicked.connect(self.send_email)
        layout.addWidget(self.send_btn)
        
        self.setLayout(layout)

    def setup_paths(self):
        """Setup file paths"""
        self.settings_dir = os.path.join(os.path.dirname(__file__), '..', 'settings')
        self.data_file = os.path.join(self.settings_dir, 'data.json')
        os.makedirs(self.settings_dir, exist_ok=True)
    
    def save_and_generate(self):
        """Save data to settings/data.json and generate template"""
        try:
            # Get selected mode
            mode_data = self.mode_combo.currentData()
            gender, formal = mode_data if mode_data else (Gender.NEUTRAL, Formal.FORMAL)
            
            # Create filled_data from form inputs
            filled_data = {
                "senderemail": self.sender_input.text() or "sender@example.com",
                "receiveremail": self.receiver_input.text() or "recipient@example.com",
                "receiver": {
                    "name": self.receiver_name_input.text() or "Recipient"
                },
                "subject": self.subject_input.text() or "subject",
                "body": self.body_input.toPlainText() or "This is a test email message.",
                "mode": {
                    "gender": gender,
                    "formal": formal
                }
            }
            
            # Save filled_data to data.json
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(filled_data, f, indent=2, ensure_ascii=False)
            
            output = template(self.lang_combo.currentText(), 'data.json')
            return output
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed: {str(e)}")
            return None
    
    def send_email(self):
        """Send email using the generated template"""
        try:
            # Generate template first
            output = self.save_and_generate()
            if output:
                # currently not implemented
                send_email(self.data_file, output)
                QMessageBox.information(self, "Success", "Email sent successfully!")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed: {str(e)}")

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Simple Mail Template Generator")
    app.setApplicationVersion("1.2")
    window = MailTemplateGUI()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()