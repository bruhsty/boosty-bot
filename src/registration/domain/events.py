from dataclasses import dataclass

from common.domain import DomainEvent


@dataclass
class BoostyProfileAdded(DomainEvent):
    user_id: int
    profile_id: int
    profile_email: str
    profile_name: str


@dataclass
class BoostyProfileVerified(DomainEvent):
    user_id: int
    profile_id: int
    profile_email: str
    profile_name: str
