import uuid
from datetime import datetime
from typing import cast

from registration.domain.events import BoostyProfileAdded, BoostyProfileVerified
from registration.domain.models import BoostyProfile, SubscriptionLevel, User, VerificationCode


def make_user() -> User:
    return User.new(telegram_id=123)


def make_profile_with_codes(codes: list[VerificationCode]) -> BoostyProfile:
    return BoostyProfile(
        id=123,
        name="John Doe",
        email="johndoe@example.com",
        next_pay_time=datetime(2077, 1, 1),
        verification_codes=codes,
        banned=False,
        level=SubscriptionLevel(456, "Level 1", 200, False),
    )


def make_verified_profile() -> BoostyProfile:
    return make_profile_with_codes(
        [
            VerificationCode(
                id=uuid.uuid4(),
                value="123-456",
                valid_until=datetime(2077, 1, 1),
                used_at=None,
                replaced_with=None,
                created_at=datetime(1998, 1, 1),
            )
        ]
    )


def test_boosty_profile_is_not_verified_if_no_codes_issued():
    profile = make_profile_with_codes([])
    assert profile.is_verified is False


def test_boosty_profile_is_not_verified_if_code_is_not_used():
    code = VerificationCode(
        id=uuid.uuid4(),
        value="123-456",
        valid_until=datetime(2077, 1, 1),
        used_at=None,
        replaced_with=None,
        created_at=datetime(2024, 1, 1),
    )

    profile = make_profile_with_codes([code])

    assert profile.is_verified is False


def test_boosty_profile_if_code_used():
    code = VerificationCode(
        id=uuid.uuid4(),
        value="123-456",
        valid_until=datetime(2077, 1, 1),
        used_at=datetime(2024, 1, 2),
        replaced_with=None,
        created_at=datetime(2024, 1, 1),
    )
    profile = make_profile_with_codes([code])

    assert profile.is_verified is True


def test_boosty_profile_cannot_be_verified_if_code_were_not_issued():
    profile = make_profile_with_codes([])
    user = User(telegram_id=123, profiles=[profile])
    user.verify_profile(profile, "123-456")

    assert profile.is_verified is False
    assert user.pop_event() is None


def test_boosty_profile_cannot_be_verified_if_code_expired():
    code = VerificationCode(
        id=uuid.uuid4(),
        value="123-456",
        valid_until=datetime(1999, 1, 1),
        used_at=None,
        replaced_with=None,
        created_at=datetime(1998, 1, 1),
    )
    profile = make_profile_with_codes([code])
    user = User(telegram_id=123, profiles=[profile])
    user.verify_profile(profile, "123-456")

    assert profile.is_verified is False
    assert user.pop_event() is None


def test_boosty_profile_cannot_be_verified_if_value_is_wrong():
    code = VerificationCode(
        id=uuid.uuid4(),
        value="123-456",
        valid_until=datetime(2077, 1, 1),
        used_at=None,
        replaced_with=None,
        created_at=datetime(1998, 1, 1),
    )
    profile = make_profile_with_codes([code])
    user = User(telegram_id=123, profiles=[profile])
    user.verify_profile(profile, "456-789")

    assert profile.is_verified is False
    assert user.pop_event() is None


def test_boosty_profile_cannot_be_verified_if_code_was_reissued():
    code = VerificationCode(
        id=uuid.uuid4(),
        value="123-456",
        valid_until=datetime(2077, 1, 1),
        used_at=None,
        replaced_with=uuid.uuid4(),
        created_at=datetime(1998, 1, 1),
    )
    profile = make_profile_with_codes([code])
    user = User(telegram_id=123, profiles=[profile])
    user.verify_profile(profile, "123-456")

    assert profile.is_verified is False
    assert user.pop_event() is None


def test_boosty_profile_can_verify():
    code = VerificationCode(
        id=uuid.uuid4(),
        value="123-456",
        valid_until=datetime(2077, 1, 1),
        used_at=None,
        replaced_with=None,
        created_at=datetime(1998, 1, 1),
    )
    profile = make_profile_with_codes([code])
    user = User(telegram_id=1234, profiles=[profile])
    user.verify_profile(profile, "123-456")

    assert profile.is_verified is True

    event = cast(BoostyProfileVerified, user.pop_event())
    assert type(event) is BoostyProfileVerified
    assert event.user_id == 1234
    assert event.profile_id == 123
    assert event.profile_email == "johndoe@example.com"
    assert event.profile_name == "John Doe"


def test_user_add_profile_produces_events():
    profile = make_profile_with_codes([])
    user = User.new(telegram_id=1234)
    user.add_profile(profile)

    events = user.pop_all_events()
    event = cast(BoostyProfileAdded, events[0])
    assert next(iter(user.profiles)) == profile
    assert type(event) is BoostyProfileAdded
    assert event.user_id == 1234
    assert event.profile_id == 123
    assert event.profile_email == "johndoe@example.com"
    assert event.profile_name == "John Doe"


def test_user_add_profile_adds_user_only_once():
    profile = make_profile_with_codes([])
    user = User.new(telegram_id=1234)
    user.add_profile(profile)
    user.add_profile(profile)

    events = user.pop_all_events()
    assert len(user.profiles) == 1
    assert len(events) == 1
