class SQLStorageError(Exception):
    pass


class NoRowAffectedError(SQLStorageError):
    pass
