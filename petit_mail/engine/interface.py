from abc import ABC, abstractclassmethod, abstractmethod
from typing import Generic, List, TypeVar

T = TypeVar('T')
U = TypeVar('U')


class EmailSender(Generic[T], ABC):
    @abstractclassmethod
    def get_creds_form(self) -> T:
        ...

    @abstractmethod
    def __init__(self, creds: T):
        ...

    @abstractmethod
    def send_html_mail(self, _from: str, subject: str, content: str, adresses: List[str]) -> None:
        ...

    @abstractmethod
    def send_raw_mail(self, _from: str, subject: str, content: str, adresses: List[str]) -> None:
        ...
