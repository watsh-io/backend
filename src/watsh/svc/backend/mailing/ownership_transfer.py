import datetime
from pathlib import Path

from src.watsh.lib.smtp_client import SMTPClientManager
from src.watsh.lib.models import Project
from src.watsh.lib.token import create_token
from ..config import DOMAIN, JWT_SECRET, JWT_ALGORITHM, WATSH_LOGO_URL, WATSH_LANDING_URL

HTML_TEMPLATE_PATH = Path('src/watsh/svc/backend/mailing/html/ownership_transfer_email.html')
HTML_TEMPLATE_CONTENT = HTML_TEMPLATE_PATH.read_text()


def replace_template_placeholders(template: str, email_address: str, project_slug: str, invite_link: str) -> str:
    """
    Replace placeholders in the HTML template with actual values.
    """
    return (template.replace('john@watsh.io', email_address)
                    .replace('WATSH_PROJECT', project_slug)
                    .replace('CONFIRMATION_LINK', invite_link)
                    .replace('WATSH_LOGO_URL', WATSH_LOGO_URL)
                    .replace('WATSH_LANDING_URL', WATSH_LANDING_URL))


def ownership_transfer_html_body(email_address: str, project_slug: str, invite_link: str) -> str:
    """
    Generate the HTML body for the ownership transfer email.
    """
    return replace_template_placeholders(HTML_TEMPLATE_CONTENT, email_address, project_slug, invite_link)


async def send_ownership_transfer(smtp_client: SMTPClientManager, project: Project, recipient_email_address: str, sender_email_address: str) -> None:
    """
    Send a validation email to the provided email address.
    """
    # Generate token payload
    expiration_time = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    payload = {'project_id': str(project.id), 'email': recipient_email_address, 'exp': expiration_time}
    
    # Note: Add a brief comment here to explain the purpose of the following line
    transfer_ownership_token = create_token(payload, JWT_SECRET, JWT_ALGORITHM)

    # Send invitation email
    invite_link = f'{DOMAIN}/v1/ownership/{project.id}/accept?transfer_ownership_token={transfer_ownership_token}'
    subject = 'Watsh - You have been granted a new project!'
    html_body = ownership_transfer_html_body(sender_email_address, project.slug, invite_link)

    await smtp_client.send_email(to_email=recipient_email_address, subject=subject, html_body=html_body)
