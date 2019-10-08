from notifiers import get_notifier


class Telegram:
    PROVIDER_NAME = 'telegram'

    def __init__(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id

    def notify(self, message):
        telegram = get_notifier(self.PROVIDER_NAME)

        return telegram.notify(message=message, token=self.token, chat_id=self.chat_id)
