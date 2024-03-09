from typing import Callable
from service import proto


class OTPService:
    def __init__(
            self,
            random: Callable[[int], bytes],
            codes_store: proto.CodeStorage,
    ) -> None:
        self.random = random
        self.codes_store = codes_store

    async def generate_otp(self, telegram_id: int, user_email: str) -> str:
        # TODO: generate one time password from given random source (self.random).
        #  save in provided codes store (self.codes_store)
        #  return generated code
        ...

    async def validate_otp(self, telegram_id: int, user_email: str, otp: str) -> None:
        # TODO: check if code is valid (valid value, wasn't used, is still valid),
        #  if not valid raise appropriate error
        #  mark code as used (set used_at field)
        ...
