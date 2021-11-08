from typing import Sequence, Union

from fastapi_mail import MessageSchema, FastMail
from starlette.background import BackgroundTasks

from core.config import settings


def send_email(background_tasks: BackgroundTasks,
               template_name: str,
               subject: str,
               email_to: Union[str, Sequence],
               template_body: dict):
    """
    Background task for sending emails.
    """

    message = MessageSchema(subject=subject,
                            recipients=[email_to] if isinstance(email_to, str) else email_to,
                            template_body=template_body,
                            subtype='html')
    fast_mail = FastMail(settings.MAIL_CONFIG)
    background_tasks.add_task(fast_mail.send_message, message, template_name=template_name)
