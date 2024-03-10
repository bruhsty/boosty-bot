from datetime import datetime


class OTPServiceError(Exception):
    pass


class CodeAlreadyUsedError(OTPServiceError):

    def __init__(self, code: str, email: str, telegram_id: int, used_at: datetime) -> None:
        super().__init__(self, f"Code {code} sent to f{email} has already been used at f{used_at}")
        self.code = code
        self.email = email
        self.telegram_id = telegram_id
        self.used_at = used_at


class CodeInvalidError(OTPServiceError):

    def __init__(self, code: str, email: str, telegram_id: int) -> None:
        super().__init__(self, f"Code {code} is invalid")
        self.code = code
        self.email = email
        self.telegram_id = telegram_id


class CodeExpiredError(OTPServiceError):

    def __init__(self, code: str, email: str, telegram_id: int, valid_until: datetime) -> None:
        super().__init__(self, f"Code {code} has expired")
        self.code = code
        self.email = email
        self.telegram_id = telegram_id
        self.valid_until = valid_until
