import os.path
 import datetime
 from google.auth.transport.requests import Request
 from google.oauth2.credentials import Credentials
 from google_auth_oauthlib.flow import InstalledAppFlow
 from googleapiclient.discovery import build
 from datetime import datetime, timedelta, timezone
 
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
     # Get date 30 days ago (timezone aware)
     one_month_ago = (datetime.now(timezone.utc) - timedelta(days=30)).strftime("%Y/%m/%d")
     query = f'is:unread before:{one_month_ago}'
 
     all_messages = []
     next_page_token = None
 
     while True:
         response = service.users().messages().list(
             userId='me',
             q=query,
             maxResults=500,  # max allowed by Gmail API
             pageToken=next_page_token
         ).execute()
 
         messages = response.get('messages', [])
         all_messages.extend([msg['id'] for msg in messages])
 
         next_page_token = response.get('nextPageToken')
         if not next_page_token:
             break
 
     if not all_messages:
         print('No unread emails older than 1 month.')
         return []
 
     print(f'Found {len(all_messages)} unread emails older than 1 month.')
     return all_messages
 
 def delete_messages(service, message_ids):
     """Deletes messages in batches of 1000 (Gmail API limit)."""
     BATCH_SIZE = 1000
     total = len(message_ids)
 
     print(f'Deleting {total} messages in batches of {BATCH_SIZE}...')
 
     for i in range(0, total, BATCH_SIZE):
         batch = message_ids[i:i + BATCH_SIZE]
         service.users().messages().batchDelete(
             userId='me',
             body={'ids': batch}
         ).execute()
         print(f'Deleted batch {i//BATCH_SIZE + 1}: {len(batch)} messages')
 
     print('All messages deleted.')
 
 def main():
     service = authenticate_gmail()
     message_ids = get_unread_emails_older_than_1_month(service)
     delete_messages(service, message_ids)
 
 if __name__ == '__main__':
     main()
 
 
 
 # if you want to change the user, run 'rm token.json' you will be prompted to log in again
