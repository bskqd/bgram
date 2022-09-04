from typing import Sequence, Union

from fastapi_mail import MessageSchema, FastMail

from core.config import settings


async def send_email(template_name: str, subject: str, email_to: Union[str, Sequence], template_body: dict):
    message = MessageSchema(
        subject=subject,
        recipients=[email_to] if isinstance(email_to, str) else email_to,
        template_body=template_body,
        subtype='html',
    )
    fast_mail = FastMail(settings.MAIL_CONFIG)
    await fast_mail.send_message(message, template_name=template_name)
