
import os
import json
import sys

# Add auth directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'auth'))

def auth(sender_email):
    """
    Determine authentication method based on sender email
    """
    try:
        # Basic email validation
        if not sender_email or '@' not in sender_email or sender_email.count('@') != 1:
            print(f"Invalid email format: {sender_email}")
            return None
        
        # Extract domain part
        domain = sender_email.split('@')[1].lower()
        
        if any(provider in domain for provider in ['outlook', 'hotmail', 'live']):
            # Use Outlook/Azure authentication
            from outlook_azure import outlook_authenticate
            return outlook_authenticate()
        elif 'gmail' in domain:
            # Use Gmail authentication
            from google_oauth2 import gmail_authenticate_service
            return gmail_authenticate_service()
        else:
            # Unknown email provider
            print(f"Unknown email provider for: {sender_email}")
            return None
    except ImportError as e:
        print(f"Authentication module not found: {e}")
        return None
    except Exception as e:
        print(f"Authentication failed: {e}")
        return None




def send_email(data_file_path, html_output):
    """
    Send an email using the data file and HTML output
    """
    try:
        # Read the data.json to get email details
        with open(data_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        sender_email = data.get('senderemail', 'unknown@example.com')
        receiver_email = data.get('receiveremail', 'unknown@example.com')
        subject = data.get('subject', 'No Subject')
        receiver_name = data.get('receiver', {}).get('name', 'Recipient')
        
        print(f"=== EMAIL SENDING PROCESS ===")
        print(f"From: {sender_email}")
        print(f"To: {receiver_email} ({receiver_name})")
        print(f"Subject: {subject}")
        print(f"HTML content length: {len(html_output)} characters")
        
        # Save HTML output to file for preview
        output_dir = os.path.join(os.path.dirname(data_file_path), '..', 'output')
        os.makedirs(output_dir, exist_ok=True)
        
        html_file_path = os.path.join(output_dir, 'latest_email.html')
        with open(html_file_path, 'w', encoding='utf-8') as f:
            f.write(html_output)
        
        print(f"HTML saved to: {html_file_path}")
        
        # Authenticate and send email
        print("Authenticating with email service...")
        auth_service = auth(sender_email)
        
        if auth_service is None:
            print("Authentication failed or email provider not supported")
            print("Email saved locally but not sent")
            return False
        
        # Attempt to send email using the authenticated service
        print("Attempting to send email...")
        
        # Both Outlook and Gmail services have send_email method
        if hasattr(auth_service, 'send_email'):
            success = auth_service.send_email(
                sender_email=sender_email,
                recipient_email=receiver_email,
                recipient_name=receiver_name,
                subject=subject,
                html_body=html_output
            )
            
            if success:
                print("Email sent successfully!")
                return True
            else:
                print("Failed to send email through service")
                return False
        
        else:
            print("Authentication service doesn't support email sending")
            print("Email saved locally but not sent")
            return False
        
    except Exception as e:
        print(f'Failed to send email: {e}')
        return False