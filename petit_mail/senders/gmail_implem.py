
import base64
from dataclasses import dataclass
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Type

import google.oauth2.credentials as Creds
from googleapiclient.discovery import build

from .interface import EmailSender, Email


@dataclass
class GmailCreds:
    client_id: str
    client_secret: str
    refresh_token: str
    email: str


TOKEN_URI = 'https://oauth2.googleapis.com/token'

scopes = ['https://www.googleapis.com/auth/gmail.send']


class GmailEmailSender(EmailSender[GmailCreds]):
    @staticmethod
    def get_creds_form() -> Type[GmailCreds]:
        return GmailCreds

    def __init__(self, gmailCreds: GmailCreds):
        self.__creds = creds = Creds.Credentials(
            token=None,
            refresh_token=gmailCreds.refresh_token,
            id_token=None,
            token_uri=TOKEN_URI,
            client_id=gmailCreds.client_id,
            client_secret=gmailCreds.client_secret,
            scopes=scopes, quota_project_id=None
        )
        self.sender = build('gmail', 'v1', credentials=creds)
        self.email = gmailCreds.email

    def send_html_mail(self, email: Email) -> None:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = email.subject
        msg['From'] = f"'{email.sender}' <{self.email}>"
        msg['To'] = ','.join(email.addresses)
        msg.attach(MIMEText(email.content, 'html'))
        self.__send_mail(msg)

    def send_raw_mail(self, email: Email) -> None:
        message = MIMEText(email.content)
        message['Subject'] = email.subject
        message['From'] = f"'{email.sender}' <{self.email}>"
        message['To'] = ','.join(email.addresses)
        self.__send_mail(message)

    def __send_mail(self, message: str) -> None:
        (self.sender
         .users()
         .messages()
         .send(
             userId='me',
             body={
                 'raw': base64.urlsafe_b64encode(
                    message.as_bytes()).decode("utf-8")
             }
         ).execute())
