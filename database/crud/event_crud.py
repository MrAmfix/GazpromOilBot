import uuid
from typing import List, Tuple

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from database.crud.base.factory import BaseCrudFactory
from database.models.models import Event, Stage, UserStage, User
from database.schemas.system_schemas import EventCreate, EventUpdate, EventGet, UserGet


class EventCrud(
    BaseCrudFactory(
        model=Event,
        create_schema=EventCreate,
        update_schema=EventUpdate,
        get_schema=EventGet
    )
):
    @staticmethod
    async def get_event_participation(session: AsyncSession, event_id: uuid.UUID) -> Tuple[int, int]:
        first_stage_query = select(Stage.id).where(
            Stage.event_id == event_id,
            Stage.event_number == 1
        )
        first_stage_result = await session.execute(first_stage_query)
        first_stage_id = first_stage_result.scalar_one_or_none()

        if not first_stage_id:
            return 0, 0

        last_stage_query = select(Stage.id).where(
            Stage.event_id == event_id
        ).order_by(Stage.event_number.desc()).limit(1)
        last_stage_result = await session.execute(last_stage_query)
        last_stage_id = last_stage_result.scalar_one_or_none()

        started_users_query = select(func.count(func.distinct(UserStage.user_id))).where(
            UserStage.stage_id == first_stage_id
        )
        started_users_result = await session.execute(started_users_query)
        started_users_count = started_users_result.scalar_one()

        finished_users_query = select(func.count(func.distinct(UserStage.user_id))).where(
            UserStage.stage_id == last_stage_id,
            UserStage.ended_at.is_not(None)
        )
        finished_users_result = await session.execute(finished_users_query)
        finished_users_count = finished_users_result.scalar_one()

        return started_users_count, finished_users_count

    @staticmethod
    async def get_users_started_event(session: AsyncSession, event_id: uuid.UUID) -> List[UserGet]:
        # Найдем первую стадию ивента (event_number=1)
        first_stage_query = select(Stage.id).where(
            Stage.event_id == event_id,
            Stage.event_number == 1
        )
        first_stage_result = await session.execute(first_stage_query)
        first_stage_id = first_stage_result.scalar_one_or_none()

        if not first_stage_id:
            return []

        users_query = select(User).distinct().join(
            UserStage, User.id == UserStage.user_id
        ).where(
            UserStage.stage_id == first_stage_id
        )

        result = await session.execute(users_query)
        users = result.scalars().all()

        return [UserGet.model_validate(user) for user in users]
