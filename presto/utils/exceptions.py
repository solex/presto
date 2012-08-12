class ValidationError(Exception):
    def __init__(self, messages):
        self.messages = messages


class AlreadyExist(ValidationError):
    pass


class PrestoCfgException(Exception):
    pass
