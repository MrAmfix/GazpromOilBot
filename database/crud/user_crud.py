import uuid
from typing import Union, List, Optional, Tuple
from sqlalchemy import select, or_, distinct, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from database.crud.base.factory import BaseCrudFactory
from database.models.models import User, Stage, UserStage
from database.schemas.system_schemas import UserCreate, UserUpdate, UserGet
from database.utils.DefaultEnum import UserRole


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

    @staticmethod
    async def get_all_admins_and_hadmins(session: AsyncSession) -> List[UserGet]:
        result = await session.execute(
            select(User).
            where(
                or_(User.role == UserRole.ADMIN, User.role == UserRole.HADMIN)
            )
        )

        return [UserGet.model_validate(user) for user in result.scalars().all()]

    @staticmethod
    async def get_user_role(session: AsyncSession, telegram_id: Union[str, int]) -> Optional[UserRole]:
        user = await UserCrud.get_filtered_by_params(session=session, telegram_id=str(telegram_id))
        return user[0].role if user else None

    @staticmethod
    async def get_user_events_stats(session: AsyncSession, user_id: uuid.UUID) -> Tuple[int, int]:
        first_stages_subquery = select(
            Stage.id.label('stage_id'),
            Stage.event_id
        ).where(
            Stage.event_number == 1
        ).subquery()

        last_stages_subquery = select(
            Stage.id.label('stage_id'),
            Stage.event_id
        ).distinct(Stage.event_id).where(
            Stage.event_id.in_(
                select(distinct(Stage.event_id)).select_from(Stage)
            )
        ).order_by(
            Stage.event_id,
            Stage.event_number.desc()
        ).subquery()

        first_stages = aliased(first_stages_subquery)
        last_stages = aliased(last_stages_subquery)

        started_events_query = select(
            func.count(distinct(first_stages.c.event_id))
        ).select_from(
            UserStage
        ).join(
            first_stages,
            UserStage.stage_id == first_stages.c.stage_id
        ).where(
            UserStage.user_id == user_id
        )

        completed_events_query = select(
            func.count(distinct(last_stages.c.event_id))
        ).select_from(
            UserStage
        ).join(
            last_stages,
            UserStage.stage_id == last_stages.c.stage_id
        ).where(
            UserStage.user_id == user_id,
            UserStage.ended_at.is_not(None)
        )

        started_result = await session.execute(started_events_query)
        started_count = started_result.scalar_one()

        completed_result = await session.execute(completed_events_query)
        completed_count = completed_result.scalar_one()

        return started_count, completed_count
