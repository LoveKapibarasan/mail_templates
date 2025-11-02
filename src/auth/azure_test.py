import smtplib
from email.message import EmailMessage
import os

smtp_server = "smtp.office365.com"
smtp_port = 587
username = os.getenv("TEST_USERNAME")  
password = os.getenv("TEST_PASSWORD")  # MFA

print("debug", username, password)
msg = EmailMessage()
msg["Subject"] = "テスト"
msg["From"] = username
msg["To"] = "recipient@example.com"
msg.set_content("テスト本文")

with smtplib.SMTP(smtp_server, smtp_port) as smtp:
    smtp.set_debuglevel(1)             # デバッグ出力を有効にしてやり取りを確認する
    smtp.ehlo()
    smtp.starttls()                    # 必須：TLS に切り替え
    smtp.ehlo()
    smtp.login(username, password)     # ここで認証
    smtp.send_message(msg)
