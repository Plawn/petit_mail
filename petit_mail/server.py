import logging
from typing import Any, Callable, Dict, List, Literal, Optional, Union

from fastapi import FastAPI
from pydantic import BaseModel
from starlette.responses import JSONResponse, Response

from .data_struct import Context
from .dto import SendPlainMailBody, SendTemplateMailBody
from .senders.interface import Email
from .utils import make_template_filename


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
    def send_mail_plain(sender_name: str, body: SendPlainMailBody):
        # getting the requested sender
        sender = senders_db[sender_name]

        addresses1 = body.addresses
        content = body.content
        subject = body.subject
        _from = body.from_

        try:
            sender.send_plain_mail(
                [Email(_from, subject, content, addresses)
                 for addresses in addresses1]
            )
            return Response(status_code=200)
        except Exception as e:
            logging.error(e)
            return Response(status_code=500)

    @app.post('/send_mail/{sender_name}/html')
    def send_mail_templated(sender_name: str, body: SendTemplateMailBody, send: int = 1):
        # getting the requested sender
        sender = senders_db[sender_name]

        addresses1 = body.addresses
        _from = body.from_
        content = None
        subject = None

        if body.template_name is not None:
            template_name = make_template_filename(body.template_name)
            if template_name in template_db.templates:
                subject, content = template_db.render(
                    template_name, body.data
                )
            else:
                # TODO: should be more consistent
                return JSONResponse({'error': 'template not found'}, 404)
        # async ?
        # log result in db ?
        if send:
            sender.send_html_mail(
                [Email(_from, subject, content, addresses)
                 for addresses in addresses1]
            )
            return Response(status_code=200)
        else:
            return Response(content, status_code=200)

    @app.get('/live')
    def live():
        return Response('OK', 200)

    @app.get('/identities')
    def identities():
        return {
            k: v.infos() for k, v in senders_db.items()
        }

    @app.get('/fields')
    def get_fields(template_name: str):
        return template_db.get_placeholders(template_name)

    return app
