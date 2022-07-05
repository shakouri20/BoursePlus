from datetime import datetime, timedelta


class expirableMessage():
    def __init__(self, message, timeout) -> None:
        self.startTime = datetime.now()
        self.message = message
        self.timeout = timeout

    def is_expired(self):
        if datetime.now()- self.startTime > timedelta(seconds=self.timeout):
            return True
        else:
            return False

    def get_message(self):
        return self.message