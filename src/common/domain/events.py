from dataclasses import dataclass
from datetime import datetime


@dataclass
class DomainEvent:
    time: datetime
