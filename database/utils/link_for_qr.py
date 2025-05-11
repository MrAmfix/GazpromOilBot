from database.config import BOT_USERNAME


def generate_link_for_qr(named_id: str) -> str:
    return f'https://t.me/{BOT_USERNAME}?start=nameid{named_id}'
