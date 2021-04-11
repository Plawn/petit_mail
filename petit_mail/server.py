from typing import Any, Callable, Dict, List, Literal, Optional

from fastapi import FastAPI
from pydantic import BaseModel
from starlette.responses import JSONResponse, Response

from .data_struct import Context
from .senders.interface import Email


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


def make_template_filename(template_name: str):
    return template_name + '.html'


def make_server(app: FastAPI, on_init: Callable[[Context], None], context: Context) -> FastAPI:
    """
    Returns a `FastAPI` prepated instance which can then be used with any ASGI server
    """
    template_db = context.template_db
    senders_db = context.senders_db

    app.on_event('startup')(lambda: on_init(context))

    @app.get('/list')
    def list_templates():
        return list(template_db.templates.keys())

    @app.get('/reload')
    def _reload():
        template_db.init()
        return {"error": False}

    @app.post('/send_mail/{sender_name}/plain')
    def send_mail_plain(sender_name: str, body: SendMailBody):
        # getting the requested sender
        sender = senders_db[sender_name]

        addresses = body.addresses
        content = body.content
        subject = body.subject
        _from = body.from_

        try:
            sender.send_plain_mail(
                [Email(_from, subject, content, addresses)]
            )
            return Response(status_code=200)
        except:
            return Response(status_code=500)

    @app.post('/send_mail/{sender_name}/html')
    def send_mail_templated(sender_name: str, body: SendMailBody, send: int = 1):
        # getting the requested sender
        sender = senders_db[sender_name]

        addresses = body.addresses
        content = body.content
        subject = body.subject
        _from = body.from_

        if body.template_name is not None:
            template_name = make_template_filename(body.template_name)
            if template_name in template_db.templates:
                subject, content = template_db.render(
                    template_name, body.data)
            else:
                # TODO: should be more consistent
                return JSONResponse({'error': 'template not found'}, 404)

        if send:
            sender.send_html_mail(
                [Email(_from, subject, content, addresses)]
            )
            return Response(status_code=200)
        else:
            return Response(content, 200)

    @app.get('/live')
    def live():
        return Response('OK', 200)

    @app.get('/identities')
    def identities():
        return {
            k: v.infos() for k, v in senders_db.items()
        }

    return app
