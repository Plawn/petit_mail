

from .interface import Email, EmailSender


class Persistor:
    def __init__(self):
        self.con = None

    def lock_quota(self, sender: EmailSender, quota: int):
        pass

    def confirm_success(self, sender: EmailSender, mail: Email):
        pass

    def confirm_fail(self, sender: EmailSender, mail: Email):
        pass
