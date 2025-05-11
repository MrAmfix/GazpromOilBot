from fastapi import APIRouter, Request, Response, Depends, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
import hmac
import hashlib
from database.crud.user_crud import UserCrud
from database.utils.DefaultEnum import UserRole
from database.gen_session import get_session
from database.config import BOT_TOKEN

router = APIRouter()

BOT_TOKEN_HASH = hashlib.sha256(BOT_TOKEN.encode()).digest()


def verify_telegram_auth(data: dict) -> bool:
    auth_data = data.copy()
    hash_to_check = auth_data.pop('hash')
    data_check_string = '\n'.join(f'{k}={auth_data[k]}' for k in sorted(auth_data))
    hmac_hash = hmac.new(BOT_TOKEN_HASH, data_check_string.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(hmac_hash, hash_to_check)


@router.get("/auth/telegram")
async def auth_telegram(request: Request, session: AsyncSession = Depends(get_session)):
    params = dict(request.query_params)
    if not verify_telegram_auth(params):
        return HTMLResponse("Неверная авторизация.", status_code=400)

    telegram_id = int(params.get("id"))
    username = params.get("username", "Пользователь")

    user = await UserCrud.get_filtered_by_params(session=session, telegram_id=str(telegram_id))
    if not user or user[0].role not in (UserRole.ADMIN, UserRole.HADMIN):
        return HTMLResponse("Доступ запрещен.", status_code=403)

    response = RedirectResponse(url="/dashboard")
    response.set_cookie(key="user_id", value=str(telegram_id))
    response.set_cookie(key="username", value=username)
    return response
