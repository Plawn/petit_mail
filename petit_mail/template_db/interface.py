from abc import ABC, abstractmethod, abstractstaticmethod
import logging
from typing import Any, Callable, Dict, Generic, List, Optional, Tuple, TypeVar, final

import premailer
from jinja2 import Environment, FunctionLoader, select_autoescape

from ..render_functions import RenderFunctions
from .utils import find_between, get_placeholder


class TemplateData:
    def __init__(self, text: str, is_common: bool, fields: List[str]):
        self.subject = find_between(text, '<subject>', '</subject>')[0]
        self.body = find_between(
            text, '<mail_content>', '</mail_content>'
        )[0] if not is_common else text
        self.fields = fields


T = TypeVar('T')


class TemplateDB(ABC, Generic[T]):
    def __init__(self, infos: Any,  logger: Optional[logging.Logger] = None):
        self.templates: Dict[str, TemplateData] = {}
        self.logger = logger or logging.getLogger()
        self.env = Environment(
            loader=FunctionLoader(self.__get_template),
            autoescape=select_autoescape(['html', 'xml'])
        )
        self.env.auto_reload = True
        self.render_functions: Dict[str, Callable[..., str]] = None

    @abstractmethod
    def init(self):
        ...

    @abstractstaticmethod
    def get_creds_form() -> T:
        ...

    @final
    def bind_render_functions(self, render_functions: RenderFunctions):
        self.render_functions = render_functions.get_functions()
        self.env.globals.update(self.render_functions)

    @final
    def __get_template(self, name: str) -> str:
        if name[-9:] == '_subject!':
            return self.templates[name[:-9]].subject
        else:
            return self.templates[name].body

    @final
    def add_template_from_text(self, template_name: str, text: str, is_common=False):
        self.templates[template_name] = TemplateData(
            text, is_common, get_placeholder(
                text, list(self.render_functions.keys()))
        )

    @final
    def render(self, name: str, data: dict) -> Tuple[str, str]:
        """Returns the subject and the body rendered
        """
        subject = self.env.get_template(name+'_subject!').render(data)
        res = '<html>' + self.env.get_template(name).render(data) + '</html>'
        body = premailer.transform(res)
        return subject, body

    def get_placeholders(self, template_name: str) -> List[str]:
        return self.templates[template_name].fields
