import logging
from petit_mail.senders.persistor import Persistor
from typing import List, Dict, Type

from . import engines
from .interface import Email, EmailSender


class Identity:
    def __init__(self, senders: Dict[str, EmailSender]):
        self.senders: Dict[str, EmailSender] = senders
        self.persistor = Persistor()

    def infos(self):
        return {
            k: v.infos() for k, v in self.senders.items()
        }

    def __send_mail(self, mails: List[Email], type_: str):
        """Cut batch to avoid uneccessary I/O
        """
        senders = self.get_senders(len(mails))
        send = None
        for nb, sender in senders:
            while nb > 0:
                if type_ == "html":
                    send = sender.send_html_mail
                else:
                    send = sender.send_raw_mail
                for mail in mails:
                    try:
                        send(mail)
                        self.persistor.confirm_success(sender, mail)
                        logging.info('send succeded')
                        # note that send succeeded
                    except:
                        logging.error('send failed')
                        # note that send failed
                        self.persistor.confirm_fail(sender, mail)
                    finally:
                        nb -= 1
        

        

    def get_senders(self, email_number: int):
        """Should ensure that a given account still has enough clearance to send emails

        // naive as of now
        """

        # get sender with enough clearance
        sender = list(self.senders.values())[0]
        # lock quota in db
        self.persistor.lock_quota(sender, email_number)
        # should be multiple if quota can't be fullfilled
        return [(email_number, sender)]

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
        senders: Dict[str, EmailSender] = {}
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
