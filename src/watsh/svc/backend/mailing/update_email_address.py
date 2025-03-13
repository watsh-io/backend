import datetime
from pathlib import Path
from src.watsh.lib.models import User
from src.watsh.lib.token import create_token
from src.watsh.lib.smtp_client import SMTPClientManager

from ..config import (
    DOMAIN, WATSH_LOGO_URL, WATSH_LANDING_URL,
    JWT_SECRET, JWT_ALGORITHM,
)

# Cache the HTML template
_HTML_TEMPLATE_PATH = Path('src/watsh/svc/backend/mailing/html/new_email.html')
_HTML_TEMPLATE_CONTENT = _HTML_TEMPLATE_PATH.read_text()

def _replace_template_placeholders(template: str, url: str) -> str:
    """
    Replace placeholders in the HTML template with actual values.
    """
    return template.replace('CONFIRMATION_LINK', url)\
                   .replace('WATSH_LOGO_URL', WATSH_LOGO_URL)\
                   .replace('WATSH_LANDING_URL', WATSH_LANDING_URL)

def email_update_html_body(url: str) -> str:
    """
    Generate the HTML body for the email update message.
    """
    return _replace_template_placeholders(_HTML_TEMPLATE_CONTENT, url)

async def send_update_address_email(
    current_user: User, email_address: str, smtp_client: SMTPClientManager
) -> None:
    """
    Send an email to the user with a link to confirm their new email address.
    """
    # Generate token payload
    payload = {
        'user_id': str(current_user.id),
        'email': email_address,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    verification_token = create_token(payload, JWT_SECRET, JWT_ALGORITHM)

    # Prepare email content
    login_link = f'{DOMAIN}/v1/me/email/accept?verification_token={verification_token}'
    subject = 'Watsh - Confirm Your New Email Address'
    html_body = email_update_html_body(login_link)

    # Send the email
    await smtp_client.send_email(to_email=email_address, subject=subject, html_body=html_body)
