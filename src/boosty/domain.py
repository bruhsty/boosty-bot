from datetime import datetime

from common.domain import Aggregate


class SubscriptionLevel(Aggregate[int]):
    def __init__(
        self,
        level_id: int,
        name: str,
        description: str,
        price: int,
    ) -> None:
        super().__init__(level_id)
        self.name = name
        self.description = description
        self.price = price


class Subscriber(Aggregate[int]):
    def __init__(
        self,
        subscriber_id: int,
        email: str,
        next_pay_time: datetime,
        is_subscribed: bool,
        level_id: int,
    ) -> None:
        super().__init__(subscriber_id)
        self.subscriber_id = subscriber_id
        self.email = email
        self.next_pay_time = next_pay_time
        self.is_subscribed = is_subscribed
        self.level_id = level_id
