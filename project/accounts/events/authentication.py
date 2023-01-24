from accounts.models import EmailConfirmationToken, User
from core.dependencies.providers import provide_settings
from notifications.async_tasks.email import send_email


async def user_registered_event(user: User, confirmation_token: EmailConfirmationToken):
    settings = provide_settings()
    email_data = {
        'link': f'{settings.HOST_DOMAIN}/accounts/confirm_email?user_id={user.id}?token={confirmation_token.token}',
    }
    await send_email('email_confirmation.html', 'Please confirm your email', user.email, template_body=email_data)
