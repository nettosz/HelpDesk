import os
import base64
import json
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Define the scopes that allow you to read Gmail messages
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate_gmail():
    """Authenticate and get Gmail API service."""
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # If no valid credentials, authenticate using credentials.json
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES, redirect_uri='http://localhost:8080/')
            creds = flow.run_local_server(port=8080)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    # Build the Gmail API service
    service = build('gmail', 'v1', credentials=creds)
    return service

def get_messages_by_subject(subject_query):
    """Retrieve Gmail messages based on subject query."""
    service = authenticate_gmail()

    # Use Gmail API to search messages by subject
    query = f'subject:{subject_query}'
    
    try:
        # Get the messages from the inbox based on the query
        results = service.users().messages().list(userId='me', q=query).execute()
        messages = results.get('messages', [])

        if not messages:
            print('No messages found.')
            return []

        message_data = []
        for message in messages:
            # Get the message details
            msg = service.users().messages().get(userId='me', id=message['id']).execute()

            # Decode message snippet
            snippet = msg['snippet']
            
            headers = msg['payload']['headers']
            subject = next((header['value'] for header in headers if header['name'] == 'Subject'), None)
            from_ = next((header['value'] for header in headers if header['name'] == 'From'), None)
            date = next((header['value'] for header in headers if header['name'] == 'Date'), None)

            message_data.append({
                'subject': subject,
                'from': from_,
                'date': date,
                'snippet': snippet,
            })

        return message_data

    except Exception as error:
        print(f'An error occurred: {error}')
        return []

# Example usage
subject_to_search = 'TI AMCEL - Ticket de Suporte 5'
messages = get_messages_by_subject(subject_to_search)

if messages:
    for i, message in enumerate(messages, 1):
        print(f"\nMessage {i}:")
        print(f"Subject: {message['subject']}")
        print(f"From: {message['from']}")
        print(f"Date: {message['date']}")
        print(f"Snippet: {message['snippet']}")
else:
    print("No messages found with the specified subject.")
