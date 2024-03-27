import uuid
from dataclasses import dataclass
from datetime import datetime

from common.domain import DomainEvent


@dataclass
class VerificationCodeIssued(DomainEvent):
    user_id: int
    email: str
    code_id: uuid.UUID
    code: str
    code_valid_until: datetime


@dataclass
class EmailVerified(DomainEvent):
    user_id: int
    email: str
    code_id: uuid.UUID
