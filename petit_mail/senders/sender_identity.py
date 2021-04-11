import logging
from typing import List, Dict, Type

from . import engines
from .interface import Email, EmailSender


class Identity:
    def __init__(self, senders: Dict[str, EmailSender]):
        self.senders: Dict[str, EmailSender] = senders

    def infos(self):
        return {
            k: v.infos() for k, v in self.senders.items()
        }

    def __send_mail(self, mails: List[Email], type_: str):
        """Cut batch to avoid uneccessary I/O
        """
        email_number = 10
        if type_ == "html":
            sender = self.get_sender(type_, email_number).send_html_mail
            for mail in mails:
                sender(mail)
        else:
            sender = self.get_sender(type_, email_number).send_raw_mail
            for mail in mails:
                sender(mail)

    def get_sender(self, type_:str, email_number: int):
        """Should ensure that a given account still has enough clearance to send emails

        // naive as of now
        """
        return list(self.senders.values())[0]

    def send_html_mail(self, mails: List[Email]):
        """Sends multiple html mails
        """
        self.__send_mail(mails, "html")

    def send_plain_mail(self, mails: List[Email]):
        """Sends multiple plain mails
        """
        self.__send_mail(mails, "raw")

    @staticmethod
    def load(creds: List[Dict[str, str]]):
        """Loads an identity from a given conf
        """
        senders: Dict[str, Type[EmailSender]] = {}
        for infos in creds:
            type_ = infos['type']
            del infos['type']
            try:
                name = infos['email']
                engine = engines[type_]
                senders[name] = engine(engine.get_creds_form()(**infos))
            except KeyError:
                logging.error("Invalid email type")
                raise Exception('Invalid mail type')
            except:
                raise

        return Identity(senders)
