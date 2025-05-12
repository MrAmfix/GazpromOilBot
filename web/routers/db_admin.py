from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from database.gen_session import get_session
from database.crud.user_crud import UserCrud
from database.utils.DefaultEnum import UserRole
from database.models.models import Base

router = APIRouter()
templates = Jinja2Templates(directory="web/templates")


@router.get("/db")
async def db_admin_page(request: Request, session: AsyncSession = Depends(get_session)):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse("/")

    role = await UserCrud.get_user_role(session=session, telegram_id=user_id)
    if role != UserRole.HADMIN:
        return RedirectResponse("/dashboard")

    table_names = list(Base.metadata.tables.keys())
    return templates.TemplateResponse("db_admin.html", {
        "request": request,
        "tables": table_names
    })


@router.get("/db/{table_name}")
async def view_table(table_name: str, request: Request, session: AsyncSession = Depends(get_session)):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse("/")

    role = await UserCrud.get_user_role(session=session, telegram_id=user_id)
    if role != UserRole.HADMIN:
        return RedirectResponse("/dashboard")

    table = Base.metadata.tables.get(table_name)
    if table is None:
        raise HTTPException(status_code=404, detail="Таблица не найдена")

    result = await session.execute(select(table))
    rows = result.fetchall()

    return templates.TemplateResponse("db_table.html", {
        "request": request,
        "table_name": table_name,
        "columns": table.columns.keys(),
        "rows": rows
    })


@router.post("/db/{table_name}/delete")
async def delete_record(
    table_name: str,
    primary_key: str = Form(...),
    request: Request = None,
    session: AsyncSession = Depends(get_session)
):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse("/")

    role = await UserCrud.get_user_role(session=session, telegram_id=user_id)
    if role != UserRole.HADMIN:
        return RedirectResponse("/dashboard")

    table = Base.metadata.tables.get(table_name)
    if table is None:
        raise HTTPException(status_code=404)

    pk_column = list(table.primary_key.columns)[0]

    await session.execute(delete(table).where(pk_column == primary_key))
    await session.commit()

    return RedirectResponse(f"/db/{table_name}", status_code=303)
