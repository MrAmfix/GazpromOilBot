from aiogram import Router
from aiogram.enums import ContentType
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from bot_src.utils.keyboards import share_number_keyboard, RemoveKeyboard
from bot_src.utils.states import RegistrationState
from database.crud.user_crud import UserCrud


urt = Router()


@urt.message(Command('start'), StateFilter(None))
async def start(msg: Message, state: FSMContext, session: AsyncSession):
    if UserCrud.get_filtered_by_params(session=session, telegram_id=str(msg.from_user.id)):
        await msg.answer('Привет, ты уже зарегистрирован 🤝')
    else:
        await UserCrud.create(session=session, telegram_id=str(msg.from_user.id))
        await msg.answer('Привет, давай для начала зарегистрируемся', reply_markup=share_number_keyboard())
        await state.set_state(RegistrationState.phone_request)


@urt.message(lambda msg: msg.content_type == ContentType.CONTACT, StateFilter(RegistrationState.phone_request))
async def get_phone(msg: Message, state: FSMContext, session: AsyncSession):
    contact = msg.contact.phone_number
    if contact[0] != '+':
        contact = '+' + contact

    await UserCrud.update_by_telegram_id(
        session=session,
        telegram_id=msg.from_user.id,
        phone=contact
    )

    await msg.answer('Спасибо, теперь мне необходимо знать твое ФИО', reply_markup=RemoveKeyboard)
    await state.set_state(RegistrationState.fullname_request)


@urt.message(StateFilter(RegistrationState.fullname_request))
async def get_fullname(msg: Message, state: FSMContext, session: AsyncSession):
    fullname = msg.text.strip()

    if not msg.content_type != ContentType.TEXT or fullname or fullname.startswith('/'):
        await msg.answer('Пожалуйста, отправь свое ФИО текстом.')
        return

    await UserCrud.update_by_telegram_id(
        session=session,
        telegram_id=msg.from_user.id,
        full_name=fullname
    )

    await msg.answer('Спасибо, теперь мне нужна ваша электронная почта')
    await state.set_state(RegistrationState.email_request)


@urt.message(StateFilter(RegistrationState.email_request))
async def get_email(msg: Message, state: FSMContext, session: AsyncSession):
    try:
        await UserCrud.update_by_telegram_id(
            session=session,
            telegram_id=msg.from_user.id,
            email=msg.text.strip()
        )

        await msg.answer('Спасибо, осталось узнать только вашу специальность, напишите ее')
        await state.set_state(RegistrationState.speciality_request)
    except IntegrityError as _ie:
        await msg.answer('Некорректный формат, введите пожалуйста почту в формате email@example.com')


@urt.message(StateFilter(RegistrationState.speciality_request))
async def get_speciality(msg: Message, state: FSMContext, session: AsyncSession):
    speciality = msg.text.strip()

    if not msg.content_type != ContentType.TEXT or speciality or speciality.startswith('/'):
        await msg.answer('Пожалуйста, отправь свое специальность текстом.')
        return

    await UserCrud.update_by_telegram_id(
        session=session,
        telegram_id=msg.from_user.id,
        speciality=speciality
    )

    await msg.answer('Спасибо, теперь ты зарегистрирован! Пропиши /help, чтобы узнать больше 🔥')
    await state.clear()
