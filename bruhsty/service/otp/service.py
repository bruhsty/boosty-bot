import struct
from typing import Callable
from bruhsty.service import proto
from bruhsty.storage.verification_codes.models import Code


class OTPService:
    def __init__(
            self,
            random: Callable[[int], bytes],
            codes_store: proto.CodeStorage,
    ) -> None:
        self.random = random
        self.codes_store = codes_store

    async def generate_otp(self, telegram_id: int, user_email: str) -> Code:
        otp_bytes = self.random(4)  # создал 6 рандомных байтов
        otp_tuple = struct.unpack("I", otp_bytes)
        otp_str = "".join(otp_tuple)
        short_otp_str = otp_str[:6]
        otp = short_otp_str.rjust(6, '0')
        code = await self.codes_store.add(telegram_id, user_email, otp)
        return code

    async def validate_otp(self, telegram_id: int, user_email: str, otp: str) -> None:
        # TODO: check if code is valid (valid value, wasn't used, is still valid),
        #  if not valid raise appropriate error
        #  mark code as used (set used_at field)
        ...
