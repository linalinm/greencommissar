class VerificationException(Exception):
    def __init__(self, details: str, *args):
        self._details = details
        super().__init__(*args)

    def getDetails(self):
        return self._details


class NotTicketChannelException(VerificationException):
    def __init__(self, details, *args):
        super().__init__(details, *args)
