import uuid
import os
import qrcode
from fastapi import APIRouter, Request, Form, UploadFile, Depends
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from database.gen_session import get_session
from database.utils.DefaultEnum import UserRole
from database.crud.user_crud import UserCrud
from database.crud.event_crud import EventCrud
from database.crud.stage_crud import StageCrud
from database.utils.link_for_qr import generate_link_for_qr
from database.config import BOT_USERNAME

router = APIRouter()
templates = Jinja2Templates(directory="web/templates")
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
ATTACH_DIR = os.path.join(BASE_DIR, "attachs")


@router.get("/events")
async def list_events(request: Request, session: AsyncSession = Depends(get_session)):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse("/")

    role = await UserCrud.get_user_role(session=session, telegram_id=user_id)
    if role not in [UserRole.ADMIN, UserRole.HADMIN]:
        return RedirectResponse("/")

    events = await EventCrud.get_all(session=session)
    status = request.query_params.get("status")
    return templates.TemplateResponse("events.html", {
        "request": request,
        "events": events,
        "bot_username": BOT_USERNAME,
        "status": status
    })


@router.post("/events/add")
async def add_event(
    named_id: str = Form(...),
    name: str = Form(...),
    start_message: str = Form(...),
    end_message: str = Form(...),
    start_sticker: str = Form(None),
    end_sticker: str = Form(None),
    session: AsyncSession = Depends(get_session)
):
    if await EventCrud.get_filtered_by_params(
        session=session,
        named_id=named_id
    ):
        return RedirectResponse("/events?status=exists", status_code=303)

    try:
        await EventCrud.create(
            session=session,
            named_id=named_id,
            name=name,
            start_message=start_message,
            end_message=end_message,
            start_sticker=start_sticker,
            end_sticker=end_sticker
        )
        return RedirectResponse("/events?status=created", status_code=303)
    except Exception:
        return RedirectResponse("/events?status=notadded", status_code=303)


@router.post("/events/delete")
async def delete_event(event_id: str = Form(...), session: AsyncSession = Depends(get_session)):
    try:
        await EventCrud.delete(session=session, record_id=event_id)
        return RedirectResponse("/events?status=deleted", status_code=303)
    except Exception:
        return RedirectResponse("/events?status=used", status_code=303)


@router.get("/events/{event_id}/qr")
async def get_qr(event_id: str, session: AsyncSession = Depends(get_session)):
    event = await EventCrud.get_by_id(session=session, record_id=uuid.UUID(event_id))

    path = os.path.join(ATTACH_DIR, "qr_codes", f"{event.named_id}.png")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path):
        qr_url = generate_link_for_qr(event.named_id)
        img = qrcode.make(qr_url)
        img.save(path)
    return FileResponse(path, media_type='image/png', filename=f"{event.named_id}.png")


@router.get("/events/{event_id}")
async def event_detail(request: Request, event_id: str, session: AsyncSession = Depends(get_session)):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse("/")

    role = await UserCrud.get_user_role(session=session, telegram_id=user_id)
    if role not in [UserRole.ADMIN, UserRole.HADMIN]:
        return RedirectResponse("/")

    event = await EventCrud.get_by_id(session=session, record_id=event_id)
    stages = await StageCrud.get_filtered_by_params(session=session, event_id=event_id)
    status = request.query_params.get("status")

    return templates.TemplateResponse("event_detail.html", {
        "request": request,
        "event": event,
        "stages": stages,
        "status": status,
        "bot_username": BOT_USERNAME
    })


@router.post("/events/{event_id}/update")
async def update_event(
    event_id: str,
    name: str = Form(...),
    start_message: str = Form(...),
    end_message: str = Form(...),
    start_sticker: str = Form(None),
    end_sticker: str = Form(None),
    session: AsyncSession = Depends(get_session)
):
    await EventCrud.update(
        session=session,
        record_id=event_id,
        name=name,
        start_message=start_message,
        end_message=end_message,
        start_sticker=start_sticker,
        end_sticker=end_sticker
    )
    return RedirectResponse(f"/events/{event_id}?status=updated", status_code=303)


@router.post("/events/{event_id}/stages/add")
async def add_stage(
    event_id: str,
    event_number: int = Form(...),
    start_message: str = Form(...),
    mid_message: str = Form(...),
    end_message: str = Form(...),
    expected_answer: str = Form(None),
    answer_options: str = Form(None),
    start_attach: UploadFile = Form(None),
    end_attach: UploadFile = Form(None),
    end_sticker: str = Form(None),
    session: AsyncSession = Depends(get_session)
):
    def save_file(file: UploadFile, suffix: str):
        if not file:
            return None
        ext = file.filename.split(".")[-1]
        filename = f"{uuid.uuid4()}_{suffix}.{ext}"
        filepath = os.path.join(ATTACH_DIR, filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "wb") as f:
            f.write(file.file.read())
        return f"attachs/{filename}"

    start_path = save_file(start_attach, "start")
    end_path = save_file(end_attach, "end")

    await StageCrud.create(
        session=session,
        event_id=event_id,
        event_number=event_number,
        start_message=start_message,
        mid_message=mid_message,
        end_message=end_message,
        expected_answer=expected_answer,
        answer_options=answer_options,
        start_attach=start_path,
        end_attach=end_path,
        end_sticker=end_sticker
    )
    return RedirectResponse(f"/events/{event_id}?status=stage_added", status_code=303)


@router.post("/stages/{stage_id}/delete")
async def delete_stage(stage_id: str, event_id: str = Form(...), session: AsyncSession = Depends(get_session)):
    try:
        await StageCrud.delete(session=session, record_id=stage_id)
        return RedirectResponse(f"/events/{event_id}?status=stage_deleted", status_code=303)
    except Exception:
        return RedirectResponse(f"/events/{event_id}?status=stage_used", status_code=303)
