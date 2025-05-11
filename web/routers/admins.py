from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from database.crud.user_crud import UserCrud
from database.gen_session import get_session
from database.utils.DefaultEnum import UserRole

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/admins", response_class=HTMLResponse)
async def manage_admins(
        request: Request,
        session: AsyncSession = Depends(get_session)
):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse(url="/")

    if (await UserCrud.get_user_role(session=session, telegram_id=user_id)
            not in [UserRole.ADMIN, UserRole.HADMIN]):
        return RedirectResponse(url="/")

    admins = await UserCrud.get_all_admins_and_hadmins(session=session)
    admins = [{
        'telegram_id': str(admin.telegram_id),
        'fullname': admin.full_name,
        'role': admin.role.value
    } for admin in admins]

    status = request.query_params.get("status")

    return templates.TemplateResponse("admins.html", {
        "request": request,
        "admins": admins,
        "roles": list(UserRole),
        "status": status
    })


@router.post("/admins/add_admin")
async def add_admin(
        request: Request,
        telegram_id: str = Form(...),
        fullname: str = Form(...),
        role: UserRole = Form(...),
        session: AsyncSession = Depends(get_session)
):
    current_telegram_id = request.cookies.get("user_id")

    if not current_telegram_id:
        return RedirectResponse(url='/')

    if await UserCrud.get_user_role(session, current_telegram_id) != UserRole.HADMIN:
        return RedirectResponse(url="/admins?status=forbidden", status_code=303)

    if current_telegram_id == telegram_id:
        return RedirectResponse(url="/admins?status=selfedit", status_code=303)

    try:
        user = await UserCrud.get_filtered_by_params(session=session, telegram_id=str(telegram_id))

        if user:
            await UserCrud.update(
                session=session,
                record_id=user[0].id,
                role=role
            )
        else:
            await UserCrud.create(
                session=session,
                telegram_id=str(telegram_id),
                full_name=fullname,
                role=role
            )

        return RedirectResponse(url="/admins?status=success", status_code=303)
    except Exception:
        return RedirectResponse(url="/admins?status=error", status_code=303)


@router.post("/admins/delete_admin")
async def delete_admin(
        request: Request,
        target_telegram_id: str = Form(...),
        session: AsyncSession = Depends(get_session)
):
    current_telegram_id = request.cookies.get("user_id")

    if not current_telegram_id:
        return RedirectResponse(url='/')

    if await UserCrud.get_user_role(session, current_telegram_id) != UserRole.HADMIN:
        return RedirectResponse(url="/admins?status=forbidden", status_code=303)

    if current_telegram_id == target_telegram_id:
        return RedirectResponse(url="/admins?status=selfedit", status_code=303)

    try:
        await UserCrud.update_by_telegram_id(
            session=session,
            telegram_id=str(target_telegram_id),
            role=UserRole.USER
        )

        return RedirectResponse(url="/admins?status=deleted", status_code=303)
    except Exception:
        return RedirectResponse(url="/admins?status=error", status_code=303)
