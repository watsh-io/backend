import datetime
from pathlib import Path
from src.watsh.lib.token import create_token
from src.watsh.lib.smtp_client import SMTPClientManager

from ..config import (
    DOMAIN, WATSH_LOGO_URL, WATSH_LANDING_URL,
    JWT_SECRET, JWT_ALGORITHM,
)

# Cache the HTML template
_HTML_TEMPLATE_PATH = Path('src/watsh/svc/backend/mailing/html/validate_email.html')
_HTML_TEMPLATE_CONTENT = _HTML_TEMPLATE_PATH.read_text()

def _replace_template_placeholders(template: str, email: str, confirmation_link: str) -> str:
    """
    Replace placeholders in the HTML template with actual values.
    """
    return (template.replace('john@watsh.io', email)
                    .replace('CONFIRMATION_LINK', confirmation_link)
                    .replace('WATSH_LOGO_URL', WATSH_LOGO_URL)
                    .replace('WATSH_LANDING_URL', WATSH_LANDING_URL))

def registration_html_body(email: str, confirmation_link: str) -> str:
    """
    Generate the HTML body for the registration email.
    """
    return _replace_template_placeholders(_HTML_TEMPLATE_CONTENT, email, confirmation_link)

async def send_validate_address_email(email_address: str, smtp_client: SMTPClientManager) -> None:
    """
    Send a validation email to the provided email address.
    """
    # Generate token payload
    payload = {
        'email': email_address,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    registration_token = create_token(payload, JWT_SECRET, JWT_ALGORITHM)

    # Prepare email content
    confirmation_link = f'{DOMAIN}/v1/register?registration_token={registration_token}'
    subject = 'Watsh - Please confirm your email address'
    html_body = registration_html_body(email_address, confirmation_link)

    # Send the email
    await smtp_client.send_email(to_email=email_address, subject=subject, html_body=html_body)
