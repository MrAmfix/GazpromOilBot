import uuid
from typing import Union
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from database.crud.base.factory import BaseCrudFactory
from database.crud.user_crud import UserCrud
from database.models.models import UserStage
from database.schemas.system_schemas import UserStageCreate, UserStageUpdate, UserStageGet


class UserStageCrud(
    BaseCrudFactory(
        model=UserStage,
        create_schema=UserStageCreate,
        update_schema=UserStageUpdate,
        get_schema=UserStageGet
    )
):
    @staticmethod
    async def update_by_stage_id_and_user_id(
            session: AsyncSession,
            stage_id: uuid.UUID,
            user_id: uuid.UUID,
            **kwargs
    ):
        await session.execute(
            update(UserStage)
            .where(UserStage.stage_id == stage_id, UserStage.user_id == user_id)
            .values(**kwargs)
        )
        await session.commit()


    @staticmethod
    async def update_by_stage_id_and_telegram_id(
            session: AsyncSession,
            stage_id: uuid.UUID,
            telegram_id: Union[str, int],
            **kwargs
    ):
        user = await UserCrud.get_filtered_by_params(
            session=session,
            telegram_id=str(telegram_id)
        )

        if not user:
            raise ValueError(f'Пользователя с telegram_id ({telegram_id}) не существует')

        await UserStageCrud.update_by_stage_id_and_user_id(
            session=session,
            stage_id=stage_id,
            user_id=user[0].id,
            **kwargs
        )

    @staticmethod
    async def create_with_telegram_id(
            session: AsyncSession,
            stage_id: uuid.UUID,
            telegram_id: Union[str, int],
            **kwargs
    ):
        user = await UserCrud.get_filtered_by_params(
            session=session,
            telegram_id=str(telegram_id)
        )

        if not user:
            raise ValueError(f'Пользователя с telegram_id ({telegram_id}) не существует')

        await UserStageCrud.create(
            session=session,
            stage_id=stage_id,
            user_id=user[0].id,
            **kwargs
        )
