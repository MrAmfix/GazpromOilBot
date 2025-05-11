import io
import xlsxwriter
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import StreamingResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from database.gen_session import get_session
from database.utils.DefaultEnum import UserRole
from database.crud.user_crud import UserCrud
from database.crud.event_crud import EventCrud

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/analytics")
async def analytics_page(request: Request, session: AsyncSession = Depends(get_session)):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse("/")

    role = await UserCrud.get_user_role(session=session, telegram_id=user_id)
    if role not in [UserRole.ADMIN, UserRole.HADMIN]:
        return RedirectResponse("/")

    events = await EventCrud.get_all(session=session)
    return templates.TemplateResponse("analytics.html", {
        "request": request,
        "events": events
    })


@router.post("/analytics/event")
async def event_analytics(named_id: str = Form(...), session: AsyncSession = Depends(get_session)):
    event = await EventCrud.get_filtered_by_params(session=session, named_id=named_id)
    if not event:
        return RedirectResponse("/analytics?status=event_not_found")
    event = event[0]

    started, finished = await EventCrud.get_event_participation(session=session, event_id=event.id)
    users = await EventCrud.get_users_started_event(session=session, event_id=event.id)

    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    sheet = workbook.add_worksheet("Event Stats")

    sheet.write("A1", f"Ивент: {event.name} ({event.named_id})")
    sheet.write("A2", f"Начали: {started}")
    sheet.write("A3", f"Завершили: {finished}")
    sheet.write("A5", "Telegram ID")
    sheet.write("B5", "ФИО")

    for idx, user in enumerate(users, start=6):
        sheet.write(f"A{idx}", user.telegram_id)
        sheet.write(f"B{idx}", user.full_name)

    workbook.close()
    output.seek(0)
    return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={
        "Content-Disposition": f"attachment; filename=analytics_{named_id}.xlsx"
    })


@router.get("/analytics/users")
async def all_users_analytics(session: AsyncSession = Depends(get_session)):
    users = await UserCrud.get_filtered_by_params(session=session, role=UserRole.USER)

    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    sheet = workbook.add_worksheet("Users")

    sheet.write_row("A1", ["Telegram ID", "ФИО", "Роль", "Email", "Телефон", "Специальность", "Ивентов начато", "Ивентов завершено"])

    for idx, user in enumerate(users, start=2):
        started, finished = await UserCrud.get_user_events_stats(session=session, user_id=user.id)
        sheet.write_row(f"A{idx}", [
            user.telegram_id,
            user.full_name,
            user.role.value,
            user.email,
            user.phone,
            user.speciality,
            started,
            finished
        ])

    workbook.close()
    output.seek(0)
    return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={
        "Content-Disposition": "attachment; filename=all_users_analytics.xlsx"
    })