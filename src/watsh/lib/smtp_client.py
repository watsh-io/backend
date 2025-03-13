import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class SMTPClientManager:
    def __init__(self, hostname: str, port: int, username: str, password: str, from_email: str):
        """
        Initialize the SMTP client manager with server and user credentials.
        """
        self.hostname: str = hostname
        self.port: int = port
        self.username: str = username
        self.password: str = password
        self.from_email: str = from_email

    async def send_email(self, to_email: str, subject: str, html_body: str) -> None:
        """
        Send an HTML email. Opens and closes the SMTP connection for each message.
        """
        message: MIMEMultipart = self._prepare_message(to_email, subject, html_body)
        await self._send_with_new_connection(message)

    def _prepare_message(self, to_email: str, subject: str, html_body: str) -> MIMEMultipart:
        """
        Prepare the email message with the given parameters.
        """
        msg: MIMEMultipart = MIMEMultipart()
        msg['From'] = self.from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(html_body, 'html'))
        return msg

    async def _send_with_new_connection(self, message: MIMEMultipart) -> None:
        """
        Create a new SMTP connection and send the message.
        """
        await aiosmtplib.send(
            message,
            hostname=self.hostname,
            port=self.port,
            username=self.username,
            password=self.password,
            use_tls=True,
        )
