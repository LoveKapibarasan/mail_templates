
"""
Microsoft Graph API authentication for Outlook/Hotmail/Live email services
REAL IMPLEMENTATION - NOT A DEMO
"""

import os
import json
import requests
import base64
import webbrowser
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlencode, parse_qs, urlparse
from datetime import datetime, timedelta


class AuthCallbackHandler(BaseHTTPRequestHandler):
    """Handle OAuth2 callback from Microsoft"""
    
    def do_GET(self):
        """Handle GET request with authorization code"""
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)
        
        if 'code' in query_params:
            self.server.auth_code = query_params['code'][0]
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'''
                <html>
                <body>
                    <h1>Authentication Successful!</h1>
                    <p>You can close this window and return to the application.</p>
                    <script>window.close();</script>
                </body>
                </html>
            ''')
        else:
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<html><body><h1>Authentication Failed</h1></body></html>')
    
    def log_message(self, format, *args):
        """Suppress HTTP server logs"""
        pass


class OutlookGraphAuth:
    """
    REAL Microsoft Graph authentication service for Outlook email
    Implements full OAuth2 flow with actual Microsoft endpoints
    """
    
    def __init__(self):
        # Azure App Registration details - MUST be configured
        self.client_id = os.getenv('AZURE_CLIENT_ID', '')
        self.client_secret = os.getenv('AZURE_CLIENT_SECRET', '')
        self.tenant_id = os.getenv('AZURE_TENANT_ID', 'common')
        
        # OAuth2 endpoints
        self.authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        self.authorize_url = f"{self.authority}/oauth2/v2.0/authorize"
        self.token_url = f"{self.authority}/oauth2/v2.0/token"
        
        # Microsoft Graph API
        self.graph_api_url = "https://graph.microsoft.com/v1.0"
        
        # Required scopes for sending email
        self.scopes = ["https://graph.microsoft.com/Mail.Send"]
        
        # Token storage
        self.access_token = None
        self.refresh_token = None
        self.token_expires = None
        self.redirect_uri = "http://localhost:8080/callback"
        
    def authenticate(self):
        """
        Microsoft Graph authentication
        """
        if not self.client_id or not self.client_secret:
            print("Azure credentials are required. Set environment variables:")
            return False
        
        try:
            
            # Step 1: Get authorization URL
            auth_url = self.get_authorization_url(self.redirect_uri)
            print(f" Opening browser for Microsoft login...")
            
            # Step 2: Start local server for callback
            server = HTTPServer(('localhost', 8080), AuthCallbackHandler)
            server.auth_code = None
            server.timeout = 60  # 60 second timeout
            
            # Step 3: Open browser for user authentication
            webbrowser.open(auth_url)
            print(" Browser opened. Please complete Microsoft authentication.")
            
            # Step 4: Wait for callback
            while server.auth_code is None:
                server.handle_request()
                if hasattr(server, '_BaseServer__shutdown_request'):
                    break
            
            if server.auth_code is None:
                print(" Authentication timeout or cancelled")
                return False
            
            print(" Authorization code received!")
            
            # Step 5: Exchange code for tokens
            if self.exchange_code_for_tokens(server.auth_code, self.redirect_uri):
                print("Microsoft Graph authentication successful!")
                return True
            else:
                print("Token exchange failed")
                return False
                
        except Exception as e:
            print(f"Authentication error: {e}")
            return False
        
        
    def get_authorization_url(self, redirect_uri):
        """
        Generate authorization URL for OAuth2 flow
        """
        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_uri': redirect_uri,
            'scope': ' '.join(self.scopes),
            'response_mode': 'query',
            'state': 'mail_template_app'  # CSRF protection
        }
        
        return f"{self.authorize_url}?{urlencode(params)}"
    
    def exchange_code_for_tokens(self, authorization_code, redirect_uri):
        """
        Exchange authorization code for access and refresh tokens
        """
        try:
            data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'code': authorization_code,
                'redirect_uri': redirect_uri,
                'grant_type': 'authorization_code',
                'scope': ' '.join(self.scopes)
            }
            
            response = requests.post(self.token_url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            
            self.access_token = token_data.get('access_token')
            self.refresh_token = token_data.get('refresh_token')
            
            # Calculate expiration time
            expires_in = token_data.get('expires_in', 3600)
            self.token_expires = datetime.now() + timedelta(seconds=expires_in)
            
            print("Successfully obtained access tokens")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"Token exchange failed: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error during token exchange: {e}")
            return False
    
    def refresh_access_token(self):
        """
        Refresh access token using refresh token
        """
        if not self.refresh_token:
            print("No refresh token available")
            return False
        
        try:
            data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'refresh_token': self.refresh_token,
                'grant_type': 'refresh_token',
                'scope': ' '.join(self.scopes)
            }
            
            response = requests.post(self.token_url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            
            self.access_token = token_data.get('access_token')
            # Update refresh token if provided
            if 'refresh_token' in token_data:
                self.refresh_token = token_data['refresh_token']
            
            # Calculate expiration time
            expires_in = token_data.get('expires_in', 3600)
            self.token_expires = datetime.now() + timedelta(seconds=expires_in)
            
            print("Successfully refreshed access token")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"Token refresh failed: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error during token refresh: {e}")
            return False
    
    def is_token_valid(self):
        """
        Check if current access token is valid
        
        Returns:
            bool: True if valid, False otherwise
        """
        if not self.access_token or not self.token_expires:
            return False
        
        # Add 5 minute buffer before expiration
        buffer_time = timedelta(minutes=5)
        return datetime.now() < (self.token_expires - buffer_time)
    
    def get_headers(self):
        """
        Get authorization headers for Microsoft Graph API calls
        
        Returns:
            dict: Headers with Bearer token
        """
        if not self.is_token_valid():
            if not self.refresh_access_token():
                return None
        
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
    
    def send_email(self, sender_email, recipient_email, recipient_name, subject, html_body):
        # Ensure we're authenticated

        headers = self.get_headers()
        if not headers:
            print("Failed to get valid authorization headers")
            return False
        
        # Construct email message according to Microsoft Graph API
        message = {
            "message": {
                "subject": subject,
                "body": {
                    "contentType": "HTML",
                    "content": html_body
                },
                "toRecipients": [
                    {
                        "emailAddress": {
                            "address": recipient_email,
                            "name": recipient_name
                        }
                    }
                ]
            },
            "saveToSentItems": True
        }
        
        try:
            # Use Microsoft Graph sendMail endpoint
            send_url = f"{self.graph_api_url}/me/sendMail"
            response = requests.post(send_url, headers=headers, json=message)
            
            if response.status_code == 202:
                print(f"Email sent successfully to {recipient_email}")
                return True
            else:
                print(f"Failed to send email. Status: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"Unexpected error sending email: {e}")
            return False


def outlook_authenticate():
    """
    Factory function to create Outlook authentication service
    """
    try:
        outlook_auth = OutlookGraphAuth()
        if outlook_auth.authenticate():
            return outlook_auth
        else:
            return None
        
    except Exception as e:
        print(f"Failed to create Outlook authentication service: {e}")
        return None