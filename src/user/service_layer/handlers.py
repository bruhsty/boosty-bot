from common.adapters.email import EmailService
from dependency_injector.wiring import Provide, inject

from ..domain.events import VerificationCodeIssued


@inject
async def send_verification_code(
    event: VerificationCodeIssued, email_service: EmailService = Provide["email_service"]
) -> None:
    await email_service.send_email(
        event.email,
        "Here is a verification code you requested",
        f"Your verification code is: {event.code}",
    )
