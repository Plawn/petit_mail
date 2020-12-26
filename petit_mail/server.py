from petit_mail.data_struct import Context
from typing import Any, Callable, Dict, List, Literal, Optional

from fastapi import FastAPI
from pydantic import BaseModel
from starlette.responses import JSONResponse, Response


class SendMailBody(BaseModel):
    addresses: List[str]
    content: str = ''
    subject: str = ''
    from_: str
    template_name: Optional[str]
    class Config:
        fields = {
            'from_': 'from'
        }

    data: Dict[str, Any] = {}


def make_server(on_init: Callable[[Context], None], context: Context) -> FastAPI:
    """
    Returns a `FastAPI` prepated instance which can then be used with any ASGI server
    """
    template_db = context.template_db
    senders_db = context.senders_db
    app = FastAPI(
        on_startup=[
            lambda:on_init(context),
        ]
    )

    def make_template_filename(template_name: str):
        return template_name + '.html'

    @app.get('/list')
    def list_templates():
        return list(template_db.templates.keys())

    @app.get('/reload')
    def _reload():
        template_db.init()
        return {"error": False}

    @app.post('/send_mail/{sender_name}/{_type}')
    def send_mail(sender_name: str, _type: Literal['plain', 'html'], body: SendMailBody, send: int = 1):
        # getting the requested sender
        sender = senders_db[sender_name]

        addresses = body.addresses
        content = body.content
        subject = body.subject
        _from = body.from_

        if _type == "html":
            if body.template_name is not None:
                template_name = make_template_filename(body.template_name)
                if template_name in template_db.templates:
                    subject, content = template_db.render(
                        template_name, body.data)
                else:
                    # TODO: should be more consistent
                    return JSONResponse({'error': 'template not found'}, 404)

            if send:
                sender.send_html_mail(_from, subject, content, addresses)
                return Response(status_code=200)
            else:
                return Response(content, 200)

        elif _type == "plain":
            sender.send_raw_mail(_from, subject, content, addresses)
            return Response(status_code=200)
        else:
            return Response(f'{_type} not found', 404)

    @app.get('/live')
    def live():
        return Response('OK', 200)

    return app
