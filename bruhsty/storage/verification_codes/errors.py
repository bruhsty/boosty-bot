__all__ = ["CodeStorageError", "CodeNotFoundError", "FieldIsNotEditable"]


class CodeStorageError(Exception):
    pass


class CodeNotFoundError(CodeStorageError):

    def __init__(self, code_id: int, message: str) -> None:
        super().__init__(message, code_id)
        self.code_id = code_id
        self.message = message


class FieldIsNotEditable(CodeStorageError):

    def __init__(self, field_name: str, message: str) -> None:
        super().__init__(message, field_name)
        self.field_name = field_name
