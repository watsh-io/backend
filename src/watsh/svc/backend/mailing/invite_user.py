import datetime
from pathlib import Path

from src.watsh.lib.smtp_client import SMTPClientManager
from src.watsh.lib.models import Project
from src.watsh.lib.token import create_token
from ..config import DOMAIN, JWT_SECRET, JWT_ALGORITHM, WATSH_LOGO_URL, WATSH_LANDING_URL

HTML_TEMPLATE_PATH = Path('src/watsh/svc/backend/mailing/html/invite_email.html')
_HTML_TEMPLATE_CONTENT = HTML_TEMPLATE_PATH.read_text()


def _replace_template_placeholders(template: str, email: str, project_slug: str, invite_link: str) -> str:
    return (template.replace('john@watsh.io', email)
                    .replace('WATSH_PROJECT', project_slug)
                    .replace('CONFIRMATION_LINK', invite_link)
                    .replace('WATSH_LOGO_URL', WATSH_LOGO_URL)
                    .replace('WATSH_LANDING_URL', WATSH_LANDING_URL))

def invite_html_body(email: str, project_slug: str, invite_link: str) -> str:
    return _replace_template_placeholders(_HTML_TEMPLATE_CONTENT, email, project_slug, invite_link)

async def send_invite_user_message(
    smtp_client: SMTPClientManager, project: Project, recipient_email_address: str, sender_email_address: str,
) -> None:
    # Send invitation email
    payload = {
        'project_id': str(project.id),
        'email': recipient_email_address,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
    }
    invite_token = create_token(payload, JWT_SECRET, JWT_ALGORITHM)

    invite_link = f'{DOMAIN}/v1/member/{project.id}/invite/accept?invite_token={invite_token}'
    subject = 'Watsh - You have been invited!'
    html_body = invite_html_body(sender_email_address, project.slug, invite_link)

    await smtp_client.send_email(
        to_email=recipient_email_address,
        subject=subject,
        html_body=html_body,
    )
