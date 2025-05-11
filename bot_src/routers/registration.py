from aiogram import Router, F
from aiogram.enums import ContentType, ParseMode
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from bot_src.utils.filters import IsAdmin
from bot_src.utils.keyboards import share_number_keyboard, RemoveKeyboard, start_event_keyboard
from bot_src.utils.states import RegistrationState
from database.crud.event_crud import EventCrud
from database.crud.onboarding_crud import OnboardingCrud
from database.crud.user_crud import UserCrud
from database.utils.emv2 import emv2


reg_rt = Router()


@reg_rt.message(Command('start'), StateFilter(None))
async def start(msg: Message, state: FSMContext, session: AsyncSession):
    onboarding = await OnboardingCrud.get_active_onboarding(session=session)
    start_param = msg.text.strip().split(maxsplit=1)[1] if len(msg.text.strip().split()) > 1 else None

    if await UserCrud.get_filtered_by_params(session=session, telegram_id=str(msg.from_user.id)):
        await msg.answer(onboarding.start_message_authorized)
        if start_param and start_param.startswith("nameid"):
            event_name_id = start_param.replace("nameid", "", 1)

            event = await EventCrud.get_filtered_by_params(
                session=session,
                named_id=event_name_id
            )
            if not event:
                await msg.answer('Событие не найдено')
            else:
                await msg.answer(f'Событие: {event[0].name}', reply_markup=start_event_keyboard(event_name_id))
    else:
        await UserCrud.create(session=session, telegram_id=str(msg.from_user.id))
        await msg.answer(onboarding.start_message_unauthorized)
        await msg.answer(onboarding.phone_request, reply_markup=share_number_keyboard())
        if start_param and start_param.startswith("nameid"):
            await state.update_data(event_param=start_param)
        await state.set_state(RegistrationState.phone_request)


@reg_rt.message(StateFilter(RegistrationState.phone_request))
async def get_phone(msg: Message, state: FSMContext, session: AsyncSession):
    onboarding = await OnboardingCrud.get_active_onboarding(session=session)

    if msg.content_type != ContentType.CONTACT:
        await msg.answer(onboarding.invalid_phone)
        return

    if msg.contact.user_id != msg.from_user.id:
        await msg.answer(onboarding.invalid_phone)
        return

    contact = msg.contact.phone_number
    if contact[0] != '+':
        contact = '+' + contact

    await UserCrud.update_by_telegram_id(
        session=session,
        telegram_id=msg.from_user.id,
        phone=contact
    )

    await msg.answer(onboarding.fullname_request, reply_markup=RemoveKeyboard)
    await state.set_state(RegistrationState.fullname_request)


@reg_rt.message(StateFilter(RegistrationState.fullname_request))
async def get_fullname(msg: Message, state: FSMContext, session: AsyncSession):
    onboarding = await OnboardingCrud.get_active_onboarding(session=session)

    if msg.content_type != ContentType.TEXT or not msg.text or msg.text.startswith('/'):
        await msg.answer(onboarding.invalid_fullname)
        return

    await UserCrud.update_by_telegram_id(
        session=session,
        telegram_id=msg.from_user.id,
        full_name=msg.text.strip()
    )

    await msg.answer(onboarding.email_request)
    await state.set_state(RegistrationState.email_request)


@reg_rt.message(StateFilter(RegistrationState.email_request))
async def get_email(msg: Message, state: FSMContext, session: AsyncSession):
    onboarding = await OnboardingCrud.get_active_onboarding(session=session)

    if msg.content_type != ContentType.TEXT:
        await msg.answer(onboarding.invalid_email)
        return

    try:
        await UserCrud.update_by_telegram_id(
            session=session,
            telegram_id=msg.from_user.id,
            email=msg.text.strip()
        )

        await msg.answer(onboarding.speciality_request)
        await state.set_state(RegistrationState.speciality_request)
    except IntegrityError as _ie:
        await msg.answer(onboarding.invalid_email)


@reg_rt.message(StateFilter(RegistrationState.speciality_request))
async def get_speciality(msg: Message, state: FSMContext, session: AsyncSession):
    onboarding = await OnboardingCrud.get_active_onboarding(session=session)

    if msg.content_type != ContentType.TEXT or not msg.text or msg.text.startswith('/'):
        await msg.answer(onboarding.invalid_speciality)
        return

    await UserCrud.update_by_telegram_id(
        session=session,
        telegram_id=msg.from_user.id,
        speciality=msg.text.strip()
    )

    await msg.answer(onboarding.success_registration)

    data = await state.get_data()
    event_param = data.get("event_param")

    await state.clear()

    if event_param and event_param.startswith("nameid"):
        event_name_id = event_param.replace("nameid", "", 1)

        event = await EventCrud.get_filtered_by_params(
            session=session,
            named_id=event_name_id
        )
        if not event:
            await msg.answer('Событие не найдено')
        else:
            await msg.answer(f'Событие: {event[0].name}', reply_markup=start_event_keyboard(event_name_id))


@reg_rt.message(StateFilter(None), F.sticker, IsAdmin())
async def get_sticker_id(msg: Message, session: AsyncSession):
    sticker_id = msg.sticker.file_id
    await msg.answer(f'{emv2("Стикер ID:")} `{sticker_id}`', parse_mode=ParseMode.MARKDOWN_V2)
