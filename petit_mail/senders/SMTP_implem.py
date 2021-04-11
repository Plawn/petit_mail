import logging
import smtplib
import threading
from dataclasses import dataclass
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Optional, Type

from .interface import EmailSender, Email


@dataclass
class SMTPCreds:
    email: str
    password: str
    server: str
    server_port: int


class SMTPMailHandler(EmailSender[SMTPCreds]):
    MAX_RETRIES = 5

    def get_creds_form(self) -> Type[SMTPCreds]:
        return SMTPCreds

    def __init__(self, creds: SMTPCreds):
        self.email = creds.email
        self.creds = creds
        self.session: Optional[smtplib.SMTP] = None
        self.lock = threading.RLock()
        self.logged: bool = False
        self.__login()

    def send_html_mail(self, email: Email) -> None:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = email.subject
        msg['From'] = f"'{email.sender}' <{self.creds.email}>"
        msg['To'] = ','.join(email.addresses)
        msg.attach(MIMEText(email.content, 'text'))
        msg.attach(MIMEText(email.content, 'html'))
        self.__send_mail(email.addresses, msg)

    def send_raw_mail(self, email: Email) -> None:
        message = MIMEText(email.content)
        message['Subject'] = email.subject
        message['From'] = f"'{email.sender}' <{self.creds.email}>"
        message['To'] = ','.join(email.addresses)
        self.__send_mail(email.addresses, message)

    def __login(self):
        # in case multiple people try to re auth the server at the same time
        with self.lock:
            if not self.logged:
                self.session = smtplib.SMTP(
                    self.creds.server, self.creds.server_port)
                self.session.ehlo()
                self.session.starttls()
                self.session.login(self.creds.email, self.creds.password)
                self.logged = True
                logging.debug(f'Successfully logged into {self.creds.email}')

    def __send_mail(self, adresses: List[str], msg: MIMEMultipart) -> None:
        done = False
        retries = 0

        while not done and retries < self.MAX_RETRIES:
            try:
                self.session.sendmail(
                    self.creds.email, adresses, msg.as_string())
                done = True
            except:
                self.logged = False
                logging.warning('trying to reconnect to the mail server')
                self.__login()
                retries += 1
        if not done:
            logging.error(f'Failed to send mail to {adresses}')

    def __repr__(self):
        return f'<SMTP {self.creds.email}>'
