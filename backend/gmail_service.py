from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import base64
from email.mime.text import MIMEText
from token_store import save_token

def get_gmail_service(token, email=None):
    creds = Credentials.from_authorized_user_info(token)

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        # Save refreshed token if email is provided
        if email:
            updated_token = {
                "token": creds.token,
                "refresh_token": creds.refresh_token,
                "token_uri": creds.token_uri,
                "client_id": creds.client_id,
                "client_secret": creds.client_secret,
                "scopes": creds.scopes
            }
            save_token(email, updated_token)

    service = build('gmail', 'v1', credentials=creds)
    return service


def send_email(token, to_email, subject, message_text, email=None):
    service = get_gmail_service(token, email)

    message = MIMEText(message_text)
    message['to'] = to_email
    message['subject'] = subject

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

    message_body = {'raw': raw}

    service.users().messages().send(
        userId='me',
        body=message_body
    ).execute()

    return {"message": "Email sent successfully"}