from src.watsh.lib.smtp_client import SMTPClientManager

from .config import SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, SMTP_FROM_EMAIL

client = SMTPClientManager(
    hostname=SMTP_HOST,
    port=SMTP_PORT,
    username=SMTP_USERNAME,
    password=SMTP_PASSWORD,
    from_email=SMTP_FROM_EMAIL,
)

async def get_smtp_client() -> SMTPClientManager:
    global client
    return client