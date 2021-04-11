from dataclasses import dataclass
from abc import ABC, abstractclassmethod, abstractmethod
from typing import Generic, List, Type, TypeVar

T = TypeVar('T')
U = TypeVar('U')


@dataclass
class Email:
    sender: str
    subject: str
    content: str
    addresses: List[str]


class EmailSender(Generic[T], ABC):
    email: str
    @abstractclassmethod
    def get_creds_form(self) -> Type[T]:
        ...

    @abstractmethod
    def __init__(self, creds: T):
        ...

    @abstractmethod
    def send_html_mail(self, email: Email) -> None:
        ...

    @abstractmethod
    def send_raw_mail(self, email: Email) -> None:
        ...

    def infos(self):
        return {
            'email': self.email,
        }
