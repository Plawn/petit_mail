import logging
import smtplib
import threading
from dataclasses import dataclass
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Optional

from .interface import EmailSender


@dataclass
class SMTPCreds:
    email: str
    password: str
    server: str
    server_port: int


class SMTPMailHandler(EmailSender[SMTPCreds]):
    MAX_RETRIES = 5

    def get_creds_form(self) -> SMTPCreds:
        return SMTPCreds

    def __init__(self, creds: SMTPCreds):
        self.creds = creds
        self.session: Optional[smtplib.SMTP] = None
        self.lock = threading.RLock()
        self.logged: bool = False
        self.__login()

    def send_html_mail(self, _from: str, subject: str, content: str, adresses: List[str]) -> None:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"'{_from}' <{self.creds.email}>"
        msg['To'] = ','.join(adresses)
        msg.attach(MIMEText(content, 'text'))
        msg.attach(MIMEText(content, 'html'))
        self.__send_mail(adresses, msg)

    def send_raw_mail(self, _from: str, subject: str, content: str, adresses: List[str]) -> None:
        message = MIMEText(content)
        message['Subject'] = subject
        message['From'] = f"'{_from}' <{self.creds.email}>"
        message['To'] = ','.join(adresses)
        self.__send_mail(adresses, message)

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
