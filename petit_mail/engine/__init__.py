from typing import Dict, Type

from .gmail_implem import GmailEmailSender
from .interface import EmailSender
from .SMTP_implem import SMTPMailHandler
from .template_db import (LocalTemplateDB, MinioInfos, MinioTemplateDB,
                          TemplateDB)

engines: Dict[str, Type[EmailSender]] = {
    'gmail': GmailEmailSender,
    'smtp': SMTPMailHandler,
}

def add_engine(name:str, engine: Type[EmailSender]) -> None:
    engines[name] = engine