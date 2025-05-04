from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton

RemoveKeyboard = ReplyKeyboardRemove()


def share_number_keyboard() -> ReplyKeyboardMarkup:
    share_phone_button = KeyboardButton(text='📞 Поделиться номером телефона', request_contact=True)
    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[share_phone_button]])
