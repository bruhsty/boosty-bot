from datetime import datetime
from typing import ClassVar, Literal, Sequence

from pydantic import BaseModel, Field
from registration.domain.models import BoostyProfile, SubscriptionLevel


class SubscriptionDataItem(BaseModel):
    type: ClassVar[Literal["image", "text"]] = Field(alias="type")


class ImageItem(SubscriptionDataItem):
    url: str = Field(alias="url")
    id: str = Field(alias="id")
    rendition: str = Field(alias="rendition")
    width: int = Field(alias="width")
    height: int = Field(alias="height")


class TextItem(SubscriptionDataItem):
    content: str = Field(alias="modificator")
    modificator: str = Field(alias="modificator")


class SubscriptionLevelItem(BaseModel):
    owner_id: int = Field(alias="ownerId")
    id: int = Field(alias="id")
    is_archived: bool = Field(alias="isArchived")
    currency_prices: dict[str, float] = Field(alias="currencyPrices")
    name: str = Field(alias="name")
    price: int = Field(alias="price")
    created_at: datetime = Field(alias="createdAt")
    data: list[ImageItem | TextItem] = Field(alias="data")

    def to_model(self) -> SubscriptionLevel:
        return SubscriptionLevel(
            id=self.id,
            name=self.name,
            is_archived=self.is_archived,
            price=self.price,
        )


class SubscribersListItem(BaseModel):
    has_avatar: bool = Field(alias="hasAvatar")
    price: int = Field(alias="price")
    avatar_url: str = Field(alias="avatarUrl")
    payments: int = Field(alias="payments")
    can_write: bool = Field(alias="canWrite")
    next_pay_time: datetime = Field(alias="nextPayTime")
    email: str = Field(alias="email")
    is_black_listed: bool = Field(alias="isBlackListed")
    name: str = Field(alias="name")
    on_time: datetime = Field(alias="onTime")
    id: int = Field(alias="id")
    subscribed: bool = Field(alias="subscribed")
    level: SubscriptionLevelItem = Field(alias="level")


class GetSubscribersListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    data: list[SubscribersListItem]

    def to_model(self) -> Sequence[BoostyProfile]:
        subscribers = []
        for subscriber_data in self.data:
            subscribers.append(
                BoostyProfile(
                    id=subscriber_data.id,
                    name=subscriber_data.name,
                    email=subscriber_data.email,
                    next_pay_time=subscriber_data.next_pay_time,
                    level=subscriber_data.level.to_model(),
                    verification_codes=[],
                    banned=subscriber_data.is_black_listed,
                )
            )
        return subscribers
