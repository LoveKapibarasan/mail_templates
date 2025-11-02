import os
import base64
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email.message import EmailMessage

# 1. Define OAuth2 Scopes (Gmail full access)
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly',
          'https://www.googleapis.com/auth/gmail.send',
          'https://www.googleapis.com/auth/gmail.modify']

JSON_PATH = "client_secret.json"


class GmailAuth:
    """
    Gmail authentication service wrapper
    """
    
    def __init__(self):
        self.service = None
        
    def gmail_authenticate(self):
        """
        Authenticate with Gmail API
        
        Returns:
            Gmail service object or None
        """
        creds = None
        # token.pickle stores the user access and refresh tokens
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)

        # If no valid credentials, request login
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(JSON_PATH, SCOPES)
                creds = flow.run_local_server(port=0)

            # Save credentials
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        return build('gmail', 'v1', credentials=creds)
        
    def authenticate(self):
        """
        Authenticate with Gmail API
        """
        try:
            self.service = self.gmail_authenticate()
            return self.service is not None
        except Exception as e:
            print(f"Gmail authentication failed: {e}")
            return False
    
    def send_email(self, sender_email, recipient_email, recipient_name, subject, html_body):
        """
        Send email using Gmail API (compatible interface with Outlook service)
        """        
        try:
            # Create email message
            message = EmailMessage()
            message['To'] = f'{recipient_name} <{recipient_email}>'
            message['From'] = sender_email
            message['Subject'] = subject
            
            # Set HTML content
            message.set_content(html_body, subtype='html')
            
            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            # Send email using Gmail API
            send_message = self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            print(f"Gmail message sent successfully. Message ID: {send_message['id']}")
            return True
            
        except Exception as e:
            print(f"Failed to send Gmail message: {e}")
            return False


def gmail_authenticate_service():
    """
    Factory function to create Gmail authentication service
    """
    try:
        gmail_auth = GmailAuth()
        if gmail_auth.authenticate():
            return gmail_auth
        else:
            return None

    except Exception as e:
        print(f"Failed to create Gmail authentication service: {e}")
        return None
