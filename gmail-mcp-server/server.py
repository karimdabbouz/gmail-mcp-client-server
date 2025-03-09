from mcp.server.fastmcp import FastMCP
import os, pickle, base64
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from typing import List
from bs4 import BeautifulSoup


mcp = FastMCP('gmail-mcp-server')


class GmailMCPServer:
    def __init__(self):
        self.client_secret_file='./credentials.json'
        self.scopes=['https://www.googleapis.com/auth/gmail.readonly']
        self.creds=self.authenticate()
        self.service=build('gmail', 'v1', credentials=self.creds)


    def authenticate(self):
        '''
        Tries to load the user's credentials from a local token file. 
        If no valid credentials are found or if the credentials are expired, 
        the user is prompted to re-authenticate in the browser using credentials.json.

        Authentication via browser requires you to run this script once directly without the client.py.
        The token is then saved for future use in the root of this project as token.pickle
        '''
        creds = None
        if os.path.exists('./token.pickle'):
            with open('./token.pickle', 'rb') as token:
                creds = pickle.load(token)
        if not creds or not creds.valid:
            flow = InstalledAppFlow.from_client_secrets_file(self.client_secret_file, self.scopes)
            creds = flow.run_local_server(port=0)
            with open('./token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        return creds


def extract_mail_content(message):
    '''
    Helper function to extract email content from messages.
    '''
    full_content = ''
    payload = message.get('payload', {})
    single_body = payload.get('body', None)
    if single_body:
        data = single_body.get('data')
        if data:
            if payload['mimeType'] == 'text/plain':
                full_content = base64.urlsafe_b64decode(data).decode('utf-8')
            elif payload['mimeType'] == 'text/html':
                html_content = base64.urlsafe_b64decode(data).decode('utf-8')
                full_content = BeautifulSoup(html_content, 'html.parser').get_text()
    if not full_content:
        plain_text = ''
        html_content = ''
        for part in payload.get('parts', []):
            part_data = part.get('body', {}).get('data')
            if part_data:
                if part['mimeType'] == 'text/plain':
                    plain_text = base64.urlsafe_b64decode(part_data).decode('utf-8')
                elif part['mimeType'] == 'text/html':
                    html_content = base64.urlsafe_b64decode(part_data).decode('utf-8')
        if plain_text:
            full_content = plain_text
        elif html_content:
            full_content = BeautifulSoup(html_content, 'html.parser').get_text()
    return full_content
    

@mcp.tool()
async def list_messages(q: str, max_results: int) -> str:
    '''
    Lists the message IDs from the user's inbox specified by the query.

    Args:
        q: Query in the same format as in the Gmail search box
        max_results: The maximum number of message IDs to return
    '''
    results = gmail_mcp_server.service.users().messages().list(userId='me', maxResults=max_results, q=q).execute()
    return '\n'.join([x['id'] for x in results['messages']])


@mcp.tool()
async def get_messages_for_ids(ids: List[str]) -> str:
    '''
    Gets the content of one or more messages specified by their message ID.

    Args:
        ids: The list with one or more IDs for which to retrieve the message content
    '''
    content = ''
    for id in ids:
        message = gmail_mcp_server.service.users().messages().get(userId='me', id=id).execute()
        content += extract_mail_content(message)
    return content


if __name__ == '__main__':
    gmail_mcp_server = GmailMCPServer()
    # for msg_id in ['19566b406fc769b2', '19562445ce749209']:
    #     message = gmail_mcp_server.service.users().messages().get(userId='me', id=msg_id).execute()
    #     body = extract_mail_content(message)
    #     print('##################################################################')
    #     print(body)
    mcp.run(transport='stdio')





