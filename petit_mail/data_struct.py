from typing import Dict

from .engine import EmailSender
from .engine.template_db.interface import TemplateDB



class Context():
    senders_db: Dict[str, EmailSender]
    template_db: TemplateDB
