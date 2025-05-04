from aiogram.fsm.state import StatesGroup, State


class RegistrationState(StatesGroup):
    phone_request = State()
    fullname_request = State()
    email_request = State()
    speciality_request = State()
