from aiogram.filters import BaseFilter
from aiogram.types import Message
from database.crud.user_crud import UserCrud
from database.utils.DefaultEnum import UserRole


class IsAdmin(BaseFilter):
    async def __call__(self, msg: Message, session) -> bool:
        user = await UserCrud.get_filtered_by_params(
            session=session,
            telegram_id=str(msg.from_user.id)
        )

        if not user or user[0].role == UserRole.USER:
            return False

        return True
