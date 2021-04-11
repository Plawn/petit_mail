from typing import Dict

from .senders.sender_identity import Identity
from .template_db.interface import TemplateDB


class Context():
    senders_db: Dict[str, Identity]
    template_db: TemplateDB
