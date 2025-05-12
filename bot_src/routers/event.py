import mimetypes
from pathlib import Path
from aiogram import Router, F
from aiogram.enums import ContentType
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession
from bot_src.utils.download_file import download_file
from bot_src.utils.keyboards import answer_options_keyboard
from bot_src.utils.states import InEvent
from database.config import WEB_PORT
from database.crud.event_crud import EventCrud
from database.crud.stage_crud import StageCrud
from database.crud.user_crud import UserCrud
from database.crud.user_stage_crud import UserStageCrud
from database.schemas.system_schemas import StageGet, UserStageCreate
from database.utils.moscow_datetime import datetime_now_moscow


event_rt = Router()
PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()


@event_rt.callback_query(F.data.startswith("start_event"), StateFilter(None))
async def start_event_callback(call: CallbackQuery, state: FSMContext, session: AsyncSession):
    name_id = call.data.removeprefix("start_event")
    await call.message.edit_reply_markup(reply_markup=None)

    event = (await EventCrud.get_filtered_by_params(
        session=session,
        named_id=name_id
    ))[0]

    stage = await StageCrud.get_by_event_id_and_number(
        session=session,
        event_id=event.id,
        number=1
    )

    if not stage:
        await call.message.answer('Упс, похоже в этом событии нет заданий')
        return

    user = await UserCrud.update_by_telegram_id(
        session=session,
        telegram_id=call.from_user.id,
        cur_event_id=event.id
    )

    await UserStageCrud.create(
        session=session,
        user_id=user.id,
        stage_id=stage.id
    )

    try:
        if event.start_sticker:
            await call.message.answer_sticker(event.start_sticker)
    except Exception:
        pass
    await call.message.answer(event.start_message)

    await state.update_data(event_id=event.id)
    await state.update_data(number=2)
    await state.set_state(InEvent.in_event)

    await send_start_message(stage, call.message)


@event_rt.callback_query(F.data.startswith("ev_ans"), InEvent.in_event)
async def handle_inline_answer(call: CallbackQuery, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    event_id = data.get("event_id")
    number = int(data.get("number"))
    user_answer = call.data.removeprefix("ev_ans")

    prev_stage = await StageCrud.get_by_event_id_and_number(
        session=session,
        event_id=event_id,
        number=number - 1
    )

    if prev_stage.expected_answer and prev_stage.expected_answer.strip() != user_answer:
        await call.answer(prev_stage.mid_message, show_alert=True)
        return

    await send_end_message(prev_stage, call.message)
    await UserStageCrud.update_by_stage_id_and_telegram_id(
        session=session,
        stage_id=prev_stage.id,
        telegram_id=call.from_user.id,
        ended_at=datetime_now_moscow()
    )

    stage = await StageCrud.get_by_event_id_and_number(
        session=session,
        event_id=event_id,
        number=number
    )

    if not stage:
        event = await EventCrud.get_by_id(session=session, record_id=event_id)
        try:
            if event.end_sticker:
                await call.message.answer_sticker(event.end_sticker)
        except Exception:
            pass
        await call.message.answer(event.end_message)
        await UserCrud.update_by_telegram_id(
            session=session,
            telegram_id=call.from_user.id,
            clean_kwargs=False,
            cur_event_id=None
        )
        await state.clear()
    else:
        await send_start_message(stage, call.message)
        await UserStageCrud.create_with_telegram_id(
            session=session,
            stage_id=stage.id,
            telegram_id=call.from_user.id
        )
        await state.update_data(number=number + 1)



@event_rt.message(InEvent.in_event)
async def handle_text_answer(msg: Message, state: FSMContext, session: AsyncSession):
    if msg.content_type != ContentType.TEXT:
        await msg.answer('Ответьте пожалуйста текстом')
        return

    data = await state.get_data()
    event_id = data.get("event_id")
    number = int(data.get("number"))
    user_answer = msg.text

    prev_stage = await StageCrud.get_by_event_id_and_number(
        session=session,
        event_id=event_id,
        number=number - 1
    )

    if prev_stage.expected_answer and prev_stage.expected_answer.strip() != user_answer.strip():
        await msg.answer(prev_stage.mid_message)
        return

    await send_end_message(prev_stage, msg)
    await UserStageCrud.update_by_stage_id_and_telegram_id(
        session=session,
        stage_id=prev_stage.id,
        telegram_id=msg.from_user.id,
        ended_at=datetime_now_moscow()
    )

    stage = await StageCrud.get_by_event_id_and_number(
        session=session,
        event_id=event_id,
        number=number
    )

    if not stage:
        event = await EventCrud.get_by_id(session=session, record_id=event_id)
        try:
            if event.end_sticker:
                await msg.answer_sticker(event.end_sticker)
        except Exception:
            pass
        await msg.answer(event.end_message)
        await UserCrud.update_by_telegram_id(
            session=session,
            telegram_id=msg.from_user.id,
            clean_kwargs=False,
            cur_event_id=None
        )
        await state.clear()
    else:
        await send_start_message(stage, msg)
        await UserStageCrud.create_with_telegram_id(
            session=session,
            stage_id=stage.id,
            telegram_id=msg.from_user.id
        )
        await state.update_data(number=number + 1)


async def send_start_message(stage: StageGet, msg: Message):
    try:
        if stage.start_sticker:
            await msg.answer_sticker(stage.start_sticker)
    except Exception:
        pass

    filename = (stage.start_attach or "").replace("attachs/", "")
    file_url = f"http://web_app:{WEB_PORT}/file/{filename}"
    file = await download_file(file_url, "start")

    if not file:
        await msg.answer(stage.start_message, reply_markup=answer_options_keyboard(stage))
        return

    mime_type, _ = mimetypes.guess_type(filename)
    try:
        if mime_type and mime_type.startswith("image/"):
            await msg.answer_photo(
                photo=file,
                caption=stage.start_message,
                reply_markup=answer_options_keyboard(stage)
            )
        else:
            await msg.answer_document(
                document=file,
                caption=stage.start_message,
                reply_markup=answer_options_keyboard(stage)
            )
    except Exception:
        await msg.answer(stage.start_message, reply_markup=answer_options_keyboard(stage))



async def send_end_message(stage: StageGet, msg: Message):
    try:
        await msg.edit_reply_markup(reply_markup=None)
    except Exception:
        pass

    try:
        if stage.end_sticker:
            await msg.answer_sticker(stage.end_sticker)
    except Exception:
        pass

    filename = (stage.end_attach or "").replace("attachs/", "")
    file_url = f"http://web_app:{WEB_PORT}/file/{filename}"
    file = await download_file(file_url, "end")

    if not file:
        await msg.answer(stage.end_message)
        return

    mime_type, _ = mimetypes.guess_type(filename)
    try:
        if mime_type and mime_type.startswith("image/"):
            await msg.answer_photo(
                photo=file,
                caption=stage.end_message
            )
        else:
            await msg.answer_document(
                document=file,
                caption=stage.end_message
            )
    except Exception:
        await msg.answer(stage.end_message)
