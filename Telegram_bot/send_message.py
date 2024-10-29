import requests
from connection import bot_token


class TelegramSendMessage:

    def __init__(self, bot_token: str = bot_token):
        self.bot_token = bot_token

    def send_text_message(self, message_text, chat_id=None):
        print("[INFO] Запуск функции send_message.send_text_message")
        if chat_id is not None:
            self.tg_group_id = chat_id
        else:
            print("Введите chat_id")

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": self.tg_group_id,
            "text": message_text
        }
        response = requests.post(url, data=payload)
        print(f"[INFO] response = {response}")


if __name__ == '__main__':
    tg = TelegramSendMessage()
    text = "TEST"
    id = 503034116
    tg.send_text_message(text, id)
