from typing import Sequence, Union

from core.config import SettingsABC
from core.dependencies.providers import provide_settings
from fastapi_mail import FastMail, MessageSchema


async def send_email(
    template_name: str,
    subject: str,
    email_to: Union[str, Sequence],
    template_body: dict,
    settings: SettingsABC = provide_settings(),
):
    message = MessageSchema(
        subject=subject,
        recipients=[email_to] if isinstance(email_to, str) else email_to,
        template_body=template_body,
        subtype='html',
    )
    fast_mail = FastMail(settings.MAIL_CONFIG)
    await fast_mail.send_message(message, template_name=template_name)
