import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from database.crud.base.factory import BaseCrudFactory
from database.models.models import Stage
from database.schemas.system_schemas import StageCreate, StageUpdate, StageGet


class StageCrud(
    BaseCrudFactory(
        model=Stage,
        create_schema=StageCreate,
        update_schema=StageUpdate,
        get_schema=StageGet
    )
):
    @staticmethod
    async def get_by_event_id_and_number(
            session: AsyncSession,
            event_id: uuid.UUID,
            number: int
    ) -> Optional[StageGet]:
        result = await StageCrud.get_filtered_by_params(
            session=session,
            event_id=event_id,
            event_number=number
        )

        return result[0] if result else None
