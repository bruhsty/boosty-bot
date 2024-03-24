import abc
from email.message import EmailMessage

import aiosmtplib


class EmailService(abc.ABC):
    @abc.abstractmethod
    async def send_email(self, to: str, subject: str, body: str) -> None: ...


class SMTPEmailService(EmailService):
    def __init__(
        self,
        server_host: str,
        server_port: int,
        username: str,
        password: str,
        use_tls: bool = True,
    ) -> None:
        self.use_tls = use_tls
        self.password = password
        self.server_port = server_port
        self.server_host = server_host
        self.username = username

    async def send_email(self, to: str, subject: str, body: str) -> None:
        message = EmailMessage()
        message["From"] = self.username
        message["To"] = to
        message["Subject"] = subject
        message["Content-Type"] = "text/plain; charset=UTF-8"
        message.set_content(body)

        await aiosmtplib.send(
            message,
            hostname=self.server_host,
            port=self.server_port,
            username=self.username,
            password=self.password,
            start_tls=self.use_tls,
        )
