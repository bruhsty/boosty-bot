__all__ = ["CodeStorageError", "CodeNotFoundError"]


class CodeStorageError(Exception):
    pass


class CodeNotFoundError(CodeStorageError):

    def __init__(self, code_id: int, message: str) -> None:
        super().__init__(message, code_id)
        self.code_id = code_id
        self.message = message
