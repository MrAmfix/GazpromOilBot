from typing import Union
from sqlalchemy.ext.asyncio import AsyncSession
from database.crud.base.factory import BaseCrudFactory
from database.models.models import User
from database.schemas.system_schemas import UserCreate, UserUpdate, UserGet


class UserCrud(
    BaseCrudFactory(
        model=User,
        create_schema=UserCreate,
        update_schema=UserUpdate,
        get_schema=UserGet
    )
):
    @staticmethod
    async def update_by_telegram_id(session: AsyncSession, telegram_id: Union[str, int],
                                    clean_kwargs: bool = True, **kwargs) -> UserGet:
        user = await UserCrud.get_filtered_by_params(session=session, telegram_id=str(telegram_id))
        if not User:
            raise Exception(f'User with telegram_id ({telegram_id}) not found')
        if clean_kwargs:
            return await UserCrud.update(session=session, record_id=user[0].id, **kwargs)
        else:
            return await UserCrud.update_no_clean(session=session, record_id=user[0].id, **kwargs)
