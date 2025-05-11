import uuid
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram import Bot
from database.gen_session import get_session
from database.config import BOT_TOKEN
from database.utils.DefaultEnum import UserRole
from database.crud.user_crud import UserCrud
from database.crud.event_crud import EventCrud
from database.crud.newsletter_crud import NewsletterCrud
from database.crud.newsletter_log_crud import NewsletterLogCrud


router = APIRouter()
templates = Jinja2Templates(directory="web/templates")
bot = Bot(token=BOT_TOKEN)


@router.get("/message")
async def message_page(request: Request, session: AsyncSession = Depends(get_session)):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse("/")

    role = await UserCrud.get_user_role(session=session, telegram_id=user_id)
    if role not in [UserRole.ADMIN, UserRole.HADMIN]:
        return RedirectResponse("/")

    events = await EventCrud.get_all(session=session)
    status = request.query_params.get("status")
    delivered = request.query_params.get("delivered")
    failed = request.query_params.get("failed")

    return templates.TemplateResponse("message.html", {
        "request": request,
        "events": events,
        "status": status,
        "delivered": delivered,
        "failed": failed
    })


@router.post("/message/send_all")
async def send_to_all_users(
    message: str = Form(...),
    session: AsyncSession = Depends(get_session)
):
    users = await UserCrud.get_filtered_by_params(session=session, role=UserRole.USER)

    newsletter = await NewsletterCrud.create(session=session, message=message)
    delivered, failed = 0, 0

    for user in users:
        try:
            await bot.send_message(chat_id=int(user.telegram_id), text=message)
            delivered += 1
            await NewsletterLogCrud.create(session=session, telegram_id=str(user.telegram_id), status=True, newsletter_id=newsletter.id)
        except Exception:
            failed += 1
            await NewsletterLogCrud.create(session=session, telegram_id=str(user.telegram_id), status=False, newsletter_id=newsletter.id)

    return RedirectResponse(url=f"/message?status=sent_all&delivered={delivered}&failed={failed}", status_code=303)


@router.post("/message/send_event")
async def send_to_event_users(
    named_id: str = Form(...),
    message: str = Form(...),
    session: AsyncSession = Depends(get_session)
):
    event = await EventCrud.get_filtered_by_params(session=session, named_id=named_id)
    if not event:
        return RedirectResponse("/message?status=event_not_found", status_code=303)

    users = await UserCrud.get_filtered_by_params(
        session=session,
        role=UserRole.USER,
        cur_event_id=event[0].id
    )

    newsletter = await NewsletterCrud.create(session=session, message=message)
    delivered, failed = 0, 0

    for user in users:
        try:
            await bot.send_message(chat_id=int(user.telegram_id), text=message)
            delivered += 1
            await NewsletterLogCrud.create(session=session, telegram_id=user.telegram_id, status=True, newsletter_id=newsletter.id)
        except Exception:
            failed += 1
            await NewsletterLogCrud.create(session=session, telegram_id=user.telegram_id, status=False, newsletter_id=newsletter.id)

    return RedirectResponse(url=f"/message?status=sent_event&delivered={delivered}&failed={failed}", status_code=303)