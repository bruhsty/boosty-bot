import datetime
from dataclasses import dataclass


@dataclass
class Event:
    time: datetime.datetime


@dataclass
class BoostyProfileAdded(Event):
    user_id: int
    profile_id: int
    profile_email: str
    profile_name: str


@dataclass
class BoostyProfileVerified(Event):
    user_id: int
    profile_id: int
    profile_email: str
    profile_name: str
