from typing import Dict

from .senders import EmailSender
from .template_db.interface import TemplateDB



class Context():
    senders_db: Dict[str, EmailSender]
    template_db: TemplateDB
