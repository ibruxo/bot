from services.messengers.telegram_like import TelegramLikeAdapter


class BaleAdapter(TelegramLikeAdapter):
    platform = "bale"

    def __init__(self, token: str, api_base_url: str = "https://tapi.bale.ai"):
        super().__init__(token, api_base_url)
