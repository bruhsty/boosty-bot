import uuid
from datetime import datetime, timezone
from typing import cast

import pytest
from user.domain.events import EmailVerified, VerificationCodeIssued
from user.domain.models import Email, InvalidCodeError, User, VerificationCode


def new_user() -> User:
    return User(telegram_id=123)


def make_email_with_codes(codes: list[VerificationCode]) -> Email:
    return Email(
        email="johndoe@example.com",
        verification_codes=codes,
    )


def make_verified_profile() -> Email:
    return make_email_with_codes(
        [
            VerificationCode(
                id=uuid.uuid4(),
                value="123-456",
                valid_until=datetime(2077, 1, 1, tzinfo=timezone.utc),
                used_at=None,
                replaced_with=None,
                replaced_with_id=None,
                created_at=datetime(1998, 1, 1, tzinfo=timezone.utc),
            )
        ]
    )


def test_email_is_not_verified_if_no_codes_issued():
    email = make_email_with_codes([])
    assert email.is_verified is False


def test_email_is_not_verified_if_code_is_not_used():
    code = VerificationCode(
        id=uuid.uuid4(),
        value="123-456",
        valid_until=datetime(2077, 1, 1, tzinfo=timezone.utc),
        used_at=None,
        replaced_with=None,
        replaced_with_id=None,
        created_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
    )

    email = make_email_with_codes([code])

    assert email.is_verified is False


def test_email_if_code_used():
    code = VerificationCode(
        id=uuid.uuid4(),
        value="123-456",
        valid_until=datetime(2077, 1, 1, tzinfo=timezone.utc),
        used_at=datetime(2024, 1, 2, tzinfo=timezone.utc),
        replaced_with=None,
        replaced_with_id=None,
        created_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
    )
    email = make_email_with_codes([code])

    assert email.is_verified is True


def test_email_cannot_be_verified_if_code_were_not_issued():
    email = make_email_with_codes([])
    user = User.make(telegram_id=123, emails=[email])
    with pytest.raises(InvalidCodeError):
        user.verify_email(email.email, "123-456")

    assert email.is_verified is False
    assert user.pop_event() is None


def test_email_cannot_be_verified_if_code_expired():
    code = VerificationCode(
        id=uuid.uuid4(),
        value="123-456",
        valid_until=datetime(1999, 1, 1, tzinfo=timezone.utc),
        used_at=None,
        replaced_with=None,
        replaced_with_id=None,
        created_at=datetime(1998, 1, 1, tzinfo=timezone.utc),
    )
    email = make_email_with_codes([code])
    user = User.make(telegram_id=123, emails=[email])
    with pytest.raises(InvalidCodeError):
        user.verify_email(email.email, "123-456")

    assert email.is_verified is False
    assert user.pop_event() is None


def test_email_cannot_be_verified_if_value_is_wrong():
    code = VerificationCode(
        id=uuid.uuid4(),
        value="123-456",
        valid_until=datetime(2077, 1, 1, tzinfo=timezone.utc),
        used_at=None,
        replaced_with=None,
        replaced_with_id=None,
        created_at=datetime(1998, 1, 1, tzinfo=timezone.utc),
    )
    email = make_email_with_codes([code])
    user = User.make(telegram_id=123, emails=[email])
    with pytest.raises(InvalidCodeError):
        user.verify_email(email.email, "456-789")

    assert email.is_verified is False
    assert user.pop_event() is None


def test_email_cannot_be_verified_if_code_was_reissued():
    code = VerificationCode(
        id=uuid.uuid4(),
        value="123-456",
        valid_until=datetime(2077, 1, 1, tzinfo=timezone.utc),
        used_at=None,
        replaced_with=None,
        replaced_with_id=uuid.uuid4(),
        created_at=datetime(1998, 1, 1, tzinfo=timezone.utc),
    )
    email = make_email_with_codes([code])
    user = User.make(telegram_id=123, emails=[email])
    with pytest.raises(InvalidCodeError):
        user.verify_email(email.email, "123-456")

    assert email.is_verified is False
    assert user.pop_event() is None


def test_email_can_verify_email():
    code = VerificationCode(
        id=uuid.uuid4(),
        value="123-456",
        valid_until=datetime(2077, 1, 1, tzinfo=timezone.utc),
        used_at=None,
        replaced_with_id=None,
        replaced_with=None,
        created_at=datetime(1998, 1, 1, tzinfo=timezone.utc),
    )
    email = make_email_with_codes([code])
    user = User.make(telegram_id=1234, emails=[email])
    user.verify_email(email.email, "123-456")

    assert email.is_verified is True

    event = cast(EmailVerified, user.pop_event())
    assert type(event) is EmailVerified
    assert event.user_id == 1234
    assert event.code_id == code.id
    assert event.email == "johndoe@example.com"


def test_user_email_verification_produces_events():
    User.CODE_GENERATOR = staticmethod(lambda: "123-456")
    user = User(telegram_id=1234)
    user.add_email("johndoe@example.com")

    event = user.pop_event()
    event = cast(VerificationCodeIssued, event)
    assert type(event) is VerificationCodeIssued
    assert event.user_id == 1234
    assert event.email == "johndoe@example.com"
    assert event.code_valid_until - event.time == User.CODE_TTL
    assert event.code == "123-456"
    code_id = event.code_id

    user.verify_email("johndoe@example.com", "123-456")
    event = user.pop_event()
    event = cast(EmailVerified, event)
    assert type(event) is EmailVerified
    assert event.user_id == 1234
    assert event.email == "johndoe@example.com"
    assert event.code_id == code_id


def test_user_add_email_adds_user_only_once():
    user = User(telegram_id=1234)
    user.add_email("johndoe@example.com")
    user.add_email("johndoe@example.com")

    events = user.pop_all_events()
    assert len(user._emails) == 1
    assert len(events) == 1
