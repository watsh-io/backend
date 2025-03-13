import datetime
from pathlib import Path
from src.watsh.lib.models import User
from src.watsh.lib.token import create_token
from src.watsh.lib.smtp_client import SMTPClientManager

from ..config import DOMAIN, WATSH_LOGO_URL, WATSH_LANDING_URL, JWT_SECRET, JWT_ALGORITHM, WATSH_APP


# Cache the HTML template
_HTML_TEMPLATE_PATH = Path('src/watsh/svc/backend/mailing/html/login_email.html')
_HTML_TEMPLATE_CONTENT = _HTML_TEMPLATE_PATH.read_text()

def _replace_template_placeholders(template: str, login_link: str) -> str:
    """
    Replace placeholders in the HTML template with actual values.
    """
    return template.replace('LOGIN_LINK', login_link)\
                   .replace('WATSH_LOGO_URL', WATSH_LOGO_URL)\
                   .replace('WATSH_LANDING_URL', WATSH_LANDING_URL)

def login_html_body(login_link: str) -> str:
    """
    Generate the HTML body for the login email.
    """
    return _replace_template_placeholders(_HTML_TEMPLATE_CONTENT, login_link)

async def send_login_email(user: User, smtp_client: SMTPClientManager) -> None:
    """
    Send a login email to the user with a login token link.
    """
    # # Generate token payload
    # payload = {
    #     'user_id': str(user.id),
    #     'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
    # }
    # login_token = create_token(payload, JWT_SECRET, JWT_ALGORITHM)

    # # Prepare email content
    # login_link = f'{DOMAIN}/v1/token?login_token={login_token}'
    # subject = 'Watsh - Complete Your Login'
    # html_body = login_html_body(login_link)

    # # Send the email
    # await smtp_client.send_email(to_email=user.email, subject=subject, html_body=html_body)


    # Redirect to dashboard with a token
    expiration_time = datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    payload = {'user_id': str(user.id), 'exp': expiration_time}
    access_token = create_token(payload, JWT_SECRET, JWT_ALGORITHM)
    redirect_url = f"{WATSH_APP}?access_token={access_token}&host={DOMAIN}"
    
    # Send the email
    subject = 'Watsh - Complete Your Login'
    html_body = login_html_body(redirect_url)
    await smtp_client.send_email(to_email=user.email, subject=subject, html_body=html_body)
