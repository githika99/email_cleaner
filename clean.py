# gmail_cleaner.py

import os.path
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these SCOPES, delete the token.json file.
#SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
SCOPES = ['https://mail.google.com/']

def authenticate_gmail():
    """Authenticate and return the Gmail service."""
    creds = None
    # token.json stores user access and refresh tokens
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials, let user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=8080)
        # Save credentials for next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def get_unread_emails_older_than_1_month(service):
    """Returns list of message IDs that are unread and older than 1 month."""
    # Get date 30 days ago
    one_month_ago = (datetime.datetime.utcnow() - datetime.timedelta(days=30)).strftime("%Y/%m/%d")
    query = f'is:unread before:{one_month_ago}'
    
    results = service.users().messages().list(userId='me', q=query).execute()
    messages = results.get('messages', [])
    
    if not messages:
        print('No unread emails older than 1 month.')
        return []
    
    print(f'Found {len(messages)} unread emails older than 1 month.')
    return [msg['id'] for msg in messages]

def delete_messages(service, message_ids):
    """Batch deletes the messages with the given IDs."""
    if not message_ids:
        return
    service.users().messages().batchDelete(userId='me', body={'ids': message_ids}).execute()
    print(f'Deleted {len(message_ids)} emails.')

def main():
    service = authenticate_gmail()
    message_ids = get_unread_emails_older_than_1_month(service)
    delete_messages(service, message_ids)

if __name__ == '__main__':
    main()


