from typing import Optional

from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, \
    InlineKeyboardButton

from database.schemas.system_schemas import StageGet

RemoveKeyboard = ReplyKeyboardRemove()


def share_number_keyboard() -> ReplyKeyboardMarkup:
    share_phone_button = KeyboardButton(text='📞 Поделиться номером телефона', request_contact=True)
    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[share_phone_button]])


def start_event_keyboard(name_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(
        text='Начать', callback_data=f'start_event{name_id}'
    )]])


def answer_options_keyboard(stage: StageGet) -> Optional[InlineKeyboardMarkup]:
    if not stage.answer_options:
        return None

    options = stage.answer_options.strip().split(';')
    if len(options) > 6 or any(len(opt) > 15 for opt in options):
        return None

    buttons = []

    i = 0
    for option in options:
        if i % 2 == 0:
            buttons.append([])
        i += 1
        buttons[-1].append(InlineKeyboardButton(
            text=option, callback_data=f'ev_ans{option}'
        ))

    return InlineKeyboardMarkup(inline_keyboard=buttons)
